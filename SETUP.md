# LookUp — AR "What Am I Looking At?" App

## Overview

An iOS AR app that identifies what you're looking at through your camera — distant landmarks, towns, mountains, and planes in the sky. Points your phone at something and it tells you what it is.

## Architecture

```
┌─────────────────────┐         HTTP POST /identify        ┌──────────────────────┐
│     iOS App          │ ──────────────────────────────────▶│   Python Backend     │
│  (iPhone, Swift)     │◀────────────────────────────────── │   (FastAPI)          │
│                      │         JSON response              │                      │
│  • ARKit camera      │                                    │  • DEM ray-casting   │
│  • CoreLocation GPS  │                                    │  • Gazetteer lookup  │
│  • Compass heading   │                                    │  • Earth curvature   │
│  • Label overlay     │                                    │    correction        │
│  • OpenSky planes    │                                    │                      │
└─────────────────────┘                                    └──────────────────────┘
        │                                                          │
        │ Direct API call                                          │ Reads from disk
        ▼                                                          ▼
┌─────────────────────┐                                    ┌──────────────────────┐
│  OpenSky Network    │                                    │  Local Data          │
│  (free ADS-B API)   │                                    │  • Copernicus DEM    │
│  Real-time aircraft │                                    │    30m GeoTIFF tiles │
│  positions          │                                    │  • Gazetteer SQLite  │
└─────────────────────┘                                    │    (OS Open Names +  │
                                                           │     GeoNames)        │
                                                           └──────────────────────┘
```

### How it works

1. iPhone gets GPS position, compass bearing, and camera pitch angle
2. Sends these to the backend: "I'm at (54.6, -5.93), looking bearing 215° at pitch 3°"
3. Backend casts 60 rays across the field of view, marching outward up to 50km
4. At each step, it samples terrain elevation from DEM tiles and checks if the terrain is visible (not blocked by closer hills)
5. Visible terrain hits are matched against a gazetteer database of named places
6. Backend returns: "You can see Slieve Donard (12km, bearing 218°), Newcastle (15km, bearing 210°)"
7. iPhone projects these onto the camera feed as floating AR labels
8. Separately, the iPhone polls OpenSky for nearby aircraft and overlays flight info

## Project Structure

