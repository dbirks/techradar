///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 17+
//DEPS info.picocli:picocli:4.7.7
//DEPS com.fasterxml.jackson.core:jackson-databind:2.19.0

// Objects cataloged from launches in the last 30 days, from CelesTrak GP data.
//
// JBang resolves the //DEPS coordinates above from Maven Central and compiles
// this single file; there is no Gradle or Maven project.

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.Callable;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;

@Command(
    name = "RecentSatellites.java",
    mixinStandardHelpOptions = true,
    version = "0.1.0",
    description = "List and search space objects from launches in the last 30 days (CelesTrak GP data).",
    subcommands = {RecentSatellites.Recent.class, RecentSatellites.Find.class})
public class RecentSatellites implements Callable<Integer> {

  static final String FEED_URL =
      "https://celestrak.org/NORAD/elements/gp.php?GROUP=LAST-30-DAYS&FORMAT=JSON";
  static final String USER_AGENT =
      "orbital-briefing/recent-satellites (+https://github.com/dbirks/techradar)";
  static final Duration TIMEOUT = Duration.ofSeconds(30);

  /** Hard ceiling on printed rows so an agent's context cannot be flooded. */
  static final int MAX_ROWS = 100;

  static final int EXIT_NO_MATCH = 3;
  static final int EXIT_API_ERROR = 4;
  static final int EXIT_BAD_INPUT = 5;

  static final ObjectMapper MAPPER = new ObjectMapper();

  public static void main(String... args) {
    int code = new CommandLine(new RecentSatellites()).execute(args);
    System.exit(code);
  }

  @Override
  public Integer call() {
    CommandLine.usage(this, System.out);
    return 0;
  }

  // ------------------------------------------------------------- fetching ---

  static ArrayNode fetchCatalog() throws ExitException {
    HttpClient client =
        HttpClient.newBuilder().connectTimeout(TIMEOUT).followRedirects(HttpClient.Redirect.NORMAL).build();
    HttpRequest request =
        HttpRequest.newBuilder(URI.create(FEED_URL))
            .header("User-Agent", USER_AGENT)
            .header("Accept", "application/json")
            .timeout(TIMEOUT)
            .GET()
            .build();

    HttpResponse<String> response;
    try {
      response = client.send(request, HttpResponse.BodyHandlers.ofString());
    } catch (java.net.http.HttpTimeoutException e) {
      throw new ExitException(
          "request to celestrak.org timed out after " + TIMEOUT.toSeconds() + "s", EXIT_API_ERROR);
    } catch (IOException e) {
      throw new ExitException("could not reach celestrak.org: " + e.getMessage(), EXIT_API_ERROR);
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new ExitException("request was interrupted", EXIT_API_ERROR);
    }

    if (response.statusCode() >= 400) {
      throw new ExitException("CelesTrak returned HTTP " + response.statusCode(), EXIT_API_ERROR);
    }

    JsonNode parsed;
    try {
      parsed = MAPPER.readTree(response.body());
    } catch (IOException e) {
      throw new ExitException(
          "CelesTrak returned a response that is not valid JSON", EXIT_API_ERROR);
    }
    if (!(parsed instanceof ArrayNode array)) {
      // CelesTrak answers a bad GROUP with a plain-text error rather than JSON.
      throw new ExitException("CelesTrak did not return a JSON array of objects", EXIT_API_ERROR);
    }
    return array;
  }

  // ---------------------------------------------------------- normalizing ---

  /**
   * CelesTrak's GP feed carries no OBJECT_TYPE field, so infer it from the
   * naming convention the catalog uses. Reported as a hint, not authority.
   */
  static String inferObjectType(String name) {
    if (name == null) {
      return "unknown";
    }
    String upper = name.toUpperCase(Locale.ROOT);
    if (upper.contains("R/B") || upper.contains("ROCKET BODY")) {
      return "rocket body";
    }
    if (upper.contains("DEB") || upper.contains("DEBRIS") || upper.contains("FRAGMENT")) {
      return "debris";
    }
    if (upper.contains("UNKNOWN") || upper.contains("TBA") || upper.contains("OBJECT ")) {
      return "unknown";
    }
    return "payload";
  }

  static String text(JsonNode node, String field) {
    JsonNode value = node.get(field);
    return value == null || value.isNull() ? null : value.asText();
  }

  static Double number(JsonNode node, String field) {
    JsonNode value = node.get(field);
    if (value == null || value.isNull() || !value.isNumber()) {
      return null;
    }
    return value.asDouble();
  }

