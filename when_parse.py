# when_parse.py - reads a typed date and time, and shows them nicely (no AI needed)
import re
from datetime import date, datetime, time as dtime, timedelta

def parse_date(text, today=None):
    """Understands 25/11, 25-11, 25.11, 25/11/26, 25/11/2026, 'today', 'tomorrow'. Returns a date or None."""
    today = today or date.today()
    s = text.strip().lower()
    if s == "today":
        return today
    if s == "tomorrow":
        return today + timedelta(days=1)
    m = re.fullmatch(r"(\d{1,2})[/.\- ](\d{1,2})(?:[/.\- ](\d{2}|\d{4}))?", s)
    if not m:
        return None
    day, month, year = int(m[1]), int(m[2]), m[3]
    try:
        if year:
            y = int(year)
            return date(y + 2000 if y < 100 else y, month, day)
        d = date(today.year, month, day)
        if d < today - timedelta(days=7):          # a date that passed long ago must mean next year
            d = date(today.year + 1, month, day)
        return d
    except ValueError:
        return None

def parse_time(text, ampm="AM"):
    """Understands 5, 5:30, 530, 5.30, 5pm, 5:30 pm and 17:30. The AM / PM toggle is used when you do not type am or pm."""
    s = text.strip().lower().replace(".", ":")
    m = re.fullmatch(r"(\d{1,2})(?::?(\d{2}))?\s*(am|pm)?", s)
    if not m:
        return None
    h, mi = int(m[1]), int(m[2] or 0)
    if mi > 59:
        return None
    if m[3]:
        ampm = m[3].upper()
    if h > 12:                                      # typed like 17:30, so the toggle is not needed
        return dtime(h, mi) if h < 24 else None
    return dtime(h % 12 + (12 if ampm == "PM" else 0), mi)

def time_label(t):
    return f"{t.hour % 12 or 12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"

def fmt(due, has_time=True):
    """Mon 09/11, 5:30 PM  (the weekday is worked out automatically)."""
    return f"{due:%a %d/%m}" + (f", {time_label(due.time())}" if has_time else "")
