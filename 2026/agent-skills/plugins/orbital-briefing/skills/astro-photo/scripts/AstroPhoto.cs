#!/usr/bin/env dotnet
#:package System.CommandLine@2.0.10

// NASA Astronomy Picture of the Day metadata.
//
// This is a .NET 10 file-based app: the #:package directive above restores the
// only external dependency straight from NuGet, with no .csproj involved.

using System.CommandLine;
using System.Globalization;
using System.Net.Http.Headers;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;

const string UserAgent = "orbital-briefing/astro-photo (+https://github.com/dbirks/techradar)";
const string ApodUrl = "https://api.nasa.gov/planetary/apod";
const int TimeoutSeconds = 30;

const int ExitApiError = 4;
const int ExitBadInput = 5;

// APOD's archive begins on 1995-06-16.
var archiveStart = new DateOnly(1995, 6, 16);

var hdOption = new Option<bool>("--hd")
{
    Description = "Prefer the HD image URL when the entry is an image and one exists.",
};
var jsonOption = new Option<bool>("--json")
{
    Description = "Emit structured JSON on stdout.",
};
var dateOption = new Option<string>("--date")
{
    Description = "Date to retrieve, formatted YYYY-MM-DD.",
    Required = true,
};

var todayCommand = new Command("today", "Retrieve today's Astronomy Picture of the Day.");
todayCommand.Options.Add(hdOption);
todayCommand.Options.Add(jsonOption);
todayCommand.SetAction((parseResult, ct) =>
    RunAsync(null, parseResult.GetValue(hdOption), parseResult.GetValue(jsonOption), ct));

var dateCommand = new Command("date", "Retrieve the Astronomy Picture of the Day for a date.");
dateCommand.Options.Add(dateOption);
dateCommand.Options.Add(hdOption);
dateCommand.Options.Add(jsonOption);
dateCommand.SetAction((parseResult, ct) =>
    RunAsync(parseResult.GetValue(dateOption), parseResult.GetValue(hdOption), parseResult.GetValue(jsonOption), ct));

var root = new RootCommand(
    "NASA Astronomy Picture of the Day metadata. Requires NASA_API_KEY; get a free key at https://api.nasa.gov/.");
root.Subcommands.Add(todayCommand);
root.Subcommands.Add(dateCommand);

return await root.Parse(args).InvokeAsync();

// ----------------------------------------------------------------- helpers ---

static int Die(string message, int code)
{
    Console.Error.WriteLine($"error: {message}");
    return code;
}

/// <summary>
/// Read the required NASA API key. There is deliberately no fallback to NASA's
/// shared DEMO_KEY: it allows only about 10 requests per IP address and then
/// blocks for hours, which fails in a way that looks like a broken tool.
/// </summary>
static string? ApiKey()
{
    var key = Environment.GetEnvironmentVariable("NASA_API_KEY");
    return string.IsNullOrWhiteSpace(key) ? null : key.Trim();
}

