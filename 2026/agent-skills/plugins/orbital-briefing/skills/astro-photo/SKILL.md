---
name: astro-photo
description: Retrieve NASA Astronomy Picture of the Day metadata for today or a specified date, including title, explanation, media type, image or video URL, and copyright attribution. Use when the user asks for today's astronomy image, an APOD from a date, or an astronomy image description.
license: MIT
compatibility: Requires the .NET 10 SDK and outbound HTTPS access to api.nasa.gov. NASA_API_KEY is optional; DEMO_KEY is used otherwise.
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
- Video entries return the video URL with `media_type` set to `video`.
- `DEMO_KEY` is heavily rate-limited; set `NASA_API_KEY` for repeated use.
- On any platform, including Windows, run `dotnet run scripts/AstroPhoto.cs -- today` instead of executing the file directly.
