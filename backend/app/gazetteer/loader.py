"""Load OS Open Names and GeoNames data into a SQLite database with R-tree spatial index."""

import csv
import sqlite3
import zipfile
from pathlib import Path

from app.config import GAZETTEER_DIR, GAZETTEER_DB

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


def load_os_open_names(conn: sqlite3.Connection, csv_path: Path) -> int:
    """Load OS Open Names CSV into the database.

    OS Open Names CSV columns (header row):
    ID, NAMES_URI, NAME1, NAME1_LANG, NAME2, NAME2_LANG,
    TYPE, LOCAL_TYPE, GEOMETRY_X, GEOMETRY_Y, ...
    (GEOMETRY_X/Y are British National Grid eastings/northings — we need lat/lon)

    Actually, the download includes a "DATA" column format with
    SAME_AS_DBPEDIA, POPULATED_PLACE, etc.

    For the prototype, we use the CSV version which has
    lat/lon in WGS84 if downloaded as the GeoPackage or
    we convert from BNG.

    Note: This loader expects pre-converted CSV with lat/lon columns.
    Use the download script to handle conversion.
    """
    count = 0
    cursor = conn.cursor()

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            local_type = row.get("LOCAL_TYPE", "")
            if local_type not in OS_RELEVANT_LOCAL_TYPES:
                continue

            name = row.get("NAME1", "").strip()
            if not name:
                continue

            try:
                lat = float(row["GEOMETRY_Y_WGS84"])
                lon = float(row["GEOMETRY_X_WGS84"])
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
