"""
export_data.py
==============
Pull all data from Google Sheets and save it as JSON files in data/.

Usage:
    python export_data.py

Output:
    data/applications.json
    data/mentor.json
    data/interviews.json
    data/users.json
    data/vit1.json
    data/vit2.json

Security note:
    data/users.json contains passwords — never push it to GitHub.
    Add data/users.json to .gitignore.
"""

import json
import os
import sys
import traceback

from services.google_drive_service import (
    fetch_applications,
    fetch_mentor,
    fetch_interviews,
    fetch_users,
    fetch_vit1,
    fetch_vit2,
)


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)


# --------------------------------------------------
# Sheets to export
# --------------------------------------------------
SHEETS = [
    ("applications", fetch_applications),
    ("mentor",       fetch_mentor),
    ("interviews",   fetch_interviews),
    ("users",        fetch_users),
    ("vit1",         fetch_vit1),
    ("vit2",         fetch_vit2),
]


# --------------------------------------------------
# Export one sheet
# --------------------------------------------------
def export_one(name, func):
    print(f"-> {name:<15}", end=" ", flush=True)

    try:
        records = func()
    except Exception as exc:
        print("FAILED")
        print(f"    Reason: {type(exc).__name__}: {exc}")
        return False

    if not records:
        print("EMPTY (0 rows) — skipped")
        return False

    path = os.path.join(DATA_DIR, f"{name}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except Exception:
        print("FAILED to write")
        traceback.print_exc()
        return False

    print(f"OK {len(records)} rows -> {path}")
    return True


# --------------------------------------------------
# main
# --------------------------------------------------
def main():
    print("=" * 60)
    print("Export Google Drive data -> data/*.json")
    print("=" * 60)
    print(f"Data folder: {DATA_DIR}")
    print()

    ok, failed = 0, 0
    for name, func in SHEETS:
        if export_one(name, func):
            ok += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"Result: {ok} succeeded, {failed} failed")
    print("=" * 60)

    if failed:
        print()
        print("Troubleshooting:")
        print("  - Check credentials/service_account.json exists")
        print("  - Share each Google Sheet with the service account client_email")
        print("  - Verify SPREADSHEET_IDS in google_drive_service.py")
        print("  - Make sure files are native Google Sheets (not .xlsx)")
        print("  - Make sure VIT1 and VIT2 IDs are set (not empty)")
        sys.exit(1)


if __name__ == "__main__":
    main()