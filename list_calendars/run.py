#!/usr/bin/env -S uv run
# /// script
# dependencies = ["google-auth", "icalendar", "recurring-ical-events", "requests"]
# ///

import json
import sys

import requests

# The tool's CWD is list_calendars/, so appending ".." makes the sibling shared/ package importable.
sys.path.append("..")

from shared.auth import get_calendar_headers, load_config
from shared.ics import list_ics_calendars


def fetch_calendars(config: dict) -> list[dict]:
    headers = get_calendar_headers(config)

    calendars = []
    page_token = None
    while True:
        params = {"maxResults": 250}
        if page_token:
            params["pageToken"] = page_token

        response = requests.get(
            "https://www.googleapis.com/calendar/v3/users/me/calendarList",
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        data = response.json()
        calendars.extend(data.get("items", []))

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return calendars


def format_calendar(calendar: dict) -> dict:
    return {
        "calendar_id": calendar.get("id"),
        "name": calendar.get("summaryOverride") or calendar.get("summary"),
        "primary": calendar.get("primary", False),
        "access_role": calendar.get("accessRole"),
        "timezone": calendar.get("timeZone"),
    }


def main() -> None:
    json.load(sys.stdin)  # No parameters, but drain stdin to match the tool contract.

    config = load_config()
    calendars = fetch_calendars(config)
    formatted = [format_calendar(calendar) for calendar in calendars] + list_ics_calendars(config)

    json.dump({"calendars": formatted}, sys.stdout)


main()
