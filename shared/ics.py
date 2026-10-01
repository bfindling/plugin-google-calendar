import json
from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events
import requests

# Feeds aren't Google calendars, so they get a prefixed ID that can't collide
# with a real calendar ID and tells the tools to read the feed instead.
ICS_PREFIX = "ics:"


def is_ics_calendar(calendar_id: str) -> bool:
    return calendar_id.startswith(ICS_PREFIX)


def require_writable(calendar_id: str) -> None:
    if is_ics_calendar(calendar_id):
        raise SystemExit(f"{calendar_id} is a read-only iCal feed; events can't be created, updated or deleted on it.")


def load_ics_feeds(config: dict[str, Any]) -> dict[str, str]:
    # Plugin config values are usually set as strings, so accept the mapping
    # either as a JSON-encoded string or as an object.
    feeds = config.get("ics_feeds") or {}
    return json.loads(feeds) if isinstance(feeds, str) else feeds


def list_ics_calendars(config: dict[str, Any]) -> list[dict]:
    return [
        {
            "calendar_id": ICS_PREFIX + name,
            "name": name,
            "primary": False,
            "access_role": "reader",
            "timezone": None,
        }
        for name in load_ics_feeds(config)
    ]


def fetch_ics_calendar(config: dict[str, Any], calendar_id: str) -> icalendar.Calendar:
    name = calendar_id.removeprefix(ICS_PREFIX)
    feeds = load_ics_feeds(config)
    if name not in feeds:
        raise SystemExit(f"Unknown iCal feed {name!r}. Use list_calendars to see available IDs.")
    response = requests.get(feeds[name], timeout=30)
    response.raise_for_status()
    return icalendar.Calendar.from_ical(response.content)


def ics_timezone(calendar: icalendar.Calendar) -> ZoneInfo | None:
    name = calendar.get("X-WR-TIMEZONE")
    return ZoneInfo(str(name)) if name else None


def ics_events_between(calendar: icalendar.Calendar, start: datetime, end: datetime) -> list[dict]:
    events = recurring_ical_events.of(calendar).between(start, end)
    return sorted((format_ics_event(event) for event in events), key=lambda event: sort_key(event["start"], start.tzinfo))


def format_ics_event(event: icalendar.Event) -> dict:
    start = event.decoded("DTSTART")
    end = event.decoded("DTEND") if "DTEND" in event else start
    return {
        "id": str(event.get("UID")),
        "title": str(event.get("SUMMARY", "")),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "description": str(event["DESCRIPTION"]) if "DESCRIPTION" in event else None,
        "location": str(event["LOCATION"]) if "LOCATION" in event else None,
        "attendees": [],
    }


def sort_key(value: str, tz: Any) -> datetime:
    # All-day events carry a plain date, which can't be compared with a datetime.
    if "T" not in value:
        return datetime.combine(date.fromisoformat(value), time.min, tzinfo=tz)
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=tz)
