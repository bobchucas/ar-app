"""Download Copernicus DEM 30m tiles from AWS Open Data.

Copernicus DEM tiles are hosted at:
  s3://copernicus-dem-30m/Copernicus_DSM_COG_10_N54_00_W006_00_DEM/
    Copernicus_DSM_COG_10_N54_00_W006_00_DEM.tif

Usage:
    python -m scripts.download_dem --lat-min 54 --lat-max 56 --lon-min -8 --lon-max -5

This will download all tiles covering Northern Ireland / north of Ireland.
"""

import argparse
import subprocess
from pathlib import Path

DEM_DIR = Path(__file__).resolve().parent.parent / "data" / "dem"
BASE_URL = "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com"


def tile_url(lat: int, lon: int) -> str:
    lat_prefix = "N" if lat >= 0 else "S"
    lon_prefix = "E" if lon >= 0 else "W"
    name = f"Copernicus_DSM_COG_10_{lat_prefix}{abs(lat):02d}_00_{lon_prefix}{abs(lon):03d}_00_DEM"
    return f"{BASE_URL}/{name}/{name}.tif"


def download_tiles(lat_min: int, lat_max: int, lon_min: int, lon_max: int):
    DEM_DIR.mkdir(parents=True, exist_ok=True)

    for lat in range(lat_min, lat_max):
        for lon in range(lon_min, lon_max):
            url = tile_url(lat, lon)
            filename = url.split("/")[-1]
            filepath = DEM_DIR / filename

            if filepath.exists():
                print(f"  Already exists: {filename}")
                continue

            print(f"  Downloading: {filename}")
            result = subprocess.run(
                ["curl", "-sS", "-f", "-o", str(filepath), url],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                print(f"  WARNING: Failed to download {filename} (may not exist for ocean tiles)")
                filepath.unlink(missing_ok=True)
            else:
                size_mb = filepath.stat().st_size / (1024 * 1024)
                print(f"  OK: {filename} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Copernicus DEM tiles")
    parser.add_argument("--lat-min", type=int, default=54, help="Min latitude (integer)")
    parser.add_argument("--lat-max", type=int, default=56, help="Max latitude (exclusive)")
    parser.add_argument("--lon-min", type=int, default=-8, help="Min longitude (integer)")
    parser.add_argument("--lon-max", type=int, default=-5, help="Max longitude (exclusive)")
    args = parser.parse_args()

    print(f"Downloading DEM tiles for lat [{args.lat_min}, {args.lat_max}) lon [{args.lon_min}, {args.lon_max})")
    download_tiles(args.lat_min, args.lat_max, args.lon_min, args.lon_max)
    print("Done.")
