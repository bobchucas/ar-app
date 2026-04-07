from pathlib import Path

# Base directory for the backend
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DEM_DIR = BASE_DIR / "data" / "dem"
GAZETTEER_DIR = BASE_DIR / "data" / "gazetteer"
GAZETTEER_DB = GAZETTEER_DIR / "gazetteer.db"

# Ray-casting parameters
MAX_RANGE_KM = 50          # Maximum ray distance
EARTH_RADIUS_M = 6371000   # Mean Earth radius
REFRACTION_K = 0.13        # Standard atmospheric refraction coefficient

# Ray sampling
RAYS_HORIZONTAL = 60       # Number of horizontal rays across FOV
RAYS_VERTICAL = 20         # Number of vertical rays across FOV
