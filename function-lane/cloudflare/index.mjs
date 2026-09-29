import { resultFor } from "./core/word_count.mjs";
import { sentenceResultFor } from "./core/sentence_count.mjs";
import { paragraphResultFor } from "./core/paragraph_count.mjs";

export default {
  async fetch(request) {
    let text = "";
    if (request.method === "POST") {
      const body = await request.json().catch(() => ({}));
      text = body.text ?? "";
    } else {
      text = new URL(request.url).searchParams.get("text") ?? "";
    }

    return Response.json({
      ...resultFor(text),
      ...sentenceResultFor(text),
      ...paragraphResultFor(text),
    });
  },
};
