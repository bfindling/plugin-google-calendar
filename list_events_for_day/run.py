#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests"]
# ///

import json
import sys
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import requests

# The tool's CWD is list_events_for_day/, so appending ".." makes the sibling shared/ package importable.
sys.path.append("..")

from shared.auth import get_calendar_headers, load_config, quote_calendar_id, resolve_calendar_id


def get_calendar_timezone(calendar_id: str, headers: dict[str, str]) -> ZoneInfo:
    response = requests.get(
        f"https://www.googleapis.com/calendar/v3/calendars/{quote_calendar_id(calendar_id)}",
        headers=headers,
    )
    response.raise_for_status()
    return ZoneInfo(response.json()["timeZone"])


def resolve_day(date_param: str | None, tz: ZoneInfo) -> date:
    # "Today" is resolved in the calendar's own timezone, not the container's,
    # so it matches what the user actually sees in their calendar.
    if date_param:
        return date.fromisoformat(date_param)
    return datetime.now(tz).date()


def day_bounds(day: date, tz: ZoneInfo) -> tuple[str, str]:
    start = datetime.combine(day, time.min, tzinfo=tz)
    end = start + timedelta(days=1)
    return start.isoformat(), end.isoformat()


def fetch_events(date_param: str | None, calendar_id_param: str | None) -> list[dict]:
    config = load_config()
    headers = get_calendar_headers(config)
    calendar_id = resolve_calendar_id(config, calendar_id_param)

    tz = get_calendar_timezone(calendar_id, headers)
    day = resolve_day(date_param, tz)
    time_min, time_max = day_bounds(day, tz)

    response = requests.get(
        f"https://www.googleapis.com/calendar/v3/calendars/{quote_calendar_id(calendar_id)}/events",
        headers=headers,
        params={
            "timeMin": time_min,
            "timeMax": time_max,
            # Expand recurring events into individual instances so they appear as discrete entries.
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": 250,
        },
    )
    response.raise_for_status()
    return response.json().get("items", [])


def format_event(event: dict) -> dict:
    return {
        "id": event.get("id"),
        "title": event.get("summary"),
        # All-day events use "date" instead of "dateTime".
        "start": event["start"].get("dateTime") or event["start"].get("date"),
        "end": event["end"].get("dateTime") or event["end"].get("date"),
        "description": event.get("description"),
        "location": event.get("location"),
        "attendees": [attendee["email"] for attendee in event.get("attendees", [])],
    }


def main() -> None:
    params = json.load(sys.stdin)
    date_param = params.get("date")
    calendar_id_param = params.get("calendar_id")

    events = fetch_events(date_param, calendar_id_param)
    formatted = [format_event(event) for event in events]

    json.dump({"events": formatted}, sys.stdout)


main()
