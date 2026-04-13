---
id: pgc-n01a
status: closed
deps: []
links: []
created: 2026-04-13T09:42:51Z
type: task
priority: 2
assignee: Stavros Korokithakis
---
# Add attendees and location to update_event

Add optional 'attendees' and 'location' parameters to update_event. Same semantics as create_event: omit → not sent (PATCH leaves unchanged). Empty string → raise error. 'none' → send empty attendees array. Other value → comma-separated emails. Location follows existing optional field pattern. Update manifest.json and run.py. Update format_event to include attendees and location, same as create_event.

## Acceptance Criteria

manifest.json declares both params. run.py handles all attendees cases plus location in the PATCH body. format_event returns attendees and location.

