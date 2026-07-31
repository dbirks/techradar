#!/usr/bin/env -S deno run --allow-net=api.nasa.gov --allow-env=NASA_API_KEY
// Near-Earth asteroid close approaches, from NASA's NeoWs feed.
//
// The shebang grants only the network host and environment variable this tool
// actually needs; Deno denies everything else by default.
import { Command } from "jsr:@cliffy/command@1.2.1";

const USER_AGENT =
  "orbital-briefing/asteroid-watch (+https://github.com/dbirks/techradar)";
const FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed";

const TIMEOUT_MS = 30_000;
// Hard ceiling on printed rows so an agent's context cannot be flooded.
const MAX_ROWS = 100;
// NeoWs allows at most a seven-day feed window.
const MAX_RANGE_DAYS = 7;

const EXIT_NO_MATCH = 3;
const EXIT_API_ERROR = 4;
const EXIT_BAD_INPUT = 5;

type SortKey = "distance" | "size" | "speed";

interface Approach {
  name: string;
  nasa_jpl_url: string | null;
  neo_reference_id: string | null;
  is_potentially_hazardous: boolean;
  diameter_min_m: number | null;
  diameter_max_m: number | null;
  close_approach_date: string | null;
  close_approach_full: string | null;
  relative_speed_km_s: number | null;
  miss_distance_km: number | null;
  orbiting_body: string | null;
}

function die(message: string, code: number): never {
  console.error(`error: ${message}`);
  Deno.exit(code);
}

