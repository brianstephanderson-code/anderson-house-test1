// Zero-cost SEARCH_DISCOVER adapter.
// Uses Wikipedia MediaWiki API as the first machine-readable specialist discover door.
// No key, no paid fallback. General-web doors can be added behind the same interface.
export async function searchDiscover(query, limit = 5) {
  const q = String(query ?? "").trim();
  if (!q) return { ok: false, function: "SEARCH_DISCOVER", error: "EMPTY_QUERY", results: [] };
  const n = Math.max(1, Math.min(Number(limit) || 5, 10));
  const u = new URL("https://en.wikipedia.org/w/api.php");
  u.searchParams.set("action", "query");
  u.searchParams.set("list", "search");
  u.searchParams.set("srsearch", q);
  u.searchParams.set("srlimit", String(n));
  u.searchParams.set("format", "json");
  u.searchParams.set("origin", "*");
  const r = await fetch(u, { headers: { "accept": "application/json" } });
  if (!r.ok) return { ok: false, function: "SEARCH_DISCOVER", error: `HTTP_${r.status}`, results: [] };
  const j = await r.json();
  const results = (j?.query?.search ?? []).map(x => ({
    title: x.title,
    url: `https://en.wikipedia.org/wiki/${encodeURIComponent(x.title.replaceAll(" ", "_"))}`,
    snippet: String(x.snippet ?? "").replace(/<[^>]+>/g, ""),
    source_door: "WIKIPEDIA_MEDIAWIKI_API",
    provenance: "en.wikipedia.org/w/api.php"
  }));
  return { ok: true, function: "SEARCH_DISCOVER", cost_gate: "$0", query: q, results };
}
