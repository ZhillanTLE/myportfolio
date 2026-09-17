"""GitHub's contribution calendar for the site footer.

GitHub has no public API for the calendar without a token, so this reads the same HTML
fragment the profile page loads (/users/<name>/contributions) and keeps what the footer draws.
"""
import re
import urllib.request

from django.core.cache import cache

USERNAME = "ZhillanTLE"
PROFILE_URL = f"https://github.com/{USERNAME}"
CALENDAR_URL = f"https://github.com/users/{USERNAME}/contributions"

CACHE_KEY = "github-contributions"
CACHE_SECONDS = 6 * 60 * 60     # the calendar only moves a few times a day
RETRY_SECONDS = 10 * 60         # after a failed fetch, don't ask again on every page view

TOTAL = re.compile(r"([\d,]+)\s+contributions?\s+in the last year")
DAY_CELL = re.compile(r"<td[^>]*\bContributionCalendar-day\b[^>]*>")
TOOLTIP = re.compile(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>')
ATTR = lambda name: re.compile(rf'\b{name}="([^"]*)"')
DATE, LEVEL, CELL_ID = ATTR("data-date"), ATTR("data-level"), ATTR("id")
COUNT = re.compile(r"^(\d+)")


def parse_calendar(html):
    """Turn the calendar HTML into {total, days: [{date, level, count}]}, or None if it isn't one."""
    total = TOTAL.search(html)
    tooltips = dict(TOOLTIP.findall(html))
    days = []
    for cell in DAY_CELL.findall(html):
        date, level, cell_id = DATE.search(cell), LEVEL.search(cell), CELL_ID.search(cell)
        if not (date and level):
            continue
        label = tooltips.get(cell_id.group(1), "") if cell_id else ""
        count = COUNT.match(label)
        days.append({
            "date": date.group(1),
            "level": int(level.group(1)),
            "count": int(count.group(1)) if count else 0,
        })
    if not total or not days:
        return None
    days.sort(key=lambda day: day["date"])
    return {"total": int(total.group(1).replace(",", "")), "days": days}


def fetch_contributions():
    request = urllib.request.Request(CALENDAR_URL, headers={"User-Agent": "myportfolio-footer"})
    with urllib.request.urlopen(request, timeout=8) as response:
        return parse_calendar(response.read().decode("utf-8", "replace"))


def get_contributions():
    """Cached calendar; None when GitHub can't be reached or the page changed shape."""
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached or None   # {} marks a recent failure
    try:
        calendar = fetch_contributions()
    except Exception:
        calendar = None
    cache.set(CACHE_KEY, calendar or {}, CACHE_SECONDS if calendar else RETRY_SECONDS)
    return calendar
