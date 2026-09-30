import { providerHiveProfile } from "./core/provider_hive.mjs";
import { searchDiscover } from "./search_discover.mjs";

export default {
  async fetch(request) {
    let body = {};
    if (request.method === "POST") body = await request.json().catch(() => ({}));
    else {
      const u = new URL(request.url);
      body = { text: u.searchParams.get("text") ?? "", type: u.searchParams.get("type") ?? "", query: u.searchParams.get("query") ?? "", limit: u.searchParams.get("limit") ?? 5 };
    }

    if (String(body.type ?? "").toUpperCase() === "SEARCH_DISCOVER") {
      return Response.json(await searchDiscover(body.query ?? body.text, body.limit ?? 5));
    }

    return Response.json(await providerHiveProfile(body.text ?? "", "cloudflare"));
  },
};
