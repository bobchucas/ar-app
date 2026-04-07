"""Earth curvature and atmospheric refraction calculations."""
from __future__ import annotations

import math
from app.config import EARTH_RADIUS_M, REFRACTION_K


def earth_radius_at_latitude(lat_deg: float) -> float:
    """WGS84 Earth radius at a given latitude (meters).

    The Earth is an oblate spheroid: ~6378km at equator, ~6357km at poles.
    """
    lat = math.radians(lat_deg)
    a = 6378137.0       # equatorial radius
    b = 6356752.314245  # polar radius
    cos_lat = math.cos(lat)
    sin_lat = math.sin(lat)
    num = (a**2 * cos_lat) ** 2 + (b**2 * sin_lat) ** 2
    den = (a * cos_lat) ** 2 + (b * sin_lat) ** 2
    return math.sqrt(num / den)


def curvature_drop(distance_m: float, lat_deg: float = 50.0) -> float:
    """Height 'hidden' by Earth's curvature at a given distance.

    Accounts for standard atmospheric refraction (k=0.13), which bends
    light downward, making distant objects appear slightly higher.

    Returns drop in meters.
    """
    R = earth_radius_at_latitude(lat_deg)
    return (distance_m ** 2) / (2 * R) * (1 - REFRACTION_K)


def destination_point(lat_deg: float, lon_deg: float,
                      bearing_deg: float, distance_m: float) -> tuple[float, float]:
    """Compute destination lat/lon given start point, bearing, and distance.

    Uses the spherical law of cosines (accurate enough for <100km).
    """
    R = EARTH_RADIUS_M
    lat1 = math.radians(lat_deg)
    lon1 = math.radians(lon_deg)
    brg = math.radians(bearing_deg)
    d_R = distance_m / R

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d_R)
        + math.cos(lat1) * math.sin(d_R) * math.cos(brg)
    )
    lon2 = lon1 + math.atan2(
        math.sin(brg) * math.sin(d_R) * math.cos(lat1),
        math.cos(d_R) - math.sin(lat1) * math.sin(lat2)
    )

    return math.degrees(lat2), math.degrees(lon2)
