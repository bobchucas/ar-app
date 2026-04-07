from __future__ import annotations
"""Load and sample elevation data from Copernicus DEM GeoTIFF tiles.

Copernicus DEM 30m tiles are named like:
  Copernicus_DSM_COG_10_N54_00_W006_00_DEM.tif
covering 1°x1° each.
"""

import math
from functools import lru_cache
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import rasterio
    from rasterio.transform import rowcol
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

from app.config import DEM_DIR


def _tile_filename(lat: float, lon: float) -> str:
    """Generate the Copernicus DEM tile filename for a given coordinate."""
    lat_int = math.floor(lat)
    lon_int = math.floor(lon)

    lat_prefix = "N" if lat_int >= 0 else "S"
    lon_prefix = "E" if lon_int >= 0 else "W"

    return (
        f"Copernicus_DSM_COG_10_{lat_prefix}{abs(lat_int):02d}_00_"
        f"{lon_prefix}{abs(lon_int):03d}_00_DEM.tif"
    )


@lru_cache(maxsize=16)
def _open_tile(path: str) -> Optional["rasterio.DatasetReader"]:
    """Open a DEM tile, cached to avoid repeated file opens."""
    if not HAS_RASTERIO:
        return None
    tile_path = Path(path)
    if not tile_path.exists():
        return None
    return rasterio.open(tile_path)


def sample_elevation(lat: float, lon: float) -> Optional[float]:
    """Sample DEM elevation at a given lat/lon using bilinear interpolation.

    Returns elevation in meters, or None if the tile is unavailable.
    """
    filename = _tile_filename(lat, lon)
    filepath = str(DEM_DIR / filename)
    dataset = _open_tile(filepath)

    if dataset is None:
        return None

    try:
        # Convert lat/lon to pixel coordinates
        row, col = rowcol(dataset.transform, lon, lat)

        # Read a 2x2 window for bilinear interpolation
        row_int = int(math.floor(row))
        col_int = int(math.floor(col))
        row_frac = row - row_int
        col_frac = col - col_int

        # Ensure we don't go out of bounds
        if (row_int < 0 or row_int >= dataset.height - 1 or
                col_int < 0 or col_int >= dataset.width - 1):
            # Fall back to nearest pixel
            r = max(0, min(int(round(row)), dataset.height - 1))
            c = max(0, min(int(round(col)), dataset.width - 1))
            window = rasterio.windows.Window(c, r, 1, 1)
            data = dataset.read(1, window=window)
            return float(data[0, 0])

        window = rasterio.windows.Window(col_int, row_int, 2, 2)
        data = dataset.read(1, window=window)

        # Bilinear interpolation
        top = data[0, 0] * (1 - col_frac) + data[0, 1] * col_frac
        bottom = data[1, 0] * (1 - col_frac) + data[1, 1] * col_frac
        value = top * (1 - row_frac) + bottom * row_frac

        return float(value)
    except Exception:
        return None


def sample_elevation_batch(coords: list[tuple[float, float]]) -> np.ndarray:
    """Sample elevation for a batch of (lat, lon) pairs.

    Returns numpy array of elevations. Missing values are NaN.
    """
    result = np.full(len(coords), np.nan)
    for i, (lat, lon) in enumerate(coords):
        elev = sample_elevation(lat, lon)
        if elev is not None:
            result[i] = elev
    return result
