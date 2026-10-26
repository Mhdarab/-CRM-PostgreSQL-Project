"""
check_drive.py - connection health check for the CRM project.

    python check_drive.py            # Drive + Users + Calendar + Email settings
    python check_drive.py --smtp     # also test the Gmail login (sends nothing)
    python check_drive.py --columns  # also print every column of every file

Run from the project root:
    CRM-Capstone-Project-/
    ├── check_drive.py          ← this file
    ├── credentials/
    │   └── service_account.json
    └── services/
        ├── __init__.py         ← MUST exist (can be empty)
        ├── google_service.py
        ├── google_drive_service.py
        ├── google_calendar_service.py
        ├── email_service.py
        └── sheets_service.py
"""

import json
import os
import sys
import textwrap
import time

# ------------------------------------------------------------------ sys.path
_HERE = os.path.dirname(os.path.abspath(__file__))

# Auto-detect: if we're inside tests/ or services/, go one level up
if os.path.basename(_HERE) in ("tests", "services"):
    _PROJECT_ROOT = os.path.dirname(_HERE)
else:
    _PROJECT_ROOT = _HERE

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
    
# ----------------------------------------------------------------- styling
if os.name == "nt":
    os.system("")                       # enables ANSI colours in Windows terminals
USE_COLOR = sys.stdout.isatty()


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


OK, WARN, FAIL = c("[ OK ]", "92"), c("[WARN]", "93"), c("[FAIL]", "91")
WIDTH = 78
results = {"ok": 0, "warn": 0, "fail": 0}


def cell(text, width, code):
    return c(f"{text:<{width}}", code)


def banner(title):
    print("\n" + c("=" * WIDTH, "36"))
    print(c(f" {title}", "1;36"))
    print(c("=" * WIDTH, "36"))


def section(title):
    print("\n" + c(f"-- {title} ", "1") + c("-" * (WIDTH - len(title) - 4), "90"))


def line(tag, label, detail=""):
    key = {OK: "ok", WARN: "warn", FAIL: "fail"}[tag]
    results[key] += 1
    print(f" {tag} {label:<16} {detail}")


def note(text, indent=9):
    for part in textwrap.wrap(text, WIDTH - indent, break_long_words=False,
                              break_on_hyphens=False):
        print(" " * indent + c(part, "90"))


# ----------------------------------------------------------------- imports
try:
    import gspread
    # Try google_service first (has authenticate + SERVICE_ACCOUNT_FILE)
    try:
        from services.google_drive_service import (
            get_client, SERVICE_ACCOUNT_FILE, load_users, CREDENTIALS_FILE,
        )
    except ImportError:
        # Fall back to google_drive_service
        from services.google_drive_service import (
            get_client, fetch_users as _fetch_users,
        )
        SERVICE_ACCOUNT_FILE = os.path.join(
            _HERE, "credentials", "service_account.json"
        )
        CREDENTIALS_FILE = SERVICE_ACCOUNT_FILE

        def load_users():
            try:
                return _fetch_users(), None
            except Exception as exc:
                return [], str(exc)

    # Sheets service (column detection helpers)
    try:
        from services.sheets_services import (
            SHEET_KEYS, read_sheet, pick, make_name_getter,
        )
    except ImportError:
        try:
            from services.sheets_services import (
                SHEET_KEYS, read_sheet, pick, make_name_getter,
            )
        except ImportError:
            # Minimal fallback so the script doesn't crash
            print(f"{WARN} services.sheets_service not found — using minimal fallback")
            SHEET_KEYS = {
                "applications": "Applications",
                "mentor":       "Mentor",
                "interviews":   "Interviews",
                "users":        "Users",
                "vit1":         "VIT1",
                "vit2":         "VIT2",
            }

            def read_sheet(key, force=False):
                from services.google_drive_service import read_sheet as _rs
                records = _rs(SHEET_KEYS.get(key, key))
                if not records:
                    return [], []
                headers = list(records[0].keys())
                rows = [list(r.values()) for r in records]
                return headers, rows

            def pick(headers, *cands, exclude=()):
                low = {h.lower(): h for h in headers}
                for cand in cands:
                    for lk, orig in low.items():
                        if cand.lower() in lk and not any(
                            ex.lower() in lk for ex in exclude
                        ):
                            return orig
                return None

            def make_name_getter(headers):
                col = pick(headers, "full name", "name",
                           "candidate name", exclude=("mentor",))
                if not col:
                    return lambda row: None
                return lambda row: (row.get(col) or "").strip()

    # Spreadsheet IDs map
    try:
        from services.google_drive_service import SPREADSHEET_IDS
    except ImportError:
        SPREADSHEET_IDS = {}

