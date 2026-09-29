import { resultFor } from "./word_count.mjs";
import { sentenceResultFor } from "./sentence_count.mjs";
import { paragraphResultFor } from "./paragraph_count.mjs";
import { punctuationResultFor } from "./terminal_punctuation.mjs";
import { characterResultFor } from "./character_count.mjs";

const CHILDREN = Object.freeze([
  ["word_count", resultFor],
  ["sentence_count", sentenceResultFor],
  ["paragraph_count", paragraphResultFor],
  ["terminal_punctuation", punctuationResultFor],
  ["character_count", characterResultFor],
]);

export async function providerHiveProfile(text = "", provider = "provider") {
  const value = String(text);
  const started = Date.now();

  const pieces = await Promise.all(
    CHILDREN.map(async ([name, fn]) => ({
      name,
      result: fn(value),
    })),
  );

  return {
    ...Object.assign({}, ...pieces.map((piece) => piece.result)),
    providerHive: {
      provider: String(provider),
      mode: "fanout-join",
      workerCount: pieces.length,
      workers: pieces.map((piece) => piece.name),
      elapsedMs: Date.now() - started,
    },
  };
}
