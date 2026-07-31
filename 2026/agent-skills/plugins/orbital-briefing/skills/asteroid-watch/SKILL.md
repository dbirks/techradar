---
name: asteroid-watch
description: Find near-Earth asteroid approaches for today or a short date range, including hazardous classification, estimated diameter, speed, and miss distance. Use when the user asks what asteroids are passing Earth, wants potentially hazardous objects, or requests structured close-approach data.
license: MIT
compatibility: Requires Deno and outbound HTTPS access to api.nasa.gov. NASA_API_KEY is optional; DEMO_KEY is used otherwise.
metadata:
  runtime: deno
  data-source: nasa-neows
---

# Asteroid Watch

Use `scripts/asteroid_watch.ts` to query NASA's Near Earth Object Web Service.

```bash
scripts/asteroid_watch.ts today --help
scripts/asteroid_watch.ts range --help
```

Prefer `--json` for programmatic use. State that "potentially hazardous" is NASA's catalog classification, not a prediction of impact.

## Notes

- Exit code `3` means the feed was retrieved but nothing matched the filters.
- A `range` window is limited to seven days.
- `DEMO_KEY` is heavily rate-limited; set `NASA_API_KEY` for repeated use.
- On Windows, run `deno run --allow-net=api.nasa.gov --allow-env=NASA_API_KEY scripts/asteroid_watch.ts ...`.
