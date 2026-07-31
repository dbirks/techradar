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

## Invoking the tools manually

Every tool supports `--help`, returns nonzero on failure, keeps human diagnostics on stderr,
and offers `--json` for agent-safe structured output. Nothing needs to be installed or built
first: each runtime fetches its own dependencies on the first run, so expect a short pause the
first time and near-instant runs afterwards.

All paths below are relative to this directory (`2026/agent-skills`). The examples use the
full path so they can be copied straight into a terminal; `cd` into a skill directory first if
you prefer the shorter `./scripts/...` form the `SKILL.md` files use.

Two invocation styles work for every skill:

- **Direct execution** — the shebang picks the runtime. Requires the executable bit, which is
  already set in this repository.
- **Explicit runtime** — call the runtime yourself. This is the form to use on Windows, where
  shebangs are not honored.

### 1. `launch-watch` — Python via uv

```bash
# direct
./plugins/orbital-briefing/skills/launch-watch/scripts/launch_watch.py --help

# explicit runtime (also the Windows form)
uv run ./plugins/orbital-briefing/skills/launch-watch/scripts/launch_watch.py --help
```

```text
launch_watch.py next  [--location TEXT] [--provider TEXT] [--timezone TEXT] [--json]
launch_watch.py list  [--days 1-365] [--location TEXT] [--provider TEXT]
                      [--limit 1-50] [--all] [--timezone TEXT] [--json]
```

`--location` and `--provider` are case-insensitive substring matches; `--location` matches the
launch site *and* the pad name. Defaults: `--days 30`, `--limit 5`, local timezone.

```bash
S=./plugins/orbital-briefing/skills/launch-watch/scripts/launch_watch.py

$S next                                              # soonest launch anywhere
$S next --provider SpaceX --timezone UTC             # soonest SpaceX launch, in UTC
$S list --days 30 --provider SpaceX --limit 5         # next 5 SpaceX launches
$S list --days 30 --location "Cape Canaveral" --json  # structured, one site
$S list --days 7 --all                               # everything in the next week
```

Only one API request is made per invocation. The unauthenticated endpoint allows about 15
requests per hour, so for repeated local runs use the stale development endpoint:

```bash
LL2_BASE_URL=https://lldev.thespacedevs.com/2.3.0 $S next
```

### 2. `space-weather` — Bun

```bash
# direct
./plugins/orbital-briefing/skills/space-weather/scripts/space_weather.ts --help

# explicit runtime (also the Windows form)
bun --install=fallback ./plugins/orbital-briefing/skills/space-weather/scripts/space_weather.ts --help
```

```text
space_weather.ts alerts  [--limit 1-100] [--scale G|S|R] [--contains TEXT] [--json]
space_weather.ts kp      [--limit 1-100] [--storm-only] [--latest] [--json]
```

Defaults: `--limit 10` for `alerts`, `--limit 12` for `kp`. Both list newest first.

```bash
S=./plugins/orbital-briefing/skills/space-weather/scripts/space_weather.ts

$S alerts --limit 5                        # 5 most recent bulletins
$S alerts --scale G                        # geomagnetic only (S = solar radiation, R = radio)
$S alerts --scale G --contains warning     # narrow to warnings
$S alerts --limit 1 --json                 # full bulletin text lives in --json
$S kp --latest                             # single most recent Kp reading
$S kp --limit 8                            # last 8 three-hour readings
$S kp --storm-only --json                  # Kp >= 5 only; exit 3 on a calm day
```

Human output shows only the bulletin headline so the terminal stays readable. The complete
multi-line NOAA message is included in `--json` under `message`.

### 3. `asteroid-watch` — Deno

```bash
# direct
./plugins/orbital-briefing/skills/asteroid-watch/scripts/asteroid_watch.ts --help

# explicit runtime (also the Windows form)
deno run --allow-net=api.nasa.gov --allow-env=NASA_API_KEY \
  ./plugins/orbital-briefing/skills/asteroid-watch/scripts/asteroid_watch.ts --help
```

The explicit form must repeat the permissions from the shebang; Deno denies everything else.

```text
asteroid_watch.ts today                      [--hazardous] [--limit 1-100]
                                             [--sort distance|size|speed] [--json]
asteroid_watch.ts range --start YYYY-MM-DD --end YYYY-MM-DD
                                             [--hazardous] [--limit 1-100]
                                             [--sort distance|size|speed] [--json]
```

Defaults: `--limit 10` for `today`, `--limit 20` for `range`, `--sort distance`. Sorting by
`distance` puts the closest approach first; `size` and `speed` put the largest and fastest
first. A `range` window may span at most 7 days.

```bash
S=./plugins/orbital-briefing/skills/asteroid-watch/scripts/asteroid_watch.ts

$S today                                                  # today's approaches, closest first
$S today --sort size --limit 5                            # 5 biggest instead
$S today --hazardous                                      # exit 3 when none qualify
$S range --start 2026-08-01 --end 2026-08-07 --limit 10
$S range --start 2026-08-01 --end 2026-08-07 --hazardous --json
```

"Potentially hazardous" is NASA's catalog classification based on size and orbit geometry. It
is not a prediction of impact, and the JSON output carries that caveat in a `note` field.

