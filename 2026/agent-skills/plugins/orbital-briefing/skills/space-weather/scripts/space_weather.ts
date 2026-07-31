#!/usr/bin/env -S bun --install=fallback
// NOAA SWPC space-weather alerts and planetary K-index observations.
//
// Bun installs the version-pinned import below into its global cache on first
// run, so this file needs no package.json, lockfile, or install step.
//
// `--install=fallback` keeps that true even when an unrelated node_modules
// exists in a parent directory (a stray ~/package.json is enough). Without it
// Bun resolves against that directory and refuses to auto-install.
import { Command, Option } from "commander@15.0.0";

const USER_AGENT =
  "orbital-briefing/space-weather (+https://github.com/dbirks/techradar)";
const ALERTS_URL = "https://services.swpc.noaa.gov/products/alerts.json";
const KP_URL =
  "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json";

const TIMEOUT_MS = 30_000;
// Hard ceiling on printed rows so an agent's context cannot be flooded.
const MAX_ROWS = 100;
// NOAA G1 begins at Kp 5.
const STORM_THRESHOLD = 5;

const EXIT_NO_MATCH = 3;
const EXIT_API_ERROR = 4;
const EXIT_BAD_INPUT = 5;

function die(message: string, code: number): never {
  console.error(`error: ${message}`);
  process.exit(code);
}

