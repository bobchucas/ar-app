"""Load OS Open Names and GeoNames data into a SQLite database with R-tree spatial index."""

import csv
import sqlite3
import zipfile
from pathlib import Path

from pyproj import Transformer

from app.config import GAZETTEER_DIR, GAZETTEER_DB

# BNG (EPSG:27700) -> WGS84 (EPSG:4326) transformer
_bng_to_wgs84 = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

# OS Open Names feature types we care about
OS_RELEVANT_TYPES = {
    "populatedPlace", "landform", "hydrography", "transportNetwork",
    "other",
}

# OS Open Names local types we want
OS_RELEVANT_LOCAL_TYPES = {
    "City", "Town", "Village", "Hamlet",
    "Hill Or Mountain", "Valley",
    "Bay", "Lake", "Loch", "Reservoir",
    "Spot Height", "Castle", "Monument",
    "Airport", "Railway Station",
}

# GeoNames feature codes we care about
GEONAMES_RELEVANT_CODES = {
    "PPL", "PPLA", "PPLA2", "PPLA3", "PPLC",  # populated places
    "MT", "MTS", "PK", "HLL", "HLLS", "RDG",   # mountains/hills
    "LK", "LKS", "RSV",                          # lakes
    "ISL", "ISLS",                                # islands
    "CSTL", "MNMT", "TOWR",                       # landmarks
    "AIRP",                                        # airports
}


def init_db() -> sqlite3.Connection:
    """Create the gazetteer database and tables."""
    conn = sqlite3.connect(str(GAZETTEER_DB))
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            elevation REAL,
            source TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS features_rtree USING rtree(
            id,
            min_lat, max_lat,
            min_lon, max_lon
        );

        CREATE INDEX IF NOT EXISTS idx_features_name ON features(name);
    """)
    return conn


OS_OPEN_NAMES_HEADER = [
    "ID", "NAMES_URI", "NAME1", "NAME1_LANG", "NAME2", "NAME2_LANG",
    "TYPE", "LOCAL_TYPE", "GEOMETRY_X", "GEOMETRY_Y",
    "MOST_DETAIL_VIEW_RES", "LEAST_DETAIL_VIEW_RES",
    "MBR_XMIN", "MBR_YMIN", "MBR_XMAX", "MBR_YMAX",
    "POSTCODE_DISTRICT", "POSTCODE_DISTRICT_URI",
    "POPULATED_PLACE", "POPULATED_PLACE_URI", "POPULATED_PLACE_TYPE",
    "DISTRICT_BOROUGH", "DISTRICT_BOROUGH_URI", "DISTRICT_BOROUGH_TYPE",
    "COUNTY_UNITARY", "COUNTY_UNITARY_URI", "COUNTY_UNITARY_TYPE",
    "REGION", "REGION_URI", "COUNTRY", "COUNTRY_URI",
    "RELATED_SPATIAL_OBJECT", "SAME_AS_DBPEDIA", "SAME_AS_GEONAMES",
]


def load_os_open_names(conn: sqlite3.Connection, csv_path: Path) -> int:
    """Load OS Open Names CSV into the database.

    Handles both formats:
    - Raw download CSVs (no header, BNG eastings/northings) — converts to WGS84
    - Pre-converted CSVs with GEOMETRY_X_WGS84 / GEOMETRY_Y_WGS84 columns
    """
    count = 0
    cursor = conn.cursor()

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        # Peek at first line to detect if there's a header row
        first_line = f.readline()
        f.seek(0)

        has_header = "LOCAL_TYPE" in first_line
        if has_header:
            reader = csv.DictReader(f)
        else:
            reader = csv.DictReader(f, fieldnames=OS_OPEN_NAMES_HEADER)

        has_wgs84 = has_header and "GEOMETRY_X_WGS84" in first_line

        for row in reader:
            local_type = row.get("LOCAL_TYPE", "")
            if local_type not in OS_RELEVANT_LOCAL_TYPES:
                continue

            name = row.get("NAME1", "").strip()
            if not name:
                continue

            try:
                if has_wgs84:
                    lat = float(row["GEOMETRY_Y_WGS84"])
                    lon = float(row["GEOMETRY_X_WGS84"])
                else:
                    easting = float(row["GEOMETRY_X"])
                    northing = float(row["GEOMETRY_Y"])
                    lon, lat = _bng_to_wgs84.transform(easting, northing)
            except (KeyError, ValueError):
                continue

            feature_type = _map_os_type(local_type)

            cursor.execute(
                "INSERT INTO features (name, type, latitude, longitude, elevation, source) "
                "VALUES (?, ?, ?, ?, NULL, 'os_open_names')",
                (name, feature_type, lat, lon),
            )
            fid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO features_rtree (id, min_lat, max_lat, min_lon, max_lon) "
                "VALUES (?, ?, ?, ?, ?)",
                (fid, lat, lat, lon, lon),
            )
            count += 1

    conn.commit()
    return count


def load_geonames(conn: sqlite3.Connection, tsv_path: Path) -> int:
    """Load GeoNames allCountries.txt (tab-separated) into the database.

    Columns: geonameid, name, asciiname, alternatenames, latitude, longitude,
    feature_class, feature_code, country_code, ...
    """
    count = 0
    cursor = conn.cursor()

    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 9:
                continue

            feature_code = parts[7]
            if feature_code not in GEONAMES_RELEVANT_CODES:
                continue

            name = parts[1].strip()
            if not name:
                continue

            try:
                lat = float(parts[4])
                lon = float(parts[5])
            except ValueError:
                continue

            elevation = None
            if len(parts) > 15 and parts[15]:
                try:
                    elevation = float(parts[15])
                except ValueError:
                    pass
            if elevation is None and len(parts) > 16 and parts[16]:
                try:
                    elevation = float(parts[16])
                except ValueError:
                    pass

            feature_type = _map_geonames_code(feature_code)

            cursor.execute(
                "INSERT INTO features (name, type, latitude, longitude, elevation, source) "
                "VALUES (?, ?, ?, ?, ?, 'geonames')",
                (name, feature_type, lat, lon, elevation),
            )
            fid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO features_rtree (id, min_lat, max_lat, min_lon, max_lon) "
                "VALUES (?, ?, ?, ?, ?)",
                (fid, lat, lat, lon, lon),
            )
            count += 1

            if count % 100000 == 0:
                conn.commit()

    conn.commit()
    return count


def _map_os_type(local_type: str) -> str:
    mapping = {
        "City": "city", "Town": "town", "Village": "village", "Hamlet": "hamlet",
        "Hill Or Mountain": "peak", "Valley": "valley",
        "Bay": "bay", "Lake": "lake", "Loch": "lake", "Reservoir": "reservoir",
        "Castle": "landmark", "Monument": "landmark",
        "Airport": "airport", "Railway Station": "station",
    }
    return mapping.get(local_type, "other")


def _map_geonames_code(code: str) -> str:
    mapping = {
        "PPL": "town", "PPLA": "city", "PPLA2": "city", "PPLA3": "town", "PPLC": "city",
        "MT": "peak", "MTS": "peak", "PK": "peak", "HLL": "hill", "HLLS": "hill", "RDG": "ridge",
        "LK": "lake", "LKS": "lake", "RSV": "reservoir",
        "ISL": "island", "ISLS": "island",
        "CSTL": "landmark", "MNMT": "landmark", "TOWR": "landmark",
        "AIRP": "airport",
    }
    return mapping.get(code, "other")
