---
id: pgc-dcgb
status: closed
deps: []
links: []
created: 2026-04-13T09:42:52Z
type: task
priority: 2
assignee: Stavros Korokithakis
---
# Update list_events format_event to include attendees and location

Update format_event in list_events/run.py to include 'attendees' (list of email strings from the API response) and 'location', matching the format_event in create_event and update_event.

## Acceptance Criteria

format_event returns attendees and location fields.