/** Fetch JSON with a timeout, failing with a useful nonzero exit code. */
async function fetchJson(url: string): Promise<unknown> {
  try {
    const response = await fetch(url, {
      headers: { "User-Agent": USER_AGENT, Accept: "application/json" },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    if (!response.ok) {
      die(`NOAA SWPC returned HTTP ${response.status} for ${url}`, EXIT_API_ERROR);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof Error && error.name === "TimeoutError") {
      die(`request to ${url} timed out after ${TIMEOUT_MS / 1000}s`, EXIT_API_ERROR);
    }
    if (error instanceof SyntaxError) {
      die(`NOAA SWPC returned a response that is not valid JSON`, EXIT_API_ERROR);
    }
    die(`could not reach ${url}: ${(error as Error).message}`, EXIT_API_ERROR);
  }
}

/** Parse a bounded positive integer option. */
function parseLimit(raw: string, name: string): number {
  const value = Number(raw);
  if (!Number.isInteger(value) || value < 1 || value > MAX_ROWS) {
    die(`${name} must be an integer between 1 and ${MAX_ROWS}`, EXIT_BAD_INPUT);
  }
  return value;
}

function emitJson(payload: unknown): void {
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
}

const retrievedAt = (): string => new Date().toISOString();

// ---------------------------------------------------------------- alerts ----

interface RawAlert {
  product_id?: string;
  issue_datetime?: string;
  message?: string;
}

interface Alert {
  product_id: string | null;
  issue_datetime: string | null;
  headline: string | null;
  scale: string | null;
  message: string;
}

/**
 * NOAA bulletins are multi-line text. Pull out the most useful single line so
 * human output stays readable; `--json` keeps the full message.
 */
function summarize(message: string): string | null {
  const lines = message
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const keyed = lines.find((line) =>
    /^(ALERT|WARNING|WATCH|SUMMARY|EXTENDED WARNING|CANCEL WARNING):/i.test(line),
  );
  if (keyed) return keyed;
  return lines.find((line) => !/^(Space Weather Message Code|Serial Number|Issue Time)/i.test(line)) ?? null;
}

/**
 * NOAA encodes the affected scale in the message body, e.g. "NOAA Scale: G2".
 * Fall back to the leading letter of a "Kp"/"R"/"S" style notice.
 */
function detectScale(message: string): string | null {
  const explicit = message.match(/NOAA\s+Scale:\s*([GSR])\s*\d/i);
  if (explicit) return explicit[1].toUpperCase();
  const alt = message.match(/\b([GSR])[1-5]\b/);
  return alt ? alt[1].toUpperCase() : null;
}

function normalizeAlert(raw: RawAlert): Alert {
  const message = String(raw.message ?? "");
  return {
    product_id: raw.product_id ?? null,
    issue_datetime: raw.issue_datetime ?? null,
    headline: summarize(message),
    scale: detectScale(message),
    message,
  };
}

async function runAlerts(options: {
  limit: number;
  scale?: string;
  contains?: string;
  json?: boolean;
}): Promise<void> {
  const payload = await fetchJson(ALERTS_URL);
  if (!Array.isArray(payload)) {
    die("NOAA alerts feed was not a JSON array", EXIT_API_ERROR);
  }

  let alerts = payload
    .filter((row): row is RawAlert => typeof row === "object" && row !== null)
    .map(normalizeAlert);

  // Newest first: the feed is oldest-first.
  alerts.sort((a, b) =>
    String(b.issue_datetime ?? "").localeCompare(String(a.issue_datetime ?? "")),
  );

  if (options.scale) {
    const wanted = options.scale.toUpperCase();
    alerts = alerts.filter((alert) => alert.scale === wanted);
  }
  if (options.contains) {
    const needle = options.contains.toLowerCase();
    alerts = alerts.filter((alert) => alert.message.toLowerCase().includes(needle));
  }

  const shown = alerts.slice(0, options.limit);

  if (options.json) {
    emitJson({
      retrieved_at: retrievedAt(),
      source: ALERTS_URL,
      count: shown.length,
      alerts: shown,
    });
  }

  if (shown.length === 0) {
    console.error("No space-weather alert matched those filters.");
    process.exit(EXIT_NO_MATCH);
  }
  if (options.json) return;

  for (const alert of shown) {
    const scale = alert.scale ? ` [${alert.scale}]` : "";
    console.log(`${alert.issue_datetime ?? "unknown time"}${scale}`);
    console.log(`  ${alert.headline ?? "(no summary line)"}`);
    if (alert.product_id) console.log(`  product: ${alert.product_id}`);
    console.log();
  }
  console.log(
    `Retrieved ${retrievedAt()} from ${ALERTS_URL}. Use --json for full bulletin text.`,
  );
}

// -------------------------------------------------------------------- kp ----

interface KpReading {
  time_tag: string | null;
  kp: number | null;
  a_running: number | null;
  station_count: number | null;
  storm: boolean;
}

/**
 * This feed currently returns an array of named objects, but several NOAA
 * products use a leading header row with array rows instead. Handle both.
 */
function normalizeKpFeed(payload: unknown): KpReading[] {
  if (!Array.isArray(payload) || payload.length === 0) {
    die("NOAA planetary K-index feed was empty or not a JSON array", EXIT_API_ERROR);
  }

  let rows: Record<string, unknown>[];

  if (Array.isArray(payload[0])) {
    // Header-row form: first row names the columns.
    const header = (payload[0] as unknown[]).map((cell) => String(cell));
    rows = (payload.slice(1) as unknown[][]).map((row) =>
      Object.fromEntries(header.map((key, index) => [key, row[index]])),
    );
  } else {
    rows = payload.filter(
      (row): row is Record<string, unknown> => typeof row === "object" && row !== null,
    );
  }

  const num = (value: unknown): number | null => {
    if (value === null || value === undefined || value === "") return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  };

  return rows.map((row) => {
    const kp = num(row.Kp ?? row.kp ?? row.kp_index);
    return {
      time_tag: row.time_tag ? String(row.time_tag) : null,
      kp,
      a_running: num(row.a_running),
      station_count: num(row.station_count),
      storm: kp !== null && kp >= STORM_THRESHOLD,
    };
  });
}

/** NOAA's G-scale label for a Kp value. */
function gScale(kp: number | null): string {
  if (kp === null) return "unknown";
  if (kp >= 9) return "G5 (extreme)";
  if (kp >= 8) return "G4 (severe)";
  if (kp >= 7) return "G3 (strong)";
  if (kp >= 6) return "G2 (moderate)";
  if (kp >= 5) return "G1 (minor)";
  return "below storm level";
}

async function runKp(options: {
  limit: number;
  stormOnly?: boolean;
  latest?: boolean;
  json?: boolean;
}): Promise<void> {
  const readings = normalizeKpFeed(await fetchJson(KP_URL));

  // Newest first.
  const ordered = [...readings].sort((a, b) =>
    String(b.time_tag ?? "").localeCompare(String(a.time_tag ?? "")),
  );

  let filtered = options.stormOnly ? ordered.filter((row) => row.storm) : ordered;
  // `--latest` returns one observation and overrides --limit.
  const cutoff = options.latest ? 1 : options.limit;
  const shown = filtered.slice(0, cutoff);

  if (options.json) {
    emitJson({
      retrieved_at: retrievedAt(),
      source: KP_URL,
      storm_threshold_kp: STORM_THRESHOLD,
      count: shown.length,
      observations: shown,
    });
  }

  if (shown.length === 0) {
    console.error(
      options.stormOnly
        ? `No observation reached Kp ${STORM_THRESHOLD} in the returned window.`
        : "No planetary K-index observations were returned.",
    );
    process.exit(EXIT_NO_MATCH);
  }
  if (options.json) return;

  for (const row of shown) {
    const kp = row.kp === null ? "?" : row.kp.toFixed(2).replace(/\.00$/, "");
    console.log(
      `${row.time_tag ?? "unknown time"}  Kp ${kp.padStart(5)}  ${gScale(row.kp)}`,
    );
  }
  console.log(`\nRetrieved ${retrievedAt()} from ${KP_URL}.`);
}

// ------------------------------------------------------------------- cli ----

const program = new Command();

program
  .name("space_weather.ts")
  .description("Current NOAA SWPC space-weather alerts and geomagnetic activity.")
  .showHelpAfterError();

program
  .command("alerts")
  .description("Show recent NOAA watches, warnings, and alerts, newest first.")
  .option("--limit <n>", "maximum alerts to show", (v) => parseLimit(v, "--limit"), 10)
  .addOption(
    new Option("--scale <scale>", "filter to a NOAA scale").choices(["G", "S", "R"]),
  )
  .option("--contains <text>", "case-insensitive substring of the bulletin text")
  .option("--json", "emit structured JSON on stdout")
  .action(runAlerts);

program
  .command("kp")
  .description("Show recent planetary K-index observations, newest first.")
  .option("--limit <n>", "maximum observations to show", (v) => parseLimit(v, "--limit"), 12)
  .option("--storm-only", `only show observations at Kp ${STORM_THRESHOLD} or higher`)
  .option("--latest", "show only the most recent observation (overrides --limit)")
  .option("--json", "emit structured JSON on stdout")
  .action(runKp);

program.parse();

if (program.args.length === 0) {
  program.help();
}
