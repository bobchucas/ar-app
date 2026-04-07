"""Query the gazetteer database for named features near terrain hits."""
from __future__ import annotations

import math
import sqlite3
from typing import Optional

from app.config import GAZETTEER_DB
from app.core.ray_caster import TerrainHit
from app.models.response import Feature

# Cache the database connection
_conn: Optional[sqlite3.Connection] = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(GAZETTEER_DB))
        _conn.row_factory = sqlite3.Row
    return _conn


def find_features_near_point(
    lat: float, lon: float, radius_km: float = 2.0
) -> list[dict]:
    """Find named features within radius_km of a point.

    Uses the R-tree spatial index for fast lookup.
    """
    conn = _get_conn()

    # Approximate degree offset for the search radius
    lat_delta = radius_km / 111.0  # ~111km per degree latitude
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    rows = conn.execute(
        """
        SELECT f.name, f.type, f.latitude, f.longitude, f.elevation
        FROM features f
        JOIN features_rtree r ON f.id = r.id
        WHERE r.min_lat >= ? AND r.max_lat <= ?
          AND r.min_lon >= ? AND r.max_lon <= ?
        """,
        (lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta),
    ).fetchall()

    return [dict(row) for row in rows]


def find_features_near_hits(hits: list[TerrainHit]) -> list[Feature]:
    """For each terrain hit, find nearby named features from the gazetteer.

    Groups nearby hits to avoid redundant queries.
    """
    features: list[Feature] = []

    # Cluster hits by rounding to ~1km grid to avoid querying the same area twice
    queried_cells: set[tuple[int, int]] = set()

    for hit in hits:
        # Grid cell: ~1km resolution
        cell = (round(hit.latitude * 100), round(hit.longitude * 100))
        if cell in queried_cells:
            continue
        queried_cells.add(cell)

        # Search within 1.5km of the hit
        nearby = find_features_near_point(hit.latitude, hit.longitude, radius_km=1.5)

        for feat in nearby:
            # Compute actual bearing and distance from the original observer
            # (approximated here using the hit's bearing and distance)
            features.append(Feature.create(
                name=feat["name"],
                type=feat["type"],
                distance_km=hit.distance_m / 1000,
                bearing=hit.bearing,
                elevation=feat.get("elevation") or hit.elevation,
                latitude=feat["latitude"],
                longitude=feat["longitude"],
            ))

    return features
