---
name: recent-satellites
description: List and search satellites and other space objects associated with launches from the last 30 days. Use when the user asks what satellites were launched recently, wants to search recent cataloged objects by name, or needs NORAD catalog and orbital-element metadata.
license: MIT
compatibility: Requires JBang and outbound HTTPS access to celestrak.org.
metadata:
  runtime: java-jbang
  data-source: celestrak
---

# Recent Satellites

Use `scripts/RecentSatellites.java` for CelesTrak's machine-readable recent-launch catalog.

```bash
scripts/RecentSatellites.java recent --help
scripts/RecentSatellites.java find --help
```

Prefer `--json` for programmatic use. Distinguish a cataloged orbital object from a launch event: one launch can produce many payloads, rocket bodies, or debris objects.

## Notes

- Exit code `3` means the catalog was retrieved but nothing matched the filters.
- CelesTrak's GP feed carries no object-type field. Payload, rocket body, and debris
  are inferred from the object name (`R/B`, `DEB`), so the type is reported as a hint.
- Orbital period is derived from mean motion (`1440 / MEAN_MOTION` minutes).
- On Windows, run `jbang scripts/RecentSatellites.java ...`.
