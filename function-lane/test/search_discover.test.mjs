import { searchDiscover } from "../cloudflare/search_discover.mjs";

const out = await searchDiscover("Washington Irving Sleepy Hollow author purpose", 5);
if (!out.ok) throw new Error(`SEARCH_DISCOVER failed: ${out.error}`);
if (!Array.isArray(out.results) || out.results.length < 1) throw new Error("No results");
for (const x of out.results) {
  if (!x.url || !x.source_door || !x.provenance) throw new Error("Missing evidence metadata");
}
if (out.cost_gate !== "$0") throw new Error("Cost gate missing");
console.log(JSON.stringify(out, null, 2));
