import { resultFor } from "./core/word_count.mjs";
import { sentenceResultFor } from "./core/sentence_count.mjs";
import { paragraphResultFor } from "./core/paragraph_count.mjs";

export const handler = async (event = {}) => {
  let body = event;
  if (typeof event.body === "string") {
    try {
      body = JSON.parse(event.body);
    } catch {
      body = { text: event.body };
    }
  }

  const text = body?.text ?? "";
  const result = {
    ...resultFor(text),
    ...sentenceResultFor(text),
    ...paragraphResultFor(text),
  };

  return {
    statusCode: 200,
    headers: { "content-type": "application/json" },
    body: JSON.stringify(result),
  };
};
