import { http } from "@google-cloud/functions-framework";
import { googleHiveProfile } from "./google_hive.mjs";

http("wordCount", async (req, res) => {
  const text = req.body?.text ?? req.query?.text ?? "";
  res.json(await googleHiveProfile(text));
});
