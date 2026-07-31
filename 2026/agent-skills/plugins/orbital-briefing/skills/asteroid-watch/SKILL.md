---
name: asteroid-watch
description: Find near-Earth asteroid approaches for today or a short date range, including hazardous classification, estimated diameter, speed, and miss distance. Use when the user asks what asteroids are passing Earth, wants potentially hazardous objects, or requests structured close-approach data.
license: MIT
compatibility: Requires Deno, a NASA_API_KEY environment variable, and outbound HTTPS access to api.nasa.gov.
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
- Exit code `5` with a `NASA_API_KEY is not set` message means the environment is missing the
  key. Get a free one at https://api.nasa.gov/. There is no `DEMO_KEY` fallback, because that
  shared key allows only about 10 requests per IP and then blocks for hours.
- A `range` window is limited to seven days.
- On Windows, run `deno run --allow-net=api.nasa.gov --allow-env=NASA_API_KEY scripts/asteroid_watch.ts ...`.