```
AR-app/
├── ios/                          ← iOS app (runs on iPhone)
│   ├── project.yml               ← XcodeGen spec (generates .xcodeproj)
│   ├── LookUp/
│   │   ├── App/
│   │   │   ├── LookUpApp.swift        ← App entry point
│   │   │   └── AppState.swift         ← Central ObservableObject (location, bearing, features)
│   │   ├── Views/
│   │   │   ├── ContentView.swift      ← Main view: AR camera + labels + debug overlay
│   │   │   ├── LabelOverlayView.swift ← Projects world coords to screen, renders labels per frame
│   │   │   ├── LandmarkLabelView.swift← Styled label for a geographic feature
│   │   │   ├── FlightInfoCard.swift   ← Styled card for aircraft
│   │   │   └── DebugOverlayView.swift ← Live sensor readout (GPS, compass, pitch)
│   │   ├── AR/
│   │   │   ├── ARCameraView.swift     ← UIViewRepresentable wrapping ARView
│   │   │   │                            Uses gravityAndHeading alignment:
│   │   │   │                            +X=East, +Y=Up, -Z=North
│   │   │   └── ScreenProjection.swift ← (bearing, distance, elevation) → ARKit world pos → screen point
│   │   ├── Services/
│   │   │   ├── LocationService.swift  ← CLLocationManager wrapper (GPS + heading)
│   │   │   ├── IdentifyAPIClient.swift← POST /identify to backend
│   │   │   ├── OpenSkyClient.swift    ← Fetches aircraft from OpenSky API, maps ICAO→airline names
│   │   │   └── BearingMatcher.swift   ← Filters aircraft to those within user's field of view
│   │   ├── Models/
│   │   │   ├── LandmarkFeature.swift  ← Codable model for a named place
│   │   │   ├── Aircraft.swift         ← Aircraft with computed bearing/distance from observer
│   │   │   ├── IdentifyRequest.swift  ← Request body for /identify
│   │   │   └── IdentifyResponse.swift ← Response from /identify
│   │   └── Utilities/
│   │       ├── GeoMath.swift          ← Haversine bearing/distance, angle wraparound
│   │       ├── CompassSmoother.swift  ← Circular rolling average (handles 359°→0° wraparound)
│   │       ├── Debouncer.swift        ← Debounce API calls on sensor changes
│   │       └── Constants.swift        ← Backend URL, thresholds, FOV values
│   └── LookUpTests/
│       ├── GeoMathTests.swift
│       ├── CompassSmootherTests.swift
│       └── BearingMatcherTests.swift
│
├── backend/                      ← Python backend (runs on server/NUC)
│   ├── requirements.txt          ← fastapi, uvicorn, rasterio, pyproj, numpy, scipy, pydantic
│   ├── app/
│   │   ├── main.py               ← FastAPI app with /identify and /health endpoints
│   │   ├── config.py             ← Paths, ray-casting params (max range, ray count, refraction)
│   │   ├── api/
│   │   │   └── identify.py       ← POST /identify handler: viewshed → gazetteer → response
│   │   ├── core/
│   │   │   ├── earth_model.py    ← WGS84 radius at latitude, curvature drop with refraction
│   │   │   │                       correction (k=0.13), destination point calculation
│   │   │   ├── dem_loader.py     ← Opens Copernicus GeoTIFF tiles via rasterio
│   │   │   │                       LRU-cached file handles, bilinear interpolation
│   │   │   │                       Tile naming: Copernicus_DSM_COG_10_N54_00_W006_00_DEM.tif
│   │   │   ├── ray_caster.py     ← Core algorithm: marches a ray outward from observer
│   │   │   │                       Step sizes: 100m (0-2km), 300m (2-10km), 700m (10-50km)
│   │   │   │                       At each step: sample DEM, subtract curvature drop,
│   │   │   │                       compute elevation angle, track max angle (visibility test)
│   │   │   └── viewshed.py       ← Casts 60 horizontal rays across the FOV, returns hits
│   │   ├── gazetteer/
│   │   │   ├── loader.py         ← Loads OS Open Names CSV + GeoNames TSV into SQLite
│   │   │   │                       Filters to relevant types (cities, peaks, lakes, landmarks)
│   │   │   │                       Creates R-tree spatial index for fast radius queries
│   │   │   └── lookup.py         ← Queries gazetteer for named features near terrain hits
│   │   │                           Clusters hits to ~1km grid to avoid redundant queries
│   │   └── models/
│   │       ├── request.py        ← Pydantic model: lat, lon, alt, bearing, pitch, fov
│   │       └── response.py       ← Pydantic model: list of Feature (name, type, distance, bearing)
│   ├── scripts/
│   │   ├── download_dem.py       ← Downloads Copernicus 30m tiles from AWS for a bounding box
│   │   ├── load_gazetteer.py     ← Loads gazetteer CSVs into SQLite DB
│   │   └── test_raycaster.py     ← Smoke test: earth model math + DEM sampling
│   ├── data/
│   │   ├── dem/                  ← Copernicus GeoTIFF tiles (~50MB each, ~200MB for all UK)
│   │   └── gazetteer/            ← OS Open Names CSVs, GeoNames TSV, gazetteer.db
│   └── tests/
│
└── .gitignore                    ← Excludes .xcodeproj, .venv, DEM tiles, gazetteer data
```

## Backend Setup (for the NUC)

### Prerequisites
- Python 3.9+
- ~500MB disk space (DEM tiles + gazetteer)

### Install

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Download DEM tiles

Downloads Copernicus 30m elevation tiles. For full UK/Ireland coverage:

```bash
python -m scripts.download_dem --lat-min 49 --lat-max 61 --lon-min -11 --lon-max 2
```

