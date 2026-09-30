import { providerHiveProfile } from "./core/provider_hive.mjs";
import { searchDiscover } from "./search_discover.mjs";
import { searchDiscoverLoc } from "./search_discover_loc.mjs";

function searchDiscoverStream(queries, limit = 5, parentTicket = "SEARCH") {
  const qs = Array.isArray(queries) ? queries.map(x => String(x).trim()).filter(Boolean).slice(0, 30) : [];
  const enc = new TextEncoder();
  const started = Date.now();
  const stream = new ReadableStream({
    start(controller) {
      if (!qs.length) {
        controller.enqueue(enc.encode(JSON.stringify({ type: "PARENT_COMPLETE", parent_ticket: parentTicket, expected: 0, received: 0 }) + "\n"));
        controller.close();
        return;
      }
      let received = 0;
      qs.forEach((query, i) => {
        const childTicket = parentTicket + "-" + String(i + 1).padStart(2, "0");
        const t0 = Date.now();
        searchDiscover(query, limit)
          .then(out => {
            received++;
            controller.enqueue(enc.encode(JSON.stringify({
              type: "CHILD_RETURN", parent_ticket: parentTicket, child_ticket: childTicket,
              query, elapsed_ms: Date.now() - t0, ...out
            }) + "\n"));
          })
          .catch(err => {
            received++;
            controller.enqueue(enc.encode(JSON.stringify({
              type: "CHILD_RETURN", parent_ticket: parentTicket, child_ticket: childTicket,
              query, elapsed_ms: Date.now() - t0, ok: false, error: String(err)
            }) + "\n"));
          })
          .finally(() => {
            if (received === qs.length) {
              controller.enqueue(enc.encode(JSON.stringify({
                type: "PARENT_COMPLETE", parent_ticket: parentTicket, expected: qs.length,
                received, elapsed_ms: Date.now() - started
              }) + "\n"));
              controller.close();
            }
          });
      });
    }
  });
  return new Response(stream, { headers: { "content-type": "application/x-ndjson; charset=utf-8", "cache-control": "no-store" } });
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
    if (type === "SEARCH_DISCOVER_STREAM") return searchDiscoverStream(body.queries, body.limit ?? 5, body.parent_ticket ?? "SEARCH");
    if (type === "SEARCH_DISCOVER_LOC") return Response.json(await searchDiscoverLoc(body.query ?? body.text, body.limit ?? 5));
    if (type === "SEARCH_DISCOVER") return Response.json(await searchDiscover(body.query ?? body.text, body.limit ?? 5));
    return Response.json(await providerHiveProfile(body.text ?? "", "cloudflare"));
  },
};
