---
id: pgc-3am0
status: closed
deps: []
links: []
created: 2026-04-13T09:42:48Z
type: task
priority: 2
assignee: Stavros Korokithakis
---
# Add attendees and location to create_event

Add optional 'attendees' and 'location' parameters to create_event. Update manifest.json with both new parameters. Update run.py to map them to the Google Calendar API body. Attendees semantics: omit → not sent. Empty string → raise an error with message 'To remove all attendees, pass "none" instead of an empty string.' 'none' → send empty attendees array. Any other value → split on comma, strip whitespace, build [{"email": ...}] list. Location is a plain string, same pattern as description (only include when provided). Update format_event to include 'attendees' (list of email strings extracted from the API response's attendees array) and 'location'. Follow existing code patterns exactly.

## Acceptance Criteria

manifest.json declares attendees and location params with clear descriptions including the 'none' sentinel docs. run.py handles all three attendees cases plus location. format_event returns attendees and location.

