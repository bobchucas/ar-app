"""Quick smoke test for the ray caster.

Run from the backend directory:
    python -m scripts.test_raycaster
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.earth_model import curvature_drop, destination_point
from app.core.dem_loader import sample_elevation


def test_earth_model():
    print("=== Earth Model Tests ===")

    # Curvature drop at various distances
    for dist_km in [1, 5, 10, 20, 50]:
        drop = curvature_drop(dist_km * 1000, lat_deg=55.0)
        print(f"  Curvature drop at {dist_km}km: {drop:.1f}m")

    # Destination point: from Belfast (54.6, -5.93) bearing 180° (south) for 100km
    lat, lon = destination_point(54.6, -5.93, 180, 100_000)
    print(f"  100km south of Belfast: ({lat:.3f}, {lon:.3f})")
    assert 53.5 < lat < 53.8, f"Expected ~53.7, got {lat}"
    print("  OK")


def test_dem_sampling():
    print("\n=== DEM Sampling Tests ===")

    # Try sampling Slieve Donard (Northern Ireland's highest peak)
    # 54.1796, -5.9206, elevation ~850m
    elev = sample_elevation(54.1796, -5.9206)
    if elev is not None:
        print(f"  Slieve Donard elevation: {elev:.0f}m (expected ~850m)")
    else:
        print("  Slieve Donard: No DEM tile available (download tiles first)")

    # Try Snowdon
    elev = sample_elevation(53.0685, -4.0763)
    if elev is not None:
        print(f"  Snowdon elevation: {elev:.0f}m (expected ~1085m)")
    else:
        print("  Snowdon: No DEM tile available")


if __name__ == "__main__":
    test_earth_model()
    test_dem_sampling()
    print("\nAll tests passed.")
