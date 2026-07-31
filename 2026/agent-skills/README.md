# Agent Skills: Orbital Briefing

Homepage: https://agentskills.io/

Specification: https://agentskills.io/specification

GitHub: https://github.com/agentskills/agentskills

Tech Radar: https://www.thoughtworks.com/en-us/radar/techniques/agent-skills

**Assessment:** Trial (April 2026, Volume 34)

Agent Skills is an open format for packaging instructions, scripts, documentation, and other resources that an AI agent can discover and load only when they are relevant. Every skill is a directory with a required `SKILL.md`; optional `scripts/`, `references/`, and `assets/` directories let the skill carry executable tools and supporting material with it.

This example collection uses real space-data APIs to show that a skill can carry a polished, dependency-aware command-line utility without requiring a conventional application repository.

## Included skills

| Skill | Runtime | CLI library | Live data |
|---|---|---|---|
| `launch-watch` | Python via `uv` and PEP 723 | Typer | The Space Devs Launch Library 2 |
| `space-weather` | Bun | Commander.js | NOAA Space Weather Prediction Center |
| `asteroid-watch` | Deno | Cliffy | NASA Near Earth Object Web Service |
| `recent-satellites` | Java via JBang | picocli | CelesTrak GP data |
| `astro-photo` | .NET 10 file-based C# | System.CommandLine | NASA Astronomy Picture of the Day |

## Why these are genuinely self-contained

- **Python/uv:** PEP 723 metadata declares PyPI dependencies in the `.py` file.
- **Bun:** a version-pinned package specifier such as `commander@15.0.0` is installed and cached automatically when the script runs.
- **Deno:** a versioned `jsr:` import resolves and caches the package without a local `package.json`.
- **Java/JBang:** `//DEPS` comments resolve Maven Central dependencies before compiling and running the source file.
- **.NET 10:** file-based apps use `#:package` directives to restore NuGet packages directly from one `.cs` file.

## Try the tools directly

```bash
# Python + uv: upcoming rocket launches
./plugins/orbital-briefing/skills/launch-watch/scripts/launch_watch.py next
./plugins/orbital-briefing/skills/launch-watch/scripts/launch_watch.py list --days 30 --provider SpaceX --limit 5
./plugins/orbital-briefing/skills/launch-watch/scripts/launch_watch.py list --days 30 --location "Cape Canaveral" --json

# Bun: NOAA alerts and planetary K-index observations
./plugins/orbital-briefing/skills/space-weather/scripts/space_weather.ts alerts --limit 5
./plugins/orbital-briefing/skills/space-weather/scripts/space_weather.ts kp --storm-only --json

# Deno: near-Earth asteroid approaches
./plugins/orbital-briefing/skills/asteroid-watch/scripts/asteroid_watch.ts today --hazardous
./plugins/orbital-briefing/skills/asteroid-watch/scripts/asteroid_watch.ts range --start 2026-08-01 --end 2026-08-07 --limit 10

# Java + JBang: recently launched cataloged objects
./plugins/orbital-briefing/skills/recent-satellites/scripts/RecentSatellites.java recent --limit 15
./plugins/orbital-briefing/skills/recent-satellites/scripts/RecentSatellites.java find starlink --json

# .NET 10: NASA's astronomy image and metadata
./plugins/orbital-briefing/skills/astro-photo/scripts/AstroPhoto.cs today
./plugins/orbital-briefing/skills/astro-photo/scripts/AstroPhoto.cs date --date 2025-12-25 --json
```

Every tool must also support `--help`, return nonzero on failure, keep human diagnostics on stderr, and offer `--json` for agent-safe structured output.

### Shared exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `2` | Usage error raised by the CLI library (unknown flag, bad choice, missing argument) |
| `3` | The request succeeded but nothing matched the filters |

| `4` | Upstream API failure: unreachable, timed out, rate-limited, or malformed response |
| `5` | Invalid input rejected before any network call |

Exit code `3` is a normal answer, not a bug. Narrow filters legitimately return nothing —
a specific launch site can be quiet for weeks, and `--hazardous` or `--storm-only` are
often empty on a calm day. Before demoing a specific filter live, check that it currently
matches. Note that Launch Library 2 treats "Kennedy Space Center" and "Cape Canaveral SFS"
as different locations, so filtering on one excludes the other.

### Optional API keys

`NASA_API_KEY` is honored by `asteroid-watch` and `astro-photo`. Without it both fall back to
NASA's shared `DEMO_KEY`, which is heavily rate-limited and will start returning exit code `4`
after a handful of calls. A free key from https://api.nasa.gov/ removes that limit:

```bash
export NASA_API_KEY=your-key-here
```

`launch-watch` needs no key, but the unauthenticated Launch Library 2 endpoint allows only
about 15 requests per hour. For repeated local development, point it at the deliberately
stale development endpoint instead:

```bash
export LL2_BASE_URL=https://lldev.thespacedevs.com/2.3.0
```

Never use that endpoint to answer a real question; its data is intentionally out of date.

## Validate the skills

The `skills-ref` package installs its CLI as `agentskills`, so it has to be run through
`uvx --from`. From `plugins/orbital-briefing`:

```bash
for skill in launch-watch space-weather asteroid-watch recent-satellites astro-photo
do
  uvx --from skills-ref agentskills validate "./skills/${skill}"
done
```

## Install with GitHub CLI Agent Skills commands

The current canonical command is `gh skill install`; `gh skill add` and `gh skills add` are aliases.

Preview one nested skill before installing it:

```bash
gh skill preview dbirks/techradar \
  2026/agent-skills/plugins/orbital-briefing/skills/launch-watch
```

Install one skill for GitHub Copilot:

```bash
gh skill install dbirks/techradar \
  2026/agent-skills/plugins/orbital-briefing/skills/launch-watch \
  --agent github-copilot \
  --scope user
```

Install the same skill for Claude Code:

```bash
gh skill install dbirks/techradar \
  2026/agent-skills/plugins/orbital-briefing/skills/launch-watch \
  --agent claude-code \
  --scope user
```

Install all five remote skills while still targeting their exact nested paths:

```bash
for skill in \
  launch-watch \
  space-weather \
  asteroid-watch \
  recent-satellites \
  astro-photo
do
  gh skill install dbirks/techradar \
    "2026/agent-skills/plugins/orbital-briefing/skills/${skill}" \
    --agent github-copilot \
    --scope user
done
```

`--all` is most useful when the repository or local directory contains only the desired skills. The explicit loop avoids accidentally installing unrelated skills that may already exist elsewhere in `dbirks/techradar`.

For a local checkout, use `--from-local`:

```bash
gh skill install \
  ./2026/agent-skills/plugins/orbital-briefing/skills/launch-watch \
  --from-local \
  --agent github-copilot \
  --scope project
```

`gh skill install` expects a GitHub repository as `OWNER/REPO`; it does not use separate HTTPS and SSH spellings for a remote skill source. HTTPS versus SSH matters when cloning first:

```bash
# HTTPS clone
git clone https://github.com/dbirks/techradar.git

# SSH clone
git clone git@github.com:dbirks/techradar.git

cd techradar
gh skill install \
  ./2026/agent-skills/plugins/orbital-briefing/skills \
  --from-local --all \
  --agent github-copilot \
  --scope user
```

GitHub CLI skill installation is currently a public-preview feature and requires a recent GitHub CLI release. Inspect third-party `SKILL.md` files and scripts before installing them.

## Turn the collection into a Claude Code and Copilot marketplace

Both clients can consume the same plugin directory and the same Claude-compatible manifest locations. Use one shared structure instead of maintaining divergent copies:

```text
2026/agent-skills/
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    └── orbital-briefing/
        ├── .claude-plugin/
        │   └── plugin.json
        └── skills/
            └── ...
```

The marketplace manifest points to one or more plugins:

```json
{
  "name": "dbirks-techradar",
  "description": "Tech Radar demo skills that query live public space-data APIs.",
  "owner": {
    "name": "dbirks"
  },
  "plugins": [
    {
      "name": "orbital-briefing",
      "source": "./plugins/orbital-briefing",
      "description": "Agent skills backed by live public space-data APIs."
    }
  ]
}
```

The plugin manifest describes the installable plugin. Both clients discover the conventional `skills/` directory automatically:

```json
{
  "name": "orbital-briefing",
  "description": "Live launch, asteroid, satellite, space-weather, and astronomy tools for agents.",
  "version": "0.1.0",
  "author": {
    "name": "dbirks"
  }
}
```

Install the marketplace from this repository's nested directory while developing locally:

```bash
# Claude Code
claude plugin marketplace add ./2026/agent-skills
claude plugin install orbital-briefing@dbirks-techradar

# GitHub Copilot CLI
copilot plugin marketplace add ./2026/agent-skills
copilot plugin install orbital-briefing@dbirks-techradar
```

Copilot can also install the nested plugin directly from GitHub without a marketplace:

```bash
copilot plugin install \
  dbirks/techradar:2026/agent-skills/plugins/orbital-briefing
```

