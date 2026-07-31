---
description: Add the Orbital Briefing agent-skills marketplace from this repo and install the plugin.
argument-hint: "[user|project|local]  (installation scope, default: user)"
allowed-tools: Bash(claude plugin marketplace:*), Bash(claude plugin install:*), Bash(claude plugin list:*), Bash(claude plugin validate:*), Bash(git rev-parse:*), Bash(ls:*), Bash(printenv NASA_API_KEY), Read
---

Install the **Orbital Briefing** skill collection that lives in this repository at
`2026/agent-skills`, so its five skills become available in this Claude Code session.

Scope requested: `$1` — if empty, use `user`.

## Why this is added from a local path

A remote marketplace referenced as `OWNER/REPO` is expected to have its
`.claude-plugin/marketplace.json` at the **repository root**. This collection deliberately lives
in a nested directory (`2026/agent-skills`), so it must be added from a local checkout by path.
Do not try `claude plugin marketplace add dbirks/techradar` — it will not find the manifest.

## Steps

1. Resolve the repository root so this works from any subdirectory:

   ```bash
   ROOT=$(git rev-parse --show-toplevel)
   ls "$ROOT/2026/agent-skills/.claude-plugin/marketplace.json"
   ```

   If that file is missing, stop and report it rather than guessing at another path.

2. Validate the manifests before registering anything:

   ```bash
   claude plugin validate "$ROOT/2026/agent-skills"
   ```

3. Add the marketplace. The manifest declares its name as `dbirks-techradar`:

   ```bash
   claude plugin marketplace add "$ROOT/2026/agent-skills"
   ```

   If it reports that the marketplace already exists, that is fine — refresh it instead:

   ```bash
   claude plugin marketplace update dbirks-techradar
   ```

4. Install the plugin, using the requested scope (default `user`):

   ```bash
   claude plugin install orbital-briefing@dbirks-techradar --scope user
   ```

5. Confirm registration and report what was found:

   ```bash
   claude plugin marketplace list
   claude plugin list
   ```

   All five skills should be discoverable: `launch-watch`, `space-weather`, `asteroid-watch`,
   `recent-satellites`, `astro-photo`.

6. Check the one piece of required configuration and tell the user plainly whether it is present:

   ```bash
   printenv NASA_API_KEY >/dev/null && echo "NASA_API_KEY is set" || echo "NASA_API_KEY is NOT set"
   ```

   `asteroid-watch` and `astro-photo` **require** it and exit `5` without it — there is no
   `DEMO_KEY` fallback. A free key comes from https://api.nasa.gov/ (name, email, accept terms).
   Note that an `export` in `~/.zshrc` is only visible to interactive shells; `~/.zshenv` covers
   scripted use too.

## Runtimes each skill needs

Report any that are missing rather than assuming they are installed. On Arch Linux:

| Skill | Needs | Package |
|---|---|---|
| `launch-watch` | uv | `extra/uv` |
| `space-weather` | Bun | `extra/bun` or AUR `bun-bin` |
| `asteroid-watch` | Deno | `extra/deno` |
| `recent-satellites` | JBang + JDK 17+ | AUR `jbang`, `extra/jdk-openjdk` |
| `astro-photo` | .NET 10 SDK | `extra/dotnet-sdk` |

## To undo

```bash
claude plugin uninstall orbital-briefing
claude plugin marketplace remove dbirks-techradar
```

## Reporting

Finish with a short summary: which marketplace was added, which skills are now available, the
scope used, and anything the user still needs to do (missing runtime, missing `NASA_API_KEY`).
Do not print the value of `NASA_API_KEY` — only whether it is set.