except Exception as exc:
    print(f"{FAIL} Cannot import project modules: {type(exc).__name__}: {exc}")
    print("       Make sure services/__init__.py exists and dependencies are installed:")
    print("           pip install -r requirements.txt")
    sys.exit(1)

started = time.time()
banner("CRM CONNECTION CHECK")

# ----------------------------------------------------------------- 1. auth
section("1. Service account")
client = None
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    line(FAIL, "Key file", "not found")
    note(f"Expected at: {SERVICE_ACCOUNT_FILE}")
else:
    try:
        with open(SERVICE_ACCOUNT_FILE, encoding="utf-8") as f:
            info = json.load(f)
        line(OK, "Key file", os.path.relpath(SERVICE_ACCOUNT_FILE))
        line(OK, "Project", info.get("project_id", "?"))
        line(OK, "Share files with", info.get("client_email", "?"))
        client = get_client()
    except Exception as exc:
        line(FAIL, "Key file", f"{type(exc).__name__}: {exc}")

# ----------------------------------------------------------------- 2. drive
section("2. Files shared with the service account")
if client:
    try:
        files = client.list_spreadsheet_files()
        if files:
            for f in files:
                print(f"        - {f['name']}")
        else:
            line(WARN, "Shared files", "none visible")
            note("Share your Drive sheets with the client_email shown above.")
    except Exception as exc:
        line(FAIL, "Drive list", f"{type(exc).__name__}: {exc}")
else:
    note("Skipped - no valid service account.", 8)

# ----------------------------------------------------------------- 3. crm files
section("3. CRM data files")
show_columns = "--columns" in sys.argv


def detect(key, headers):
    """Which columns the app will actually use."""
    if key == "applications":
        name = make_name_getter(headers)
        sample = {h: "X" for h in headers}
        return {
            "Name": "ok" if name(sample) else None,
            "Email": pick(headers, "email", "e-mail", "mail"),
            "Mentor meeting": pick(headers, "mentor meeting", "mentor", "meeting"),
        }
    if key == "mentor":
        return {
            "Candidate": pick(headers, "candidate name", "full name",
                              "name", exclude=("mentor",)),
            "Recommendation": pick(headers, "recommendation", "suitab"),
        }
    if key == "interviews":
        return {
            "Name": pick(headers, "full name", "name", "candidate name"),
            "Sent": pick(headers, "project sent date", "project sent", "sent"),
            "Received": pick(headers, "project received date",
                             "project received", "received"),
        }
    if key in ("vit1", "vit2"):
        name = make_name_getter(headers)
        return {"Name": "ok" if name({h: "X" for h in headers}) else None}
    return {}


print(f" {'File':<14}{'Status':<9}{'Rows':>6}{'Cols':>6}   Note")
print(" " + c("-" * (WIDTH - 2), "90"))
details = []
for key, title in SHEET_KEYS.items():
    if not SPREADSHEET_IDS.get(title):
        print(f" {title:<14}{cell('SKIPPED', 9, '93')}{'-':>6}{'-':>6}   "
              f"no ID in google_drive_service.py")
        results["warn"] += 1
        details.append((title, "skip", None, None))
        continue
    if not client:
        print(f" {title:<14}{cell('SKIPPED', 9, '93')}{'-':>6}{'-':>6}   "
              f"no service account")
        results["warn"] += 1
        continue
    try:
        headers, rows = read_sheet(key, force=True)
        mapped = detect(key, headers)
        missing = [k for k, v in mapped.items() if not v]
        status = cell("OK", 9, "92") if not missing else cell("CHECK", 9, "93")
        results["ok" if not missing else "warn"] += 1
        msg = "" if not missing else "column not found: " + ", ".join(missing)
        print(f" {title:<14}{status}{len(rows):>6}{len(headers):>6}   {msg}")
        details.append((title, "ok", headers, mapped))
    except gspread.SpreadsheetNotFound:
        print(f" {title:<14}{cell('FAIL', 9, '91')}{'-':>6}{'-':>6}   "
              f"wrong ID or file not shared")
        results["fail"] += 1
    except Exception as exc:
        print(f" {title:<14}{cell('FAIL', 9, '91')}{'-':>6}{'-':>6}   "
              f"{type(exc).__name__}: {str(exc)[:40]}")
        results["fail"] += 1