async Task<int> RunAsync(string? rawDate, bool hd, bool asJson, CancellationToken ct)
{
    DateOnly? requested = null;

    if (rawDate is not null)
    {
        if (!DateOnly.TryParseExact(rawDate, "yyyy-MM-dd", CultureInfo.InvariantCulture,
                DateTimeStyles.None, out var parsed))
        {
            return Die($"--date must be a real calendar date formatted YYYY-MM-DD (got {rawDate})", ExitBadInput);
        }

        var todayUtc = DateOnly.FromDateTime(DateTime.UtcNow);
        if (parsed > todayUtc)
        {
            return Die($"--date {rawDate} is in the future; APOD only has entries through {todayUtc:yyyy-MM-dd}", ExitBadInput);
        }
        if (parsed < archiveStart)
        {
            return Die($"--date {rawDate} predates the APOD archive, which starts {archiveStart:yyyy-MM-dd}", ExitBadInput);
        }

        requested = parsed;
    }

    var key = ApiKey();
    if (key is null)
    {
        return Die(
            "NASA_API_KEY is not set. Get a free key at https://api.nasa.gov/ "
            + "(name, email, accept terms) and export it:\n"
            + "       export NASA_API_KEY=your-key-here",
            ExitBadInput);
    }

    var url = requested is null
        ? $"{ApodUrl}?api_key={Uri.EscapeDataString(key)}"
        : $"{ApodUrl}?date={requested:yyyy-MM-dd}&api_key={Uri.EscapeDataString(key)}";

    using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(TimeoutSeconds) };
    client.DefaultRequestHeaders.UserAgent.ParseAdd(UserAgent);
    client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

    HttpResponseMessage response;
    try
    {
        response = await client.GetAsync(url, ct);
    }
    catch (TaskCanceledException) when (!ct.IsCancellationRequested)
    {
        return Die($"request to api.nasa.gov timed out after {TimeoutSeconds}s", ExitApiError);
    }
    catch (HttpRequestException e)
    {
        return Die($"could not reach api.nasa.gov: {e.Message}", ExitApiError);
    }

    if ((int)response.StatusCode == 429)
    {
        return Die(
            "NASA API rate limit reached for this key (4000 requests per hour). "
            + "Check the x-ratelimit-remaining response header and retry later.",
            ExitApiError);
    }
    if (!response.IsSuccessStatusCode)
    {
        return Die($"NASA APOD returned HTTP {(int)response.StatusCode}", ExitApiError);
    }

    JsonNode? payload;
    try
    {
        payload = JsonNode.Parse(await response.Content.ReadAsStringAsync(ct));
    }
    catch (JsonException)
    {
        return Die("NASA APOD returned a response that is not valid JSON", ExitApiError);
    }

    if (payload is not JsonObject obj)
    {
        return Die("NASA APOD did not return a JSON object", ExitApiError);
    }

    string? Text(string field) => obj.TryGetPropertyValue(field, out var node) ? node?.GetValue<string>() : null;

    var mediaType = Text("media_type");
    var regularUrl = Text("url");
    var hdUrl = Text("hdurl");

    // --hd only applies to images; video entries have no HD variant.
    var selectedUrl = hd && mediaType == "image" && !string.IsNullOrWhiteSpace(hdUrl)
        ? hdUrl
        : regularUrl;

    var record = new ApodRecord(
        Date: Text("date"),
        Title: Text("title"),
        Explanation: Text("explanation"),
        MediaType: mediaType,
        SelectedUrl: selectedUrl,
        Url: regularUrl,
        HdUrl: hdUrl,
        ThumbnailUrl: Text("thumbnail_url"),
        ServiceVersion: Text("service_version"),
        Copyright: Text("copyright"),
        RetrievedAt: DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture),
        Source: ApodUrl);

    if (asJson)
    {
        Console.WriteLine(JsonSerializer.Serialize(record, ApodJson.RecordInfo));
        return 0;
    }

    Console.WriteLine(record.Title ?? "(untitled)");
    Console.WriteLine($"  date:      {record.Date}");
    Console.WriteLine($"  media:     {record.MediaType}");
    if (!string.IsNullOrWhiteSpace(record.SelectedUrl))
    {
        Console.WriteLine($"  url:       {record.SelectedUrl}");
    }
    if (!string.IsNullOrWhiteSpace(record.HdUrl) && record.HdUrl != record.SelectedUrl)
    {
        Console.WriteLine($"  hd url:    {record.HdUrl}");
    }
    if (!string.IsNullOrWhiteSpace(record.ThumbnailUrl))
    {
        Console.WriteLine($"  thumbnail: {record.ThumbnailUrl}");
    }
    Console.WriteLine($"  copyright: {record.Copyright ?? "(none stated; not necessarily public domain)"}");
    if (!string.IsNullOrWhiteSpace(record.Explanation))
    {
        Console.WriteLine();
        Console.WriteLine(Wrap(record.Explanation!, 78));
    }
    Console.WriteLine();
    Console.WriteLine($"Retrieved {record.RetrievedAt} from {record.Source}.");
    Console.WriteLine("Respect the stated copyright; APOD assets are not all public domain.");
    return 0;
}

/// <summary>Wrap explanation text so terminal output stays readable.</summary>
static string Wrap(string text, int width)
{
    var words = text.Split(' ', StringSplitOptions.RemoveEmptyEntries);
    var lines = new List<string>();
    var line = new System.Text.StringBuilder();

    foreach (var word in words)
    {
        if (line.Length > 0 && line.Length + 1 + word.Length > width)
        {
            lines.Add(line.ToString());
            line.Clear();
        }
        if (line.Length > 0) line.Append(' ');
        line.Append(word);
    }
    if (line.Length > 0) lines.Add(line.ToString());
    return string.Join(Environment.NewLine, lines);
}

record ApodRecord(
    [property: JsonPropertyName("date")] string? Date,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("explanation")] string? Explanation,
    [property: JsonPropertyName("media_type")] string? MediaType,
    [property: JsonPropertyName("selected_url")] string? SelectedUrl,
    [property: JsonPropertyName("url")] string? Url,
    [property: JsonPropertyName("hdurl")] string? HdUrl,
    [property: JsonPropertyName("thumbnail_url")] string? ThumbnailUrl,
    [property: JsonPropertyName("service_version")] string? ServiceVersion,
    [property: JsonPropertyName("copyright")] string? Copyright,
    [property: JsonPropertyName("retrieved_at")] string? RetrievedAt,
    [property: JsonPropertyName("source")] string? Source);

[JsonSourceGenerationOptions(WriteIndented = true)]
[JsonSerializable(typeof(ApodRecord))]
partial class ApodJsonContext : JsonSerializerContext;

static class ApodJson
{
    // The generated resolver keeps serialization trim- and AOT-safe, so running
    // the script produces no IL2026/IL3050 warnings. The encoder is layered on
    // top to keep apostrophes readable: output only ever goes to stdout, never
    // into HTML, so the relaxed encoder is appropriate here.
    private static readonly JsonSerializerOptions Options =
        new(ApodJsonContext.Default.Options)
        {
            Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        };

    internal static readonly JsonTypeInfo<ApodRecord> RecordInfo =
        (JsonTypeInfo<ApodRecord>)Options.GetTypeInfo(typeof(ApodRecord));
}
