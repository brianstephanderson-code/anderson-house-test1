import { http } from "@google-cloud/functions-framework";
import { providerHiveProfile } from "./core/provider_hive.mjs";

http("wordCount", async (req, res) => {
  const text = req.body?.text ?? req.query?.text ?? "";
  res.json(await providerHiveProfile(text, "google"));
});
