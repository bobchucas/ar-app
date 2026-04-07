"""Ray marching engine for terrain visibility analysis.

Casts rays outward from the observer, sampling DEM elevation at each step,
and accounting for Earth curvature + atmospheric refraction to determine
what terrain features are visible along each line of sight.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from app.core.earth_model import curvature_drop, destination_point
from app.core.dem_loader import sample_elevation


@dataclass
class TerrainHit:
    """A point where a ray hits visible terrain."""
    latitude: float
    longitude: float
    elevation: float      # meters ASL
    distance_m: float     # distance from observer
    bearing: float        # degrees from north
    elevation_angle: float  # degrees, angle from horizontal at observer


def cast_ray(
    observer_lat: float,
    observer_lon: float,
    observer_alt: float,
    bearing: float,
    max_range_m: float = 50_000,
) -> TerrainHit | None:
    """Cast a single ray from the observer along a bearing.

    Steps outward at increasing intervals, sampling DEM elevation.
    Returns the first visible terrain hit, or None if the ray doesn't
    hit anything (e.g., points out to sea or sky).

    Step sizes:
    - 0-2km: 100m steps (nearby detail)
    - 2-10km: 300m steps (mid-range)
    - 10-50km: 700m steps (distant features)
    """
    max_elevation_angle = -90.0  # Track the highest terrain angle seen so far
    best_hit: TerrainHit | None = None

    distance = 100.0  # Start at 100m out
    while distance <= max_range_m:
        # Compute geographic position at this distance
        lat, lon = destination_point(observer_lat, observer_lon, bearing, distance)

        # Sample DEM elevation
        terrain_elev = sample_elevation(lat, lon)
        if terrain_elev is None:
            distance += _step_size(distance)
            continue

        # Account for Earth curvature: terrain appears lower from observer's
        # perspective than its true elevation
        drop = curvature_drop(distance, observer_lat)
        apparent_elev = terrain_elev - drop

        # Elevation angle from observer to this terrain point
        elev_diff = apparent_elev - observer_alt
        angle = math.degrees(math.atan2(elev_diff, distance))

        # This point is visible if its angle is higher than anything closer.
        # This is the key visibility test — closer terrain blocks farther terrain.
        if angle > max_elevation_angle:
            max_elevation_angle = angle
            best_hit = TerrainHit(
                latitude=lat,
                longitude=lon,
                elevation=terrain_elev,
                distance_m=distance,
                bearing=bearing,
                elevation_angle=angle,
            )

        distance += _step_size(distance)

    return best_hit


def _step_size(distance: float) -> float:
    """Variable step size — finer resolution nearby, coarser at distance."""
    if distance < 2000:
        return 100
    elif distance < 10000:
        return 300
    else:
        return 700