### Important remote-marketplace caveat

A remote marketplace added as `OWNER/REPO` is expected to have its recognized marketplace manifest at the repository root. Because this collection lives under `2026/agent-skills`, use one of these approaches:

1. Keep it nested and add it from a local checkout.
2. Publish `2026/agent-skills` as a dedicated repository, for example `dbirks/orbital-agent-skills`.
3. Move or mirror the marketplace manifest and plugin directory to the root of `dbirks/techradar`.

For a dedicated repository, both clients can use a short GitHub source:

```bash
claude plugin marketplace add dbirks/orbital-agent-skills
copilot plugin marketplace add dbirks/orbital-agent-skills
```

Or an explicit Git clone URL:

```bash
# HTTPS
claude plugin marketplace add https://github.com/dbirks/orbital-agent-skills.git
copilot plugin marketplace add https://github.com/dbirks/orbital-agent-skills.git

# SSH
claude plugin marketplace add git@github.com:dbirks/orbital-agent-skills.git
copilot plugin marketplace add git@github.com:dbirks/orbital-agent-skills.git
```

A plugin is copied into a client-managed cache, so every file it needs must live inside the plugin directory. Do not make skills depend on files elsewhere in the Tech Radar repository.

## Runtime prerequisites

Each skill needs only its own runtime; none of them share an environment.

| Runtime | Arch Linux package | Verified with |
|---|---|---|
| uv | `extra/uv` | 0.12.0 |
| Bun | `extra/bun` (or AUR `bun-bin`) | 1.3.2 |
| Deno | `extra/deno` | 2.9.4 |
| JBang | AUR `jbang` | 0.141.0 |
| JDK 17+ | `extra/jdk-openjdk` | OpenJDK 17.0.20 |
| .NET 10 SDK | `extra/dotnet-sdk` (or AUR `dotnet-sdk-bin`) | 10.0.110 |

### Bun and a stray parent `node_modules`

Bun walks up the directory tree looking for `node_modules`. If it finds an unrelated one —
a `~/package.json` and `~/node_modules` are enough — it resolves against that directory and
refuses to auto-install the pinned import, failing with
`Cannot find package 'commander@15.0.0'`.

`space_weather.ts` therefore uses this shebang:

```text
#!/usr/bin/env -S bun --install=fallback
```

`--install=fallback` keeps existing `node_modules` resolution but auto-installs anything
missing, so the script works no matter where in the filesystem it is run from.

## Notes on upstream data shapes

These were verified against the live APIs rather than assumed, and a few differ from what the
documentation implies:

- **NOAA planetary K-index** returns an array of named objects (`time_tag`, `Kp`, `a_running`,
  `station_count`). Some other NOAA products use a leading header row with array rows instead,
  so `space_weather.ts` handles both shapes.
- **CelesTrak GP data** has no `OBJECT_TYPE` and no `PERIOD` field. `RecentSatellites.java`
  infers payload/rocket body/debris from the `R/B` and `DEB` naming conventions and derives the
  orbital period as `1440 / MEAN_MOTION` minutes. Both are reported as derived values.
- **Launch Library 2** only returns `vid_urls` and `info_urls` in `mode=detailed`, so
  `launch_watch.py` requests that mode to report a webcast URL.
- **NASA NeoWs** keys its response by date; `asteroid_watch.ts` flattens those into one list.

## Research and data-source notes

- Launch Library 2 is free but currently limits unauthenticated production requests to 15 per hour. Use its development endpoint only during implementation because that endpoint intentionally contains stale, limited data.
- NASA's `DEMO_KEY` works without registration but has low shared limits. Respect `NASA_API_KEY` when it is set.
- NOAA SWPC and CelesTrak examples need no private key.
- The person remembered as the satellite-newsletter author is likely astronomer Jonathan McDowell, author of *Jonathan's Space Report*. It is excellent presentation inspiration, but CelesTrak is the better executable demo source because it exposes structured JSON.

## Additional skill ideas not implemented in the first pass

- `mars-season`: calculate Mars solar longitude and report the current Martian season.
- `iss-pass`: use an observer latitude/longitude to predict visible ISS passes.
- `donki-events`: summarize NASA DONKI solar flares, CMEs, and geomagnetic storms.
- `exoplanet-query`: search the NASA Exoplanet Archive with TAP/ADQL.
- `space-image-search`: query NASA's Image and Video Library and download selected assets.
- `decay-watch`: list CelesTrak objects marked as potential orbital decays.
- `mission-clock`: show countdowns to selected launch or mission milestones.
