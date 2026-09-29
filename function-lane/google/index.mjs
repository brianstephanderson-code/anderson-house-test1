import { http } from "@google-cloud/functions-framework";
import { resultFor } from "./core/word_count.mjs";
import { sentenceResultFor } from "./core/sentence_count.mjs";
import { paragraphResultFor } from "./core/paragraph_count.mjs";

http("wordCount", (req, res) => {
  const text = req.body?.text ?? req.query?.text ?? "";
  res.json({
    ...resultFor(text),
    ...sentenceResultFor(text),
    ...paragraphResultFor(text),
  });
});
