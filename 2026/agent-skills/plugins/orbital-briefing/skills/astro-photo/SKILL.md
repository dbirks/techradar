---
name: astro-photo
description: Retrieve NASA Astronomy Picture of the Day metadata for today or a specified date, including title, explanation, media type, image or video URL, and copyright attribution. Use when the user asks for today's astronomy image, an APOD from a date, or an astronomy image description.
license: MIT
compatibility: Requires the .NET 10 SDK, a NASA_API_KEY environment variable, and outbound HTTPS access to api.nasa.gov.
metadata:
  runtime: dotnet-file-app
  data-source: nasa-apod
---

# Astronomy Picture

Use `scripts/AstroPhoto.cs` to retrieve NASA APOD metadata.

Always put `--` after the script path. The `dotnet` CLI consumes `--help` and `-h`
itself, so without the separator those flags print `dotnet run` help instead of this
tool's help.

```bash
scripts/AstroPhoto.cs -- today --help
scripts/AstroPhoto.cs -- date --help
scripts/AstroPhoto.cs -- today --json
scripts/AstroPhoto.cs -- date --date 2025-12-25 --json
```

Prefer `--json` for programmatic use. Preserve the returned copyright or attribution field and do not claim every returned asset is public domain.

## Notes

- APOD's archive starts 1995-06-16; earlier or future dates are rejected.
- `--hd` selects `hdurl` when the entry is an image and an HD URL exists.
- Video entries return the video URL with `media_type` set to `video`, and `--hd` is ignored.
- Exit code `5` with a `NASA_API_KEY is not set` message means the environment is missing the
  key. Get a free one at https://api.nasa.gov/. There is no `DEMO_KEY` fallback, because that
  shared key allows only about 10 requests per IP and then blocks for hours.
- On any platform, including Windows, run `dotnet run scripts/AstroPhoto.cs -- today` instead of executing the file directly.
