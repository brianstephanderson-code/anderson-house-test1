import test from "node:test";
import assert from "node:assert/strict";
import { googleHiveProfile } from "../google/google_hive.mjs";

test("Google hive fans one request into four child particles and joins them", async () => {
  const result = await googleHiveProfile("Many hands work. Bees return!");

  assert.equal(result.words, 5);
  assert.equal(result.sentences, 2);
  assert.equal(result.paragraphs, 1);
  assert.equal(result.terminalPunctuation, true);
  assert.equal(result.googleHive.mode, "fanout-join");
  assert.equal(result.googleHive.workerCount, 4);
  assert.deepEqual(result.googleHive.workers, [
    "word_count",
    "sentence_count",
    "paragraph_count",
    "terminal_punctuation",
  ]);
});