### 4. `recent-satellites` — Java via JBang

```bash
# direct
./plugins/orbital-briefing/skills/recent-satellites/scripts/RecentSatellites.java --help

# explicit runtime (also the Windows form)
jbang ./plugins/orbital-briefing/skills/recent-satellites/scripts/RecentSatellites.java --help
```

The very first run resolves Maven dependencies and compiles, which takes a few seconds. JBang
caches the result, so later runs start quickly.

```text
RecentSatellites.java recent        [--limit 1-100] [--name TEXT]
                                    [--inclination-min DEGREES] [--json]
RecentSatellites.java find QUERY    [--limit 1-100] [--json]
```

`QUERY` is positional and required. It searches object name, international designator, and
NORAD catalog ID. Default `--limit 20` for both.

```bash
S=./plugins/orbital-briefing/skills/recent-satellites/scripts/RecentSatellites.java

$S recent --limit 15                   # most recently cataloged objects
$S recent --inclination-min 80         # near-polar and sun-synchronous orbits
$S recent --name starlink --limit 5
$S find starlink --json
$S find 2026-171                       # everything from one launch
```

Covers launches from the last 30 days. One launch produces many catalog entries, so expect
payloads, rocket bodies, and debris from the same international designator.

### 5. `astro-photo` — .NET 10 file-based C#

```bash
# direct — no separator needed
./plugins/orbital-briefing/skills/astro-photo/scripts/AstroPhoto.cs today --help

# explicit runtime (also the Windows form) — `--` IS required here
dotnet run ./plugins/orbital-briefing/skills/astro-photo/scripts/AstroPhoto.cs -- today --help
```

The `--` asymmetry is worth understanding, because the failure is confusing either way. The
dotnet CLI claims `--help` and `-h` for itself, so something has to tell it to forward
arguments to the app. This script's shebang does that itself:

```text
#!/usr/bin/env -S dotnet --
```

`-S` lets `env` split the line into separate arguments so the `--` can live in the shebang,
which is the form Microsoft's file-based apps documentation recommends. Consequences:

- **Direct execution:** do *not* add `--`. The shebang already supplied it, and a second one
  makes System.CommandLine treat the rest as literals, giving `'today' was not matched`.
- **Explicit `dotnet run`:** you *must* add `--`, since no shebang is involved. Without it,
  `--help` prints `dotnet run` usage instead of the tool's.

```text
AstroPhoto.cs today                   [--hd] [--json]
AstroPhoto.cs date --date YYYY-MM-DD  [--hd] [--json]
```

`--date` is required for the `date` command. The archive starts 1995-06-16; earlier or future
dates are rejected before any network call.

```bash
S=./plugins/orbital-briefing/skills/astro-photo/scripts/AstroPhoto.cs

$S today                                 # today's image and full explanation
$S today --hd                            # prefer the high-resolution URL
$S today --json
$S date --date 2025-12-25 --json
$S date --date 2026-07-13 --json         # a video entry
```

`--hd` applies only to image entries. Video entries return the video URL with `media_type` set
to `video`, a null `hdurl`, and `--hd` ignored rather than erroring.

### Quick check that all five still work

```bash
./plugins/orbital-briefing/skills/launch-watch/scripts/launch_watch.py next
./plugins/orbital-briefing/skills/space-weather/scripts/space_weather.ts kp --latest
./plugins/orbital-briefing/skills/asteroid-watch/scripts/asteroid_watch.ts today --limit 3
./plugins/orbital-briefing/skills/recent-satellites/scripts/RecentSatellites.java recent --limit 3
./plugins/orbital-briefing/skills/astro-photo/scripts/AstroPhoto.cs today
```

If one of them exits `4`, the upstream API is rate-limiting or unreachable rather than the
script being broken. See the exit-code table below.

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

`NASA_API_KEY` is **required** by `asteroid-watch` and `astro-photo`. Without it they exit `5`
with instructions rather than falling back to NASA's shared `DEMO_KEY`. That fallback was
removed deliberately: `DEMO_KEY` is limited far more tightly than the docs imply, and silently
degrading to it turns a missing-configuration problem into what looks like a broken tool.
Measured from the API's own response headers:

| Key | `x-ratelimit-limit` | Recovery after exhaustion |
|---|---|---|
| `DEMO_KEY` | 10 (shared per IP) | `retry-after` observed at over 8 hours |
| Personal key | 4000 | one hour |

`DEMO_KEY` is the literal string `DEMO_KEY`: NASA's public, unauthenticated key, published in
their docs so an endpoint can be tried from a browser. It is shared by everyone and counted per
IP address, so its budget is often already spent before you make a single call.

Get a free key instead — the form at https://api.nasa.gov/ asks only for a name, email, and
accepting the terms, and returns the key immediately.

```bash
export NASA_API_KEY=your-key-here
```

Because zsh sources `~/.zshrc` only for interactive shells, an export placed there is not
visible to non-interactive tooling. Use `~/.zshenv` if something scripted needs to see it.

Check which limit is in effect at any time:

```bash
curl -s -D - -o /dev/null "https://api.nasa.gov/planetary/apod?api_key=${NASA_API_KEY:-DEMO_KEY}" \
  | grep -i ratelimit
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
