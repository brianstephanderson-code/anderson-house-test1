import { providerHiveProfile } from "./core/provider_hive.mjs";

export default {
  async fetch(request) {
    let text = "";
    if (request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      text = body.text ?? "";
    } else {
      text = new URL(request.url).searchParams.get("text") ?? "";
    }

    return Response.json(await providerHiveProfile(text, "cloudflare"));
  },
};