/** Validate a strict YYYY-MM-DD calendar date. */
function parseIsoDate(raw: string, label: string): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    die(`${label} must be formatted YYYY-MM-DD (got ${raw})`, EXIT_BAD_INPUT);
  }
  const parsed = new Date(`${raw}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== raw) {
    die(`${label} is not a real calendar date (got ${raw})`, EXIT_BAD_INPUT);
  }
  return raw;
}

function todayUtc(): string {
  return new Date().toISOString().slice(0, 10);
}

function daysBetween(start: string, end: string): number {
  const ms = Date.parse(`${end}T00:00:00Z`) - Date.parse(`${start}T00:00:00Z`);
  return Math.round(ms / 86_400_000);
}

/**
 * Read the required NASA API key. There is deliberately no fallback to NASA's
 * shared DEMO_KEY: it allows only about 10 requests per IP address and then
 * blocks for hours, which fails in a way that looks like a broken tool.
 */
function apiKey(): string {
  const key = Deno.env.get("NASA_API_KEY")?.trim();
  if (!key) {
    die(
      "NASA_API_KEY is not set. Get a free key at https://api.nasa.gov/ " +
        "(name, email, accept terms) and export it:\n" +
        "       export NASA_API_KEY=your-key-here",
      EXIT_BAD_INPUT,
    );
  }
  return key;
}

async function fetchFeed(start: string, end: string): Promise<Record<string, unknown>> {
  const url = new URL(FEED_URL);
  url.searchParams.set("start_date", start);
  url.searchParams.set("end_date", end);
  url.searchParams.set("api_key", apiKey());

  let response: Response;
  try {
    response = await fetch(url, {
      headers: { "User-Agent": USER_AGENT, Accept: "application/json" },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (error) {
    if (error instanceof Error && error.name === "TimeoutError") {
      die(`request to api.nasa.gov timed out after ${TIMEOUT_MS / 1000}s`, EXIT_API_ERROR);
    }
    die(`could not reach api.nasa.gov: ${(error as Error).message}`, EXIT_API_ERROR);
  }

  if (response.status === 429) {
    die(
      "NASA API rate limit reached for this key (4000 requests per hour). " +
        "Check the x-ratelimit-remaining response header and retry later.",
      EXIT_API_ERROR,
    );
  }
  if (!response.ok) {
    die(`NASA NeoWs returned HTTP ${response.status}`, EXIT_API_ERROR);
  }

  try {
    return await response.json();
  } catch {
    die("NASA NeoWs returned a response that is not valid JSON", EXIT_API_ERROR);
  }
}

const num = (value: unknown): number | null => {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

/** Flatten NeoWs' date-keyed response into one list of approaches. */
function normalize(payload: Record<string, unknown>): Approach[] {
  const byDate = payload.near_earth_objects;
  if (typeof byDate !== "object" || byDate === null) {
    die("NASA NeoWs response did not contain near_earth_objects", EXIT_API_ERROR);
  }

  const out: Approach[] = [];
  for (const objects of Object.values(byDate as Record<string, unknown>)) {
    if (!Array.isArray(objects)) continue;
    for (const raw of objects) {
      if (typeof raw !== "object" || raw === null) continue;
      const obj = raw as Record<string, any>;
      const meters = obj.estimated_diameter?.meters ?? {};
      const approach = obj.close_approach_data?.[0] ?? {};
      out.push({
        name: String(obj.name ?? "unknown object"),
        nasa_jpl_url: obj.nasa_jpl_url ?? null,
        neo_reference_id: obj.neo_reference_id ?? null,
        is_potentially_hazardous: Boolean(obj.is_potentially_hazardous_asteroid),
        diameter_min_m: num(meters.estimated_diameter_min),
        diameter_max_m: num(meters.estimated_diameter_max),
        close_approach_date: approach.close_approach_date ?? null,
        close_approach_full: approach.close_approach_date_full ?? null,
        relative_speed_km_s: num(approach.relative_velocity?.kilometers_per_second),
        miss_distance_km: num(approach.miss_distance?.kilometers),
        orbiting_body: approach.orbiting_body ?? null,
      });
    }
  }
  return out;
}

/** Sort nulls last so incomplete records never lead the list. */
function sortApproaches(items: Approach[], key: SortKey): Approach[] {
  const value = (item: Approach): number | null => {
    if (key === "distance") return item.miss_distance_km;
    if (key === "speed") return item.relative_speed_km_s;
    return item.diameter_max_m;
  };
  // Distance ascends (closest first); size and speed descend (largest first).
  const descending = key !== "distance";
  return [...items].sort((a, b) => {
    const av = value(a);
    const bv = value(b);
    if (av === null && bv === null) return 0;
    if (av === null) return 1;
    if (bv === null) return -1;
    return descending ? bv - av : av - bv;
  });
}

function describe(item: Approach): string {
  const flag = item.is_potentially_hazardous ? "  [potentially hazardous]" : "";
  const lines = [`${item.name}${flag}`];
  if (item.close_approach_full || item.close_approach_date) {
    lines.push(`  approach: ${item.close_approach_full ?? item.close_approach_date}`);
  }
  if (item.diameter_min_m !== null && item.diameter_max_m !== null) {
    lines.push(
      `  diameter: ${item.diameter_min_m.toFixed(0)}-${item.diameter_max_m.toFixed(0)} m (estimated)`,
    );
  }
  if (item.relative_speed_km_s !== null) {
    lines.push(`  speed:    ${item.relative_speed_km_s.toFixed(2)} km/s`);
  }
  if (item.miss_distance_km !== null) {
    lines.push(`  miss:     ${Math.round(item.miss_distance_km).toLocaleString("en-US")} km`);
  }
  if (item.orbiting_body) lines.push(`  body:     ${item.orbiting_body}`);
  if (item.nasa_jpl_url) lines.push(`  source:   ${item.nasa_jpl_url}`);
  return lines.join("\n");
}

interface RunOptions {
  start: string;
  end: string;
  hazardous: boolean;
  limit: number;
  sort: SortKey;
  json: boolean;
}

async function run(options: RunOptions): Promise<void> {
  const payload = await fetchFeed(options.start, options.end);
  const retrievedAt = new Date().toISOString();

  let items = normalize(payload);
  if (options.hazardous) {
    items = items.filter((item) => item.is_potentially_hazardous);
  }
  const shown = sortApproaches(items, options.sort).slice(0, options.limit);

  if (options.json) {
    console.log(
      JSON.stringify(
        {
          retrieved_at: retrievedAt,
          source: FEED_URL,
          start_date: options.start,
          end_date: options.end,
          sort: options.sort,
          hazardous_only: options.hazardous,
          note:
            "'potentially hazardous' is NASA's catalog classification based on " +
            "size and orbit geometry. It is not a prediction of impact.",
          count: shown.length,
          approaches: shown,
        },
        null,
        2,
      ),
    );
  }

  if (shown.length === 0) {
    console.error(
      options.hazardous
        ? `No potentially hazardous object approached between ${options.start} and ${options.end}.`
        : `No close approaches were returned between ${options.start} and ${options.end}.`,
    );
    Deno.exit(EXIT_NO_MATCH);
  }
  if (options.json) return;

  console.log(shown.map(describe).join("\n\n"));
  console.log(
    `\nRetrieved ${retrievedAt} from NASA NeoWs (${options.start} to ${options.end}).`,
  );
  console.log(
    "'Potentially hazardous' is NASA's catalog classification from size and orbit,",
  );
  console.log("not a prediction of impact.");
}

/** Shared bounded-integer parsing for --limit. */
function checkLimit(value: number): number {
  if (!Number.isInteger(value) || value < 1 || value > MAX_ROWS) {
    die(`--limit must be an integer between 1 and ${MAX_ROWS}`, EXIT_BAD_INPUT);
  }
  return value;
}

const SORT_CHOICES: SortKey[] = ["distance", "size", "speed"];

await new Command()
  .name("asteroid_watch.ts")
  .version("0.1.0")
  .description(
    "Near-Earth asteroid close approaches from NASA NeoWs. " +
      "Requires NASA_API_KEY; get a free key at https://api.nasa.gov/.",
  )
  .action(function () {
    this.showHelp();
    Deno.exit(0);
  })
  .command("today", "Show close approaches for today (UTC).")
  .option("--hazardous", "Only show objects NASA classifies as potentially hazardous.")
  .option("--limit <n:integer>", "Maximum approaches to show.", { default: 10 })
  .option("--sort <key:string>", `Sort order: ${SORT_CHOICES.join(", ")}.`, {
    default: "distance",
  })
  .option("--json", "Emit structured JSON on stdout.")
  .action(async (options) => {
    const sort = String(options.sort) as SortKey;
    if (!SORT_CHOICES.includes(sort)) {
      die(`--sort must be one of ${SORT_CHOICES.join(", ")}`, EXIT_BAD_INPUT);
    }
    const today = todayUtc();
    await run({
      start: today,
      end: today,
      hazardous: Boolean(options.hazardous),
      limit: checkLimit(Number(options.limit)),
      sort,
      json: Boolean(options.json),
    });
  })
  .command("range", "Show close approaches across a date window of up to 7 days.")
  .option("--start <date:string>", "First date, YYYY-MM-DD.", { required: true })
  .option("--end <date:string>", "Last date, YYYY-MM-DD.", { required: true })
  .option("--hazardous", "Only show objects NASA classifies as potentially hazardous.")
  .option("--limit <n:integer>", "Maximum approaches to show.", { default: 20 })
  .option("--sort <key:string>", `Sort order: ${SORT_CHOICES.join(", ")}.`, {
    default: "distance",
  })
  .option("--json", "Emit structured JSON on stdout.")
  .action(async (options) => {
    const sort = String(options.sort) as SortKey;
    if (!SORT_CHOICES.includes(sort)) {
      die(`--sort must be one of ${SORT_CHOICES.join(", ")}`, EXIT_BAD_INPUT);
    }
    const start = parseIsoDate(String(options.start), "--start");
    const end = parseIsoDate(String(options.end), "--end");

    const span = daysBetween(start, end);
    if (span < 0) {
      die(`--end (${end}) is before --start (${start})`, EXIT_BAD_INPUT);
    }
    if (span + 1 > MAX_RANGE_DAYS) {
      die(
        `the window ${start} to ${end} spans ${span + 1} days; NeoWs allows at most ${MAX_RANGE_DAYS}`,
        EXIT_BAD_INPUT,
      );
    }

    await run({
      start,
      end,
      hazardous: Boolean(options.hazardous),
      limit: checkLimit(Number(options.limit)),
      sort,
      json: Boolean(options.json),
    });
  })
  .parse(Deno.args);
