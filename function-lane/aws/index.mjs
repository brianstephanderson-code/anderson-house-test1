import { providerHiveProfile } from "./core/provider_hive.mjs";

export const handler = async (event = {}) => {
  let body = event;
  if (typeof event.body === "string") {
    try {
      body = JSON.parse(event.body);
    } catch {
      body = { text: event.body };
    }
  }

  const result = await providerHiveProfile(body?.text ?? "", "aws");

  return {
    statusCode: 200,
    headers: { "content-type": "application/json" },
    body: JSON.stringify(result),
  };
};
