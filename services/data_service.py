"""
data_service.py - business logic for the Applications, Mentor and
Interviews pages. Every function reads from Google Drive (gspread) and
NEVER raises: on failure it returns an empty result and the page can show
get_last_error().
"""

import functools

from services.sheets_services import (
    read_sheet, pick, norm, make_name_getter, make_email_getter, friendly_error,
)

_last_error = ""


def get_last_error():
    return _last_error


def _guard(default_factory):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            global _last_error
            _last_error = ""
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                _last_error = friendly_error(exc)
                return default_factory()
        return wrapper
    return decorator


def name_matches(query, name):
    """'As' matches 'Asma Ali' and 'Ali Asaad' (start of any word)."""
    q = norm(query)
    return bool(q) and (" " + q) in (" " + norm(name))


# =========================================================== INTERVIEWS
INTERVIEW_COLS = ["Full Name", "Project Sent Date", "Project Received Date"]


def _interviews(refresh=False):
    headers, rows = read_sheet("interviews", force=refresh)
    name = make_name_getter(headers)
    sent = pick(headers, "project sent date", "project sent", "sent")
    recv = pick(headers, "project received date", "project received", "received")
    return [{
        "Full Name": name(r),
        "Project Sent Date": r.get(sent, "") if sent else "",
        "Project Received Date": r.get(recv, "") if recv else "",
    } for r in rows]


_NO = {"", "no", "false", "0", "-", "none", "n/a", "na", "not sent",
       "not received", "not defined", "not identified", "undefined"}


def _is_yes(value):
    return norm(value) not in _NO


@_guard(list)
def get_all_interviews(refresh=False):
    return _interviews(refresh)


@_guard(list)
def search_interviews(q):
    return [r for r in _interviews() if name_matches(q, r["Full Name"])]


@_guard(list)
def get_projects_sent():
    return [r for r in _interviews() if _is_yes(r["Project Sent Date"])]


@_guard(list)
def get_projects_received():
    return [r for r in _interviews() if _is_yes(r["Project Received Date"])]


# =========================================================== MENTOR
MENTOR_COLS = ["Date", "VIT Group", "Candidate Name", "Mentor Name",
               "Score", "Recommendation", "Secondary Score", "Notes"]

_MENTOR_ALIASES = {
    "Date": ("date",),
    "VIT Group": ("vit group", "vit", "group"),
    "Mentor Name": ("mentor name", "mentor"),
    "Score": ("score",),
    "Recommendation": ("recommendation", "suitab"),
    "Secondary Score": ("secondary score", "second score", "score 2"),
    "Notes": ("notes", "note", "comment"),
}


def _mentor(refresh=False):
    headers, rows = read_sheet("mentor", force=refresh)
    name = make_name_getter(headers)
    cols = {c: pick(headers, *keys) for c, keys in _MENTOR_ALIASES.items()}
    out = []
    for r in rows:
        item = {c: (r.get(h, "") if h else "") for c, h in cols.items()}
        item["Candidate Name"] = name(r)
        out.append(item)
    return out


def _clean(text):
    return norm(text).rstrip(".")


@_guard(list)
def get_all_conversations(refresh=False):
    return _mentor(refresh)


@_guard(list)
def search_conversations(q):
    return [r for r in _mentor() if name_matches(q, r["Candidate Name"])]


@_guard(list)
def get_conversations_by_recommendation(value):
    wanted = _clean(value)
    return [r for r in _mentor() if _clean(r["Recommendation"]) == wanted]


# =========================================================== APPLICATIONS
# Every function returns (headers, rows) so the table can show any columns.

def _app_key(row, name, email):
    return (norm(name(row)), email(row))


@_guard(lambda: ([], []))
def get_applications(refresh=False):
    return read_sheet("applications", force=refresh)


@_guard(lambda: ([], []))
def search_applications(q):
    headers, rows = read_sheet("applications")
    name = make_name_getter(headers)
    return headers, [r for r in rows if name_matches(q, name(r))]


def _mentor_split(defined):
    headers, rows = read_sheet("applications")
    col = pick(headers, "mentor meeting", "mentor", "meeting")
    if not col:
        raise KeyError("No 'Mentor meeting' column found in the Applications file.")
    return headers, [r for r in rows if _is_yes(r.get(col, "")) == defined]


@_guard(lambda: ([], []))
def get_mentor_defined():
    return _mentor_split(True)


@_guard(lambda: ([], []))
def get_mentor_not_defined():
    return _mentor_split(False)


@_guard(lambda: ([], []))
def get_duplicate_applications():
    """Only the people registered more than once (same name + e-mail)."""
    headers, rows = read_sheet("applications")
    name, email = make_name_getter(headers), make_email_getter(headers)
    counts = {}
    for r in rows:
        k = _app_key(r, name, email)
        counts[k] = counts.get(k, 0) + 1
    dup = [r for r in rows
           if _app_key(r, name, email)[0] and counts[_app_key(r, name, email)] > 1]
    dup.sort(key=lambda r: _app_key(r, name, email))
    return headers, dup


@_guard(lambda: ([], []))
def get_unique_applications():
    """Duplicates removed: each person (name + e-mail) appears once."""
    headers, rows = read_sheet("applications")
    name, email = make_name_getter(headers), make_email_getter(headers)
    seen, out = set(), []
    for r in rows:
        k = _app_key(r, name, email)
        if k[0] and k in seen:
            continue
        seen.add(k)
        out.append(r)
    return headers, out


def _vit_people():
    result = {}
    for key, label in (("vit1", "VIT1"), ("vit2", "VIT2")):
        headers, rows = read_sheet(key)
        name = make_name_getter(headers)
        result[label] = (headers, rows, name)
    return result


@_guard(lambda: ([], []))
def get_previous_vit():
    """Applicants who also appear in VIT1 and/or VIT2."""
    headers, rows = read_sheet("applications")
    name = make_name_getter(headers)
    vit = _vit_people()
    names = {lbl: {norm(n(r)) for r in rs if n(r)} for lbl, (_, rs, n) in vit.items()}
    out = []
    for r in rows:
        key = norm(name(r))
        found = [lbl for lbl, s in names.items() if key and key in s]
        if found:
            out.append({**r, "Found In": " + ".join(found)})
    return headers + ["Found In"], out


@_guard(lambda: ([], []))
def get_different_records():
    """Candidates that are NOT common to VIT1 and VIT2 (only in one of them)."""
    vit = _vit_people()
    names = {lbl: {norm(n(r)) for r in rs if n(r)} for lbl, (_, rs, n) in vit.items()}
    common = names["VIT1"] & names["VIT2"]

    headers, out = ["VIT"], []
    for lbl, (hs, rs, n) in vit.items():
        headers += [h for h in hs if h not in headers]
        out += [{"VIT": lbl, **r} for r in rs if norm(n(r)) not in common]
    return headers, out