For just Northern Ireland (quick test):

```bash
python -m scripts.download_dem --lat-min 54 --lat-max 56 --lon-min -8 --lon-max -5
```

Each tile is ~50MB, covers 1°×1°. Ocean-only tiles will fail to download (expected).

### Download gazetteer data

1. **OS Open Names** (UK/NI place names — 2.6M features):
   - Go to https://osdatahub.os.uk/downloads/open/OpenNames
   - Download CSV format
   - Extract to `backend/data/gazetteer/`

2. **GeoNames** (global fallback — optional):
   - Download https://download.geonames.org/export/dump/GB.zip
   - Extract `GB.txt` to `backend/data/gazetteer/`

3. **Load into SQLite:**
   ```bash
   python -m scripts.load_gazetteer
   ```
   Creates `backend/data/gazetteer/gazetteer.db` with R-tree spatial index.

### Run the server

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Verify it's working

```bash
# Health check
curl http://localhost:8000/health

# Smoke test (will return empty features if no DEM/gazetteer loaded)
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"latitude": 54.6, "longitude": -5.93, "altitude": 50, "bearing": 180, "pitch": 2, "fov_horizontal": 69, "fov_vertical": 54}'
```

## iOS App Setup

### Prerequisites
- Xcode 16+
- Physical iPhone (ARKit doesn't work in simulator)
- XcodeGen (`brew install xcodegen`)

### Build

```bash
cd ios
xcodegen generate
open LookUp.xcodeproj
```

In Xcode:
1. Set your development team in Signing & Capabilities
2. Update `Constants.swift` → `backendBaseURL` to your NUC's IP (currently `http://192.168.4.93:8000`)
3. Build and run on your iPhone

### Key config in Constants.swift

| Constant | Value | What it does |
|----------|-------|--------------|
| `backendBaseURL` | `http://192.168.4.93:8000` | NUC backend address — **change this to your NUC's IP** |
| `openSkyPollInterval` | 10s | How often to fetch aircraft positions |
| `bearingChangeThreshold` | 5° | Min bearing change before re-querying backend |
| `pitchChangeThreshold` | 3° | Min pitch change before re-querying backend |
| `apiDebounceDelay` | 0.3s | Wait for sensor stability before firing request |
| `defaultFovHorizontal` | 69° | iPhone wide lens horizontal FOV |

## Key Technical Details

### Ray-casting algorithm (ray_caster.py)
- Casts 60 rays across the horizontal FOV
- Each ray marches outward in steps (100m→300m→700m) up to 50km
- At each step: samples DEM elevation, subtracts Earth curvature drop, computes elevation angle
- Curvature correction: `drop = d²/(2R) × (1 - 0.13)` where 0.13 is atmospheric refraction
- At 10km the curvature drop is ~6.8m, at 50km it's ~171m — can't be ignored
- A terrain point is visible if its elevation angle exceeds all closer terrain

### ARKit coordinate system
- `gravityAndHeading` world alignment: +X=East, +Y=Up, -Z=North
- Labels placed at capped AR distance (500m max) to avoid float precision issues
- Screen projection via `arView.project()` each frame

### Compass smoothing
- Raw magnetometer heading is noisy (5-15° error near buildings/metal)
- Circular rolling average using sin/cos decomposition handles 359°→0° wraparound
- Window of 10 samples

## What's Not Yet Built (Step 12: Polish)

- Label jitter smoothing (EMA on screen positions)
- Label overlap prevention (greedy algorithm by distance)
- Response caching (5min for landmarks, 30s for aircraft)
- Graceful error states (no GPS, no compass, API timeout)
- Offline fallback with cached responses

## Network Requirements

The iPhone must be able to reach the backend server. Options:
- **Same WiFi**: phone and NUC on the same local network ✓
- **VPN**: use Tailscale/WireGuard to reach the NUC from mobile data
- **Cloud**: deploy backend to a VPS for anywhere access
