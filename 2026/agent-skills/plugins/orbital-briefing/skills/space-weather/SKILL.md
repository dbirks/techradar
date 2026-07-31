---
name: space-weather
description: Check current NOAA space-weather alerts and geomagnetic activity, including G-scale, S-scale, R-scale notices and planetary K-index observations. Use for aurora conditions, geomagnetic storms, radio blackouts, solar radiation storms, or a current space-weather briefing.
license: MIT
compatibility: Requires Bun and outbound HTTPS access to services.swpc.noaa.gov.
metadata:
  runtime: bun
  data-source: noaa-swpc
---

# Space Weather

Use `scripts/space_weather.ts` for current NOAA SWPC data.

```bash
scripts/space_weather.ts alerts --help
scripts/space_weather.ts kp --help
```

Use `alerts` for watches, warnings, and alerts. Use `kp` for planetary K-index observations. Prefer `--json` for programmatic use and preserve NOAA's issue timestamps.

## Notes

- Exit code `3` means the feed was retrieved but nothing matched the filters.
- `--storm-only` means Kp of 5 or higher (NOAA G1 or stronger).
- On Windows, run `bun scripts/space_weather.ts ...` instead of executing the file directly.
