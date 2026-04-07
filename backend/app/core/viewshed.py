"""Viewshed computation — casts rays across the user's field of view
and returns all visible terrain hits."""
from __future__ import annotations

from app.core.ray_caster import cast_ray, TerrainHit
from app.config import RAYS_HORIZONTAL, RAYS_VERTICAL, MAX_RANGE_KM


def compute_viewshed(
    lat: float,
    lon: float,
    altitude: float,
    bearing: float,
    pitch: float,
    fov_h: float,
    fov_v: float,
) -> list[TerrainHit]:
    """Cast rays across the user's field of view and return visible terrain hits.

    Args:
        lat, lon: Observer position
        altitude: Observer altitude (meters ASL)
        bearing: Center bearing (degrees from north)
        pitch: Center pitch (degrees, positive = up)
        fov_h: Horizontal field of view (degrees)
        fov_v: Vertical field of view (degrees)

    Returns:
        List of terrain hits visible from the observer.
    """
    hits: list[TerrainHit] = []
    max_range_m = MAX_RANGE_KM * 1000

    # Sample bearings across the horizontal FOV
    h_start = bearing - fov_h / 2
    h_step = fov_h / max(RAYS_HORIZONTAL - 1, 1)

    for i in range(RAYS_HORIZONTAL):
        ray_bearing = (h_start + i * h_step) % 360

        hit = cast_ray(
            observer_lat=lat,
            observer_lon=lon,
            observer_alt=altitude,
            bearing=ray_bearing,
            max_range_m=max_range_m,
        )

        if hit is not None:
            hits.append(hit)

    return hits
