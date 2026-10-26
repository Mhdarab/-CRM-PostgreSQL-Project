"""
sheets_service.py - low-level Google Sheets reading (gspread).

* Spreadsheets are opened by ID (SPREADSHEET_IDS in google_drive_service.py).
* The header row is detected automatically and columns are found by name
  (see pick()), so small differences in column names do not break the app.
* Results are kept in memory for CACHE_TTL_SECONDS so clicking buttons is
  fast. Set it to 0 to always read live from Drive.
"""

import re
import time

from services.google_drive_service import SPREADSHEET_IDS, _get_client

# internal key -> key in SPREADSHEET_IDS
SHEET_KEYS = {
    "applications": "Applications",
    "mentor": "Mentor",
    "interviews": "Interviews",
    "vit1": "VIT1",
    "vit2": "VIT2",
}

CACHE_TTL_SECONDS = 60
_cache = {}


# ------------------------------------------------------------------ helpers
def norm(value):
    """Lower-case, trimmed, single-spaced text."""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def pick(headers, *keys, exclude=()):
    """Find a header: exact match first, then 'contains'. Returns None if absent."""
    usable = [h for h in headers if not any(x in norm(h) for x in exclude)]
    for key in keys:
        for h in usable:
            if norm(h) == key:
                return h
    for key in keys:
        for h in usable:
            if key in norm(h):
                return h
    return None


def make_name_getter(headers):
    """Return f(row) -> candidate's full name, whatever the columns look like."""
    full = pick(headers, "full name", "candidate name", "applicant name",
                "name", "candidate", "applicant", exclude=("mentor",))
    exact = {norm(h) for h in headers}
    if full and norm(full) in exact and norm(full) in (
            "full name", "candidate name", "applicant name", "name",
            "candidate", "applicant"):
        return lambda row: row.get(full, "").strip()

    first = pick(headers, "first name", "given name", exclude=("mentor",))
    last = pick(headers, "last name", "surname", "family name", exclude=("mentor",))
    if first and last:
        return lambda row: f"{row.get(first, '')} {row.get(last, '')}".strip()
    if full:
        return lambda row: row.get(full, "").strip()
    return lambda row: ""


def make_email_getter(headers):
    col = pick(headers, "email", "e-mail", "mail")
    return (lambda row: norm(row.get(col, ""))) if col else (lambda row: "")


def _unique_headers(raw):
    seen, out = {}, []
    for i, h in enumerate(raw):
        h = str(h).strip() or f"Column {i + 1}"
        if h in seen:
            seen[h] += 1
            h = f"{h} ({seen[h]})"
        else:
            seen[h] = 1
        out.append(h)
    return out


def friendly_error(exc):
    """Short human-readable text for the status label."""
    import gspread
    if isinstance(exc, FileNotFoundError):
        return "credentials/service_account.json not found."
    if isinstance(exc, ValueError):
        return str(exc)
    if isinstance(exc, gspread.SpreadsheetNotFound):
        return ("A Drive file was not found. Check its ID in SPREADSHEET_IDS "
                "(services/google_drive_service.py) and share it with the service account.")
    if isinstance(exc, gspread.exceptions.APIError):
        return f"Google API error: {exc}"
    return f"{type(exc).__name__}: {exc}"


# ------------------------------------------------------------------ reading
def read_sheet(key, force=False):
    """Return (headers, rows) where rows is a list of dicts keyed by header."""
    now = time.time()
    cached = _cache.get(key)
    if cached and not force and CACHE_TTL_SECONDS > 0 \
            and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1], cached[2]

    sheet_id = SPREADSHEET_IDS.get(SHEET_KEYS[key], "")
    if not sheet_id:
        raise ValueError(
            f"No spreadsheet ID set for '{SHEET_KEYS[key]}' in "
            "services/google_drive_service.py")
    worksheet = _get_client().open_by_key(sheet_id).sheet1
    values = worksheet.get_all_values()

    header_idx = next(
        (i for i, r in enumerate(values)
         if sum(1 for x in r if str(x).strip()) >= 2), None)
    if header_idx is None:
        return [], []

    raw = list(values[header_idx])
    while raw and not str(raw[-1]).strip():
        raw.pop()
    headers = _unique_headers(raw)

    rows = []
    for r in values[header_idx + 1:]:
        if not any(str(x).strip() for x in r):
            continue
        r = list(r) + [""] * (len(headers) - len(r))
        rows.append({h: str(r[i]).strip() for i, h in enumerate(headers)})

    _cache[key] = (now, headers, rows)
    return headers, rows


def clear_cache():
    _cache.clear()