  /** One normalized catalog record. */
  record SpaceObject(
      String objectName,
      String objectId,
      Integer noradCatId,
      String objectType,
      String epoch,
      Double inclination,
      Double meanMotion,
      Double periodMinutes,
      Double eccentricity) {

    ObjectNode toJson() {
      ObjectNode node = MAPPER.createObjectNode();
      node.put("OBJECT_NAME", objectName);
      node.put("OBJECT_ID", objectId);
      if (noradCatId == null) {
        node.putNull("NORAD_CAT_ID");
      } else {
        node.put("NORAD_CAT_ID", noradCatId);
      }
      node.put("OBJECT_TYPE_INFERRED", objectType);
      node.put("EPOCH", epoch);
      putNullable(node, "INCLINATION", inclination);
      putNullable(node, "MEAN_MOTION", meanMotion);
      putNullable(node, "PERIOD_MINUTES_DERIVED", periodMinutes);
      putNullable(node, "ECCENTRICITY", eccentricity);
      return node;
    }

    private static void putNullable(ObjectNode node, String field, Double value) {
      if (value == null) {
        node.putNull(field);
      } else {
        node.put(field, value);
      }
    }

    String describe() {
      StringBuilder sb = new StringBuilder();
      sb.append(objectName == null ? "(unnamed object)" : objectName);
      sb.append("  [").append(objectType).append("]");
      sb.append(System.lineSeparator()).append("  intl designator: ").append(objectId);
      sb.append(System.lineSeparator()).append("  NORAD catalog:   ").append(noradCatId);
      if (epoch != null) {
        sb.append(System.lineSeparator()).append("  epoch:           ").append(epoch);
      }
      if (inclination != null) {
        sb.append(System.lineSeparator())
            .append(String.format("  inclination:     %.4f deg", inclination));
      }
      if (meanMotion != null) {
        sb.append(System.lineSeparator())
            .append(String.format("  mean motion:     %.6f rev/day", meanMotion));
      }
      if (periodMinutes != null) {
        sb.append(System.lineSeparator())
            .append(String.format("  period:          %.1f min (derived)", periodMinutes));
      }
      if (eccentricity != null) {
        sb.append(System.lineSeparator())
            .append(String.format("  eccentricity:    %.7f", eccentricity));
      }
      return sb.toString();
    }
  }

  static SpaceObject normalize(JsonNode raw) {
    String name = text(raw, "OBJECT_NAME");
    Double meanMotion = number(raw, "MEAN_MOTION");
    // CelesTrak's GP feed has no PERIOD field; derive it from mean motion.
    Double period =
        (meanMotion == null || meanMotion <= 0) ? null : 1440.0 / meanMotion;
    JsonNode norad = raw.get("NORAD_CAT_ID");
    Integer noradId = (norad == null || norad.isNull()) ? null : norad.asInt();

    return new SpaceObject(
        name,
        text(raw, "OBJECT_ID"),
        noradId,
        inferObjectType(name),
        text(raw, "EPOCH"),
        number(raw, "INCLINATION"),
        meanMotion,
        period,
        number(raw, "ECCENTRICITY"));
  }

  static List<SpaceObject> loadAll() throws ExitException {
    ArrayNode array = fetchCatalog();
    List<SpaceObject> out = new ArrayList<>(array.size());
    for (JsonNode raw : array) {
      if (raw != null && raw.isObject()) {
        out.add(normalize(raw));
      }
    }
    return out;
  }

  /** Default ordering: international designator, then object name. */
  static final Comparator<SpaceObject> DEFAULT_ORDER =
      Comparator.comparing(
              (SpaceObject o) -> o.objectId() == null ? "" : o.objectId(),
              Comparator.reverseOrder())
          .thenComparing(o -> o.objectName() == null ? "" : o.objectName());

  // ----------------------------------------------------------- reporting ----

  static int report(List<SpaceObject> items, boolean asJson, String emptyMessage) {
    String retrievedAt = Instant.now().toString();

    if (asJson) {
      ObjectNode root = MAPPER.createObjectNode();
      root.put("retrieved_at", retrievedAt);
      root.put("source", FEED_URL);
      root.put(
          "note",
          "OBJECT_TYPE_INFERRED is derived from the object name; CelesTrak's GP feed "
              + "has no type field. PERIOD_MINUTES_DERIVED is 1440 / MEAN_MOTION.");
      root.put("count", items.size());
      ArrayNode arr = root.putArray("objects");
      for (SpaceObject item : items) {
        arr.add(item.toJson());
      }
      try {
        System.out.println(MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(root));
      } catch (com.fasterxml.jackson.core.JsonProcessingException e) {
        System.err.println("error: could not serialize output: " + e.getMessage());
        return EXIT_API_ERROR;
      }
    }

    if (items.isEmpty()) {
      System.err.println(emptyMessage);
      return EXIT_NO_MATCH;
    }
    if (asJson) {
      return 0;
    }

    for (int i = 0; i < items.size(); i++) {
      if (i > 0) {
        System.out.println();
      }
      System.out.println(items.get(i).describe());
    }
    System.out.println();
    System.out.println(
        "Retrieved " + retrievedAt + " from CelesTrak (LAST-30-DAYS). Object type is inferred");
    System.out.println(
        "from the catalog name. One launch can produce many payloads, rocket bodies, and debris.");
    return 0;
  }

