import { providerHiveProfile } from "./core/provider_hive.mjs";
import { searchDiscover } from "./search_discover.mjs";
import { searchDiscoverLocRoute } from "./search_discover_loc_route.mjs";
import { fetchText } from "./fetch_text.mjs";
import { readTextLinks } from "./read_text_links.mjs";
import { searchEndToEndV1 } from "./search_end_to_end.mjs";
import { searchWebPublic } from "./search_web_public.mjs";
import { normalizeResults, deduplicateResults } from "./search_socket.mjs";
import { aiSourceGate } from "./search_ai_source_gate.mjs";
import { cloudflareAiCasts } from "./cloudflare_ai_casts.mjs";
import { cloudflareAiAnswer } from "./cloudflare_ai_answer.mjs";\nimport { cloudflareEvidenceAnswer } from "./cloudflare_evidence_answer.mjs";\nimport { cloudflareAiCastsV20 } from "./cloudflare_ai_casts_v20.mjs";

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
  async fetch(request, env) {
    let body = {};
    if (request.method === "POST") body = await request.json().catch(() => ({}));
    else {
      const u = new URL(request.url);
      body = {
        text: u.searchParams.get("text") ?? "",
        type: u.searchParams.get("type") ?? "",
        query: u.searchParams.get("query") ?? "",
        limit: u.searchParams.get("limit") ?? 5,
        url: u.searchParams.get("url") ?? "",
        max_chars: u.searchParams.get("max_chars") ?? undefined,
        max_links: u.searchParams.get("max_links") ?? undefined,
        read_limit: u.searchParams.get("read_limit") ?? undefined,
        parent_ticket: u.searchParams.get("parent_ticket") ?? undefined,
        browser_fallback: u.searchParams.get("browser_fallback") ?? undefined,
        answer: u.searchParams.get("answer") ?? undefined,
        evidence: [],
        sources: u.searchParams.getAll("source"),
        evidence_terms: u.searchParams.getAll("evidence_term")
      };
    }
    const type = String(body.type ?? "").toUpperCase();
    const browserFallbackRequested = body.browser_fallback === true || ["1","true","yes","on"].includes(String(body.browser_fallback ?? "").toLowerCase());
    if (type === "AI_SOURCE_GATE") return Response.json(await aiSourceGate({answer:body.answer,sources:body.sources},{evidenceTerms:body.evidence_terms??[]}));
    if (type === "CLOUDFLARE_AI_CASTS") return Response.json(await cloudflareAiCasts(body.query ?? body.text, env?.AI));\n    if (type === "CLOUDFLARE_AI_CASTS_V20") return Response.json(await cloudflareAiCastsV20(body.query ?? body.text, env?.AI));
    if (type === "CLOUDFLARE_AI_ANSWER") return Response.json(await cloudflareAiAnswer(body.query ?? body.text, body.evidence ?? [], env?.AI));\n    if (type === "CLOUDFLARE_EVIDENCE_ANSWER") return Response.json(await cloudflareEvidenceAnswer(body.query ?? body.text, body.evidence ?? [], env?.AI));
    if (type === "SEARCH_DISCOVER_STREAM") return searchDiscoverStream(body.queries, body.limit ?? 5, body.parent_ticket ?? "SEARCH");
    if (type === "SEARCH_MULTI_DOOR") {
      const query=body.query ?? body.text;
      const limit=body.limit ?? 5;
      const [wiki,loc]=await Promise.all([searchDiscover(query,limit),searchDiscoverLocRoute(query,limit)]);
      const results=deduplicateResults([
        ...normalizeResults(wiki.results,"WIKIPEDIA_MEDIAWIKI_API"),
        ...normalizeResults(loc.results,"LIBRARY_OF_CONGRESS_JSON_API")
      ]);
      return Response.json({ok:wiki.ok||loc.ok,function:"SEARCH_MULTI_DOOR",cost_gate:"$0",query,doors:[
        {door:"WIKIPEDIA_MEDIAWIKI_API",ok:!!wiki.ok,count:wiki.results?.length??0},
        {door:"LIBRARY_OF_CONGRESS_JSON_API",ok:!!loc.ok,count:loc.results?.length??0}
      ],results});
    }
    if (type === "SEARCH_WEB_PUBLIC") return Response.json(await searchWebPublic(body.query ?? body.text, body.limit ?? 10));
    if (type === "SEARCH_END_TO_END_V1") return Response.json(await searchEndToEndV1(body.query ?? body.text,{limit:body.limit,readLimit:body.read_limit,maxChars:body.max_chars,browserBinding:browserFallbackRequested?(env?.BROWSER??null):null}));
    if (type === "READ_TEXT_LINKS") return Response.json(await readTextLinks(body.url,{maxChars:body.max_chars,maxLinks:body.max_links}));
    if (type === "FETCH_TEXT") return Response.json(await fetchText(body.url, body.max_chars));
    if (type === "SEARCH_DISCOVER_LOC") return Response.json(await searchDiscoverLocRoute(body.query ?? body.text, body.limit ?? 5));
    if (type === "SEARCH_DISCOVER") return Response.json(await searchDiscover(body.query ?? body.text, body.limit ?? 5));
    return Response.json(await providerHiveProfile(body.text ?? "", "cloudflare"));
  },
};
