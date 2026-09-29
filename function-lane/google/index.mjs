import { http } from "@google-cloud/functions-framework";
import { resultFor } from "./core/word_count.mjs";

http("wordCount", (req, res) => {
  const text = req.body?.text ?? req.query?.text ?? "";
  res.json(resultFor(text));
});
