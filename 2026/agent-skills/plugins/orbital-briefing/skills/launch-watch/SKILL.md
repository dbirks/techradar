---
name: launch-watch
description: Look up upcoming rocket launches, launch times, providers, missions, and launch locations. Use when the user asks about the next launch, launches in a date window, SpaceX or another provider, Kennedy Space Center or another site, or wants structured launch data.
license: MIT
compatibility: Requires uv and outbound HTTPS access to ll.thespacedevs.com.
metadata:
  runtime: python-uv
  data-source: launch-library-2
---

# Launch Watch

Use `scripts/launch_watch.py` to retrieve current upcoming launch data.

## Commands

```bash
scripts/launch_watch.py next --help
scripts/launch_watch.py list --help
```

Use `next` for a single soonest matching launch. Use `list` for a bounded schedule.

Prefer `--json` when consuming the result programmatically. Mention that launch schedules can change and include the source timestamp in the response.

## Notes

- Exit code `3` means the request succeeded but nothing matched the filters.
- The unauthenticated API allows roughly 15 requests per hour; each invocation makes one request.
- On Windows, run `uv run scripts/launch_watch.py ...` instead of executing the file directly.
