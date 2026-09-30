import { providerHiveProfile } from "./core/provider_hive.mjs";
import { searchDiscover } from "./search_discover.mjs";

async function searchDiscoverBatch(queries, limit = 5) {
  const qs = Array.isArray(queries) ? queries.map(x => String(x).trim()).filter(Boolean).slice(0, 10) : [];
  if (!qs.length) return { ok: false, function: "SEARCH_DISCOVER_BATCH", error: "EMPTY_QUERIES", searches: [] };
  const started = Date.now();
  const searches = await Promise.all(qs.map(async (query, i) => {
    const t0 = Date.now();
    const out = await searchDiscover(query, limit);
    return { sub_ticket: i + 1, query, elapsed_ms: Date.now() - t0, ...out };
  }));
  return { ok: searches.every(x => x.ok), function: "SEARCH_DISCOVER_BATCH", cost_gate: "$0", parallel: true, elapsed_ms: Date.now() - started, search_count: searches.length, success_count: searches.filter(x => x.ok).length, failure_count: searches.filter(x => !x.ok).length, searches };
}

export default {
  async fetch(request) {
    let body = {};
    if (request.method === "POST") body = await request.json().catch(() => ({}));
    else {
      const u = new URL(request.url);
      body = { text: u.searchParams.get("text") ?? "", type: u.searchParams.get("type") ?? "", query: u.searchParams.get("query") ?? "", limit: u.searchParams.get("limit") ?? 5 };
    }
    const type = String(body.type ?? "").toUpperCase();
    if (type === "SEARCH_DISCOVER_BATCH") return Response.json(await searchDiscoverBatch(body.queries, body.limit ?? 5));
    if (type === "SEARCH_DISCOVER") return Response.json(await searchDiscover(body.query ?? body.text, body.limit ?? 5));
    return Response.json(await providerHiveProfile(body.text ?? "", "cloudflare"));
  },
};
