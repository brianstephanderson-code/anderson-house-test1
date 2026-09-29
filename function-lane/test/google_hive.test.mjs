import test from "node:test";
import assert from "node:assert/strict";
import { providerHiveProfile } from "../core/provider_hive.mjs";

test("provider hive fans one request into four child particles and joins them", async () => {
  const result = await providerHiveProfile("Many hands work. Bees return!", "test");

  assert.equal(result.words, 5);
  assert.equal(result.sentences, 2);
  assert.equal(result.paragraphs, 1);
  assert.equal(result.terminalPunctuation, true);
  assert.equal(result.providerHive.mode, "fanout-join");
  assert.equal(result.providerHive.workerCount, 4);
  assert.deepEqual(result.providerHive.workers, [
    "word_count",
    "sentence_count",
    "paragraph_count",
    "terminal_punctuation",
  ]);
});