  static int checkLimit(int limit) throws ExitException {
    if (limit < 1 || limit > MAX_ROWS) {
      throw new ExitException("--limit must be between 1 and " + MAX_ROWS, EXIT_BAD_INPUT);
    }
    return limit;
  }

  // ---------------------------------------------------------- subcommands ---

  @Command(
      name = "recent",
      mixinStandardHelpOptions = true,
      description = "List recently cataloged objects, newest international designator first.")
  static class Recent implements Callable<Integer> {

    @Option(names = "--limit", description = "Maximum objects to show (default: ${DEFAULT-VALUE}).")
    int limit = 20;

    @Option(names = "--name", description = "Case-insensitive substring of the object name.")
    String name;

    @Option(
        names = "--inclination-min",
        description = "Only objects with orbital inclination at or above this many degrees.")
    Double inclinationMin;

    @Option(names = "--json", description = "Emit structured JSON on stdout.")
    boolean json;

    @Override
    public Integer call() {
      try {
        checkLimit(limit);
        if (inclinationMin != null && (inclinationMin < 0 || inclinationMin > 180)) {
          throw new ExitException("--inclination-min must be between 0 and 180", EXIT_BAD_INPUT);
        }

        List<SpaceObject> items = new ArrayList<>(loadAll());
        if (name != null && !name.isBlank()) {
          String needle = name.toLowerCase(Locale.ROOT);
          items.removeIf(
              o ->
                  o.objectName() == null
                      || !o.objectName().toLowerCase(Locale.ROOT).contains(needle));
        }
        if (inclinationMin != null) {
          items.removeIf(o -> o.inclination() == null || o.inclination() < inclinationMin);
        }
        items.sort(DEFAULT_ORDER);

        List<SpaceObject> shown = items.subList(0, Math.min(limit, items.size()));
        return report(shown, json, "No cataloged object matched those filters.");
      } catch (ExitException e) {
        return e.report();
      }
    }
  }

  @Command(
      name = "find",
      mixinStandardHelpOptions = true,
      description = "Search recent objects by name, international designator, or NORAD catalog ID.")
  static class Find implements Callable<Integer> {

    @Parameters(index = "0", paramLabel = "QUERY", description = "Case-insensitive search text.")
    String query;

    @Option(names = "--limit", description = "Maximum objects to show (default: ${DEFAULT-VALUE}).")
    int limit = 20;

    @Option(names = "--json", description = "Emit structured JSON on stdout.")
    boolean json;

    @Override
    public Integer call() {
      try {
        checkLimit(limit);
        if (query == null || query.isBlank()) {
          throw new ExitException("QUERY must not be empty", EXIT_BAD_INPUT);
        }
        String needle = query.toLowerCase(Locale.ROOT);

        List<SpaceObject> items = new ArrayList<>();
        for (SpaceObject o : loadAll()) {
          String haystack =
              String.join(
                      " ",
                      o.objectName() == null ? "" : o.objectName(),
                      o.objectId() == null ? "" : o.objectId(),
                      o.noradCatId() == null ? "" : String.valueOf(o.noradCatId()))
                  .toLowerCase(Locale.ROOT);
          if (haystack.contains(needle)) {
            items.add(o);
          }
        }
        items.sort(DEFAULT_ORDER);

        List<SpaceObject> shown = items.subList(0, Math.min(limit, items.size()));
        return report(shown, json, "No cataloged object matched \"" + query + "\".");
      } catch (ExitException e) {
        return e.report();
      }
    }
  }

  // --------------------------------------------------------------- errors ---

  /** Carries a human-readable diagnostic and the exit code to return. */
  static class ExitException extends Exception {
    final int code;

    ExitException(String message, int code) {
      super(message);
      this.code = code;
    }

    int report() {
      System.err.println("error: " + getMessage());
      return code;
    }
  }
}
