"""Load gazetteer data into SQLite.

Usage:
    # First, download OS Open Names from:
    #   https://osdatahub.os.uk/downloads/open/OpenNames
    # Download the CSV format, extract to backend/data/gazetteer/

    # Optionally download GeoNames:
    #   https://download.geonames.org/export/dump/GB.zip (UK only, ~5MB)
    #   Extract GB.txt to backend/data/gazetteer/

    python -m scripts.load_gazetteer
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import GAZETTEER_DIR
from app.gazetteer.loader import init_db, load_os_open_names, load_geonames


def main():
    print("Initialising database...")
    conn = init_db()

    # Load OS Open Names CSVs
    # The download extracts to multiple CSV files in subdirectories
    os_csvs = list(GAZETTEER_DIR.glob("**/*_OpenNames.csv")) + \
              list(GAZETTEER_DIR.glob("**/OS_Open_Names*.csv")) + \
              list(GAZETTEER_DIR.glob("**/*.csv"))

    # Deduplicate
    os_csvs = list(set(os_csvs))

    if os_csvs:
        total = 0
        for csv_path in sorted(os_csvs):
            if csv_path.name == "gazetteer.db":
                continue
            print(f"  Loading OS Open Names: {csv_path.name}...")
            count = load_os_open_names(conn, csv_path)
            total += count
            print(f"    -> {count} features")
        print(f"  OS Open Names total: {total} features")
    else:
        print("  No OS Open Names CSV files found in", GAZETTEER_DIR)
        print("  Download from: https://osdatahub.os.uk/downloads/open/OpenNames")

    # Load GeoNames
    geonames_file = GAZETTEER_DIR / "GB.txt"
    if geonames_file.exists():
        print(f"  Loading GeoNames: {geonames_file.name}...")
        count = load_geonames(conn, geonames_file)
        print(f"    -> {count} features")
    else:
        print("  No GeoNames file found. Download GB.txt from:")
        print("  https://download.geonames.org/export/dump/GB.zip")

    conn.close()
    print("Done. Database at:", GAZETTEER_DIR / "gazetteer.db")


if __name__ == "__main__":
    main()
