import { resultFor } from "./core/word_count.mjs";
import { sentenceResultFor } from "./core/sentence_count.mjs";
import { paragraphResultFor } from "./core/paragraph_count.mjs";
import { punctuationResultFor } from "./core/terminal_punctuation.mjs";

const CHILDREN = [
  ["word_count", resultFor],
  ["sentence_count", sentenceResultFor],
  ["paragraph_count", paragraphResultFor],
  ["terminal_punctuation", punctuationResultFor],
];

export async function googleHiveProfile(text = "") {
  const value = String(text);
  const started = Date.now();
  const pieces = await Promise.all(
    CHILDREN.map(async ([name, fn]) => ({ name, result: fn(value) }))
  );

  return {
    ...Object.assign({}, ...pieces.map((piece) => piece.result)),
    googleHive: {
      mode: "fanout-join",
      workerCount: pieces.length,
      workers: pieces.map((piece) => piece.name),
      elapsedMs: Date.now() - started,
    },
  };
}
