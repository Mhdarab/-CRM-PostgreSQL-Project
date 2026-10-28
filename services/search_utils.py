import re


def norm(value):
    """Lower-case, trimmed, single-spaced text."""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def name_matches(query, name):
    """Match the beginning of any word in a name."""
    q = norm(query)
    return bool(q) and (" " + q) in (" " + norm(name))