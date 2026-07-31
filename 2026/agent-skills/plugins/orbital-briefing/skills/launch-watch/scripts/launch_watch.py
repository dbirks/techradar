#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx>=0.28,<1",
#   "typer>=0.27,<1",
# ]
# ///
"""Upcoming orbital launches, from The Space Devs Launch Library 2."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, NoReturn
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
import typer

USER_AGENT = "orbital-briefing/launch-watch (+https://github.com/dbirks/techradar)"
PROD_BASE_URL = "https://ll.thespacedevs.com/2.3.0"
BASE_URL = os.environ.get("LL2_BASE_URL", PROD_BASE_URL).rstrip("/")

# The API's own ceiling for a single page. Never request more than this.
MAX_PAGE_SIZE = 100
# Hard cap on rows we will ever print, so an agent's context cannot be flooded.
MAX_RESULTS = 50
TIMEOUT_SECONDS = 30.0

# Exit codes
EXIT_NO_MATCH = 3
EXIT_API_ERROR = 4
EXIT_BAD_INPUT = 5

# `ZoneInfo` and `timezone` share only the tzinfo protocol; alias it for clarity.
tzinfo_t = Any

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help=(
        "Look up upcoming rocket launches from Launch Library 2.\n\n"
        "Set LL2_BASE_URL=https://lldev.thespacedevs.com/2.3.0 to use the "
        "development endpoint during repeated local runs. That endpoint holds "
        "intentionally stale, limited data and must not be used for real answers."
    ),
)


def die(message: str, code: int) -> NoReturn:
    """Report a human-readable failure on stderr and exit nonzero."""
    print(f"error: {message}", file=sys.stderr)
    raise typer.Exit(code)


def resolve_timezone(name: str | None) -> tzinfo_t:
    """Resolve a timezone name, falling back to local time and then UTC."""
    if name:
        try:
            return ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            die(f"unknown timezone {name!r}; try a name like 'America/Indiana/Indianapolis'", EXIT_BAD_INPUT)
    local = datetime.now().astimezone().tzinfo
    return local or timezone.utc


def fetch_upcoming(window_end: datetime, page_size: int) -> dict[str, Any]:
    """Make exactly one request for upcoming launches inside the window."""
    params = {
        "limit": min(page_size, MAX_PAGE_SIZE),
        "mode": "detailed",
        "ordering": "net",
        "net__lte": window_end.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        response = httpx.get(
            f"{BASE_URL}/launches/upcoming/",
            params=params,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
            follow_redirects=True,
        )
    except httpx.TimeoutException:
        die(f"request to {BASE_URL} timed out after {TIMEOUT_SECONDS:.0f}s", EXIT_API_ERROR)
    except httpx.HTTPError as exc:
        die(f"could not reach {BASE_URL}: {exc}", EXIT_API_ERROR)

    if response.status_code == 429:
        die(
            "Launch Library 2 rate limit reached (about 15 requests per hour when "
            "unauthenticated). Wait and retry, or set LL2_BASE_URL to the dev endpoint.",
            EXIT_API_ERROR,
        )
    if response.status_code >= 400:
        die(f"Launch Library 2 returned HTTP {response.status_code}", EXIT_API_ERROR)

    try:
        return response.json()
    except ValueError:
        die("Launch Library 2 returned a response that is not valid JSON", EXIT_API_ERROR)


def first_url(entries: Any) -> str | None:
    """Pull the first usable URL out of an LL2 url-list field."""
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if isinstance(entry, dict) and entry.get("url"):
            return str(entry["url"])
    return None


def normalize(raw: dict[str, Any], tz: tzinfo_t) -> dict[str, Any]:
    """Flatten one LL2 launch record into the fields this tool reports."""
    pad = raw.get("pad") or {}
    location = pad.get("location") or {}
    provider = raw.get("launch_service_provider") or {}
    status = raw.get("status") or {}
    mission = raw.get("mission") or {}

    net_raw = raw.get("net")
    net_local = None
    if net_raw:
        try:
            parsed = datetime.fromisoformat(str(net_raw).replace("Z", "+00:00"))
            net_local = parsed.astimezone(tz)
        except ValueError:
            net_local = None

    return {
        "name": raw.get("name"),
        "net_utc": net_raw,
        "net_local": net_local.isoformat() if net_local else None,
        "net_precision": (raw.get("net_precision") or {}).get("name"),
        "status": status.get("name"),
        "status_description": status.get("description"),
        "provider": provider.get("name"),
        "pad": pad.get("name"),
        "location": location.get("name"),
        "mission": mission.get("name"),
        "mission_type": mission.get("type"),
        "webcast_url": first_url(raw.get("vid_urls")),
        "info_url": first_url(raw.get("info_urls")),
        "source_url": raw.get("url"),
        "last_updated": raw.get("last_updated"),
    }


def matches(item: dict[str, Any], location: str | None, provider: str | None) -> bool:
    """Case-insensitive substring filtering over location and provider."""
    if location:
        haystack = " ".join(
            str(item.get(key) or "") for key in ("location", "pad")
        ).lower()
        if location.lower() not in haystack:
            return False
    if provider and provider.lower() not in str(item.get("provider") or "").lower():
        return False
    return True


def collect(
    days: int,
    location: str | None,
    provider: str | None,
    tz: tzinfo_t,
) -> tuple[list[dict[str, Any]], str]:
    """Fetch once, then filter client-side. Returns (matches, retrieved_at)."""
    window_end = datetime.now(timezone.utc) + timedelta(days=days)
    payload = fetch_upcoming(window_end, MAX_PAGE_SIZE)
    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    results = payload.get("results")
    if not isinstance(results, list):
        die("Launch Library 2 response did not contain a results list", EXIT_API_ERROR)

    items = [normalize(raw, tz) for raw in results if isinstance(raw, dict)]
    return [item for item in items if matches(item, location, provider)], retrieved_at


def emit_json(payload: dict[str, Any]) -> None:
    """Machine-readable output goes to stdout and nowhere else."""
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def describe(item: dict[str, Any]) -> str:
    """Render one launch as an indented human-readable block."""
    when = item["net_local"] or item["net_utc"] or "unknown time"
    lines = [f"{item['name'] or 'Unnamed launch'}", f"  when:     {when}"]
    if item["net_precision"]:
        lines.append(f"  accuracy: {item['net_precision']}")
    for label, key in (
        ("status", "status"),
        ("provider", "provider"),
        ("pad", "pad"),
        ("location", "location"),
        ("mission", "mission"),
        ("type", "mission_type"),
        ("webcast", "webcast_url"),
        ("source", "source_url"),
    ):
        if item.get(key):
            lines.append(f"  {label + ':':<9} {item[key]}")
    return "\n".join(lines)


def report(
    items: list[dict[str, Any]],
    retrieved_at: str,
    as_json: bool,
    empty_message: str,
) -> None:
    """Shared output path for both subcommands."""
    if not items:
        if as_json:
            emit_json({"retrieved_at": retrieved_at, "source": BASE_URL, "count": 0, "launches": []})
        print(empty_message, file=sys.stderr)
        raise typer.Exit(EXIT_NO_MATCH)

    if as_json:
        emit_json(
            {
                "retrieved_at": retrieved_at,
                "source": BASE_URL,
                "count": len(items),
                "launches": items,
            }
        )
        return

    print("\n\n".join(describe(item) for item in items))
    print(f"\nRetrieved {retrieved_at} from {BASE_URL}. Launch schedules change frequently.")


@app.command("next")
def next_launch(
    location: Annotated[str | None, typer.Option("--location", help="Case-insensitive substring of the launch location or pad.")] = None,
    provider: Annotated[str | None, typer.Option("--provider", help="Case-insensitive substring of the launch service provider.")] = None,
    timezone_name: Annotated[str | None, typer.Option("--timezone", help="IANA timezone for displayed times. Defaults to local time.")] = None,
    as_json: Annotated[bool, typer.Option("--json", help="Emit structured JSON on stdout.")] = False,
) -> None:
    """Show the single soonest upcoming launch that matches the filters."""
    tz = resolve_timezone(timezone_name)
    items, retrieved_at = collect(365, location, provider, tz)
    report(
        items[:1],
        retrieved_at,
        as_json,
        "No upcoming launch matched those filters.",
    )


@app.command("list")
def list_launches(
    days: Annotated[int, typer.Option("--days", min=1, max=365, help="Size of the forward window in days.")] = 30,
    location: Annotated[str | None, typer.Option("--location", help="Case-insensitive substring of the launch location or pad.")] = None,
    provider: Annotated[str | None, typer.Option("--provider", help="Case-insensitive substring of the launch service provider.")] = None,
    limit: Annotated[int, typer.Option("--limit", min=1, max=MAX_RESULTS, help="Maximum launches to show.")] = 5,
    show_all: Annotated[bool, typer.Option("--all", help=f"Show every match in the window, still capped at {MAX_RESULTS}.")] = False,
    timezone_name: Annotated[str | None, typer.Option("--timezone", help="IANA timezone for displayed times. Defaults to local time.")] = None,
    as_json: Annotated[bool, typer.Option("--json", help="Emit structured JSON on stdout.")] = False,
) -> None:
    """Show a bounded schedule of upcoming launches."""
    tz = resolve_timezone(timezone_name)
    items, retrieved_at = collect(days, location, provider, tz)
    cutoff = MAX_RESULTS if show_all else limit
    report(
        items[:cutoff],
        retrieved_at,
        as_json,
        f"No launch matched those filters in the next {days} day(s).",
    )


if __name__ == "__main__":
    app()
