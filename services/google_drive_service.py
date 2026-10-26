"""
Google Drive Service
Author: Waseem

Reads data from MULTIPLE separate Google Sheets — one ID per file.

Setup:
    1. Convert each .xlsx to a native Google Sheet
       (File → Save as Google Sheets)
    2. Share EACH Google Sheet with the service account email
       (from credentials/service_account.json → client_email)
    3. Paste each spreadsheet's ID into SPREADSHEET_IDS below
    4. Make sure the tab name matches (worksheet)
"""

import os
import sys
import gspread
import hmac
from google.oauth2.service_account import Credentials


# --------------------------------------------------
# CONFIG
# --------------------------------------------------
# Next to the .exe when frozen by PyInstaller, otherwise the project root
BASE_DIR = (os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials", "service_account.json")

# Alias used by check_drive.py and other tools
SERVICE_ACCOUNT_FILE = CREDENTIALS_FILE


# --------------------------------------------------
# SPREADSHEET IDs — one per file
# --------------------------------------------------
SPREADSHEET_IDS = {
    "Interviews":   "1hJqf4AelD6fI_EY5PHm4BoZJTNLQmgpedDg3vpk79Gs",
    "Mentor":       "1FzIEp4rMKAohYZpjypTP5EAcmVH_xdqsq9QGgksa0GI",
    "Users":        "1pfSX9Zpl4rJcaDAgsD--puvUh8HawT0iaZoYPOWa2-c",
    "Applications": "1kuiyYAiyrX-aLq3rJqH1xobOQ6bcwMT0d3Nl_li_YTM",
    "VIT1":"188D93b1oAYpxcahaps0-S8oGUw1BPCJMAvgpkLfVQEs",   # ← paste the VIT1 spreadsheet ID
    "VIT2":"13f8wtXb2VFkknD3nQjitmFVaPIEt8CgSZDq_zKrmbD4",   # ← paste the VIT2 spreadsheet ID
}

# --------------------------------------------------
# SCOPES
# --------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


# --------------------------------------------------
# AUTH
# --------------------------------------------------
def _get_client():
    """Return an authenticated gspread client."""
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return gspread.authorize(creds)


# Public alias — check_drive.py expects `get_client`
def get_client():
    """Public alias for _get_client (used by check_drive.py)."""
    return _get_client()


# --------------------------------------------------
# GENERIC READER
# --------------------------------------------------
def read_sheet(key, tab_name=None):
    """
    Read data from a separate spreadsheet.

    Returns a list of dicts (one per row).
    """
    if key not in SPREADSHEET_IDS:
        raise ValueError(f"Unknown sheet key: '{key}'")
    if not SPREADSHEET_IDS[key]:
        raise ValueError(
            f"No spreadsheet ID set for '{key}' in services/google_drive_service.py")

    client = _get_client()
    spreadsheet = client.open_by_key(SPREADSHEET_IDS[key])

    if tab_name:
        worksheet = spreadsheet.worksheet(tab_name)
    else:
        worksheet = spreadsheet.sheet1

    return worksheet.get_all_records()


# --------------------------------------------------
# SPECIFIC FETCHERS
# --------------------------------------------------
def fetch_interviews():
    return read_sheet("Interviews")


def fetch_mentor():
    return read_sheet("Mentor")


def fetch_users():
    return read_sheet("Users")


def fetch_applications():
    return read_sheet("Applications")


def fetch_vit1():
    return read_sheet("VIT1")


def fetch_vit2():
    return read_sheet("VIT2")


# --------------------------------------------------
# HELPERS FOR LOGIN
# --------------------------------------------------
def _normalise(record):
    """Lower-case header names, strip values."""
    return {str(k).strip().lower(): str(v).strip() for k, v in record.items()}


def _role_of(user):
    value = (user.get("authority") or user.get("role")
             or user.get("login authority") or "user")
    return "admin" if value.strip().lower() == "admin" else "user"


def _same(a, b):
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


# Alias expected by check_drive.py
def load_users():
    """
    Read + normalise the Users sheet.

    Returns (users, error) — same contract as google_service.load_users().
    """
    try:
        users = [_normalise(r) for r in fetch_users()]
        return users, None
    except FileNotFoundError:
        return [], "service_account.json not found in the credentials folder."
    except Exception as exc:
        return [], f"Could not read the Users file from Drive: {exc}"


def authenticate(username, password):
    """
    Verify a user against the Users spreadsheet.

    Returns (success: bool, role: 'admin' | 'user' | None, message: str)
    """
    users, err = load_users()
    if err:
        return False, None, err
    if not users:
        return False, None, "The Users file is empty."

    for user in users:
        if user.get("username", "").lower() == username.lower():
            if _same(user.get("password", ""), password):
                return True, _role_of(user), "Login successful"
            return False, None, "Wrong password."
    return False, None, "User not found."