for title, state, headers, mapped in details:
    if state == "ok" and (show_columns or any(not v for v in mapped.values())):
        print(f"\n   {c(title, '1')} columns:")
        for part in textwrap.wrap(" | ".join(headers), WIDTH - 6):
            print("     " + part)
        used = ", ".join(
            f"{k} -> {v}" for k, v in mapped.items() if v and v != "ok"
        )
        if used:
            print("   " + c(f"used: {used}", "90"))

if any(s == "skip" for _, s, _, _ in details):
    print()
    note("VIT1 / VIT2 are needed only for 'Previous VIT Check' and "
         "'Different Record'. Paste their spreadsheet IDs in "
         "services/google_drive_service.py and share them with the "
         "service account.", 3)

# ----------------------------------------------------------------- 4. login
section("4. Login (Users file)")
try:
    users, err = load_users()
    if err:
        line(FAIL, "Users", err)
    else:
        admins = sum(
            1 for u in users
            if (u.get("authority") or u.get("role") or "").strip().lower() == "admin"
        )
        line(OK, "Users",
             f"{len(users)} users ({admins} admin, {len(users) - admins} user)")
        if users and not ({"username", "password"} <= set(users[0])):
            line(WARN, "Columns", "expected Username / Password / Authority")
except Exception as exc:
    line(FAIL, "Users", f"{type(exc).__name__}: {exc}")

# ----------------------------------------------------------------- 5. calendar
section("5. Google Calendar")
try:
    from services.google_calendar_service import fetch_events, CALENDAR_ID
    events = fetch_events(max_results=10)
    line(OK, "Calendar", f"{CALENDAR_ID} - {len(events)} event(s)")
    for ev in events[:3]:
        print(f"        - {ev['date']} {ev['time']:<8} "
              f"{ev['title'][:32]:<32} "
              f"({len(ev['participants'])} participant(s))")
    if not events:
        line(WARN, "Events", "none - add events with guests, share the calendar")
except Exception as exc:
    line(FAIL, "Calendar", f"{type(exc).__name__}: {str(exc)[:60]}")

# ----------------------------------------------------------------- 6. email
section("6. E-mail (Gmail SMTP)")
try:
    from services.email_service import (
        SMTP_USER, SMTP_PASS, SMTP_SERVER, SMTP_PORT,
    )
    if SMTP_USER and SMTP_PASS:
        masked = SMTP_USER[:2] + "***@" + SMTP_USER.split("@")[-1]
        line(OK, ".env", f"sender {masked}, password set ({len(SMTP_PASS)} chars)")
        if len(SMTP_PASS) != 16:
            line(WARN, "App password",
                 "usually 16 characters - check it is an App Password")
        if "--smtp" in sys.argv:
            import smtplib
            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as s:
                    s.starttls()
                    s.login(SMTP_USER, SMTP_PASS)
                line(OK, "SMTP login",
                     f"{SMTP_SERVER} accepted the credentials (nothing sent)")
            except Exception as exc:
                line(FAIL, "SMTP login",
                     f"{type(exc).__name__}: {str(exc)[:50]}")
        else:
            note("Run with --smtp to test the Gmail login (no e-mail is sent).", 8)
    else:
        line(FAIL, ".env", "CRM_EMAIL / CRM_PASSWORD missing")
except Exception as exc:
    line(FAIL, "E-mail", f"{type(exc).__name__}: {exc}")

# ----------------------------------------------------------------- summary
elapsed = time.time() - started
print("\n" + c("=" * WIDTH, "36"))
summary = (f" SUMMARY   {c(str(results['ok']) + ' ok', '92')}   "
           f"{c(str(results['warn']) + ' warning(s)', '93')}   "
           f"{c(str(results['fail']) + ' failed', '91')}   ({elapsed:.1f}s)")
print(summary)
print(c("=" * WIDTH, "36"))
sys.exit(1 if results["fail"] else 0)