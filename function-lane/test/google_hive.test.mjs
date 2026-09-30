import test from "node:test";
import assert from "node:assert/strict";
import { providerHiveProfile } from "../core/provider_hive.mjs";

test("provider hive fans one request into eight child particles and joins them", async () => {
  const text = "Many hands working. Bees return!";
  const result = await providerHiveProfile(text, "test");

  assert.equal(result.words, 5);
  assert.equal(result.sentences, 2);
  assert.equal(result.paragraphs, 1);
  assert.equal(result.terminalPunctuation, true);
  assert.equal(result.characters, text.length);
  assert.equal(result.lines, 1);
  assert.equal(result.blankLines, 0);
  assert.deepEqual(result.candidateTokens.namedReferences, []);
  assert.ok(result.candidateTokens.wordCandidates.includes("working"));
  assert.equal(result.providerHive.mode, "fanout-join");
  assert.equal(result.providerHive.workerCount, 8);
  assert.deepEqual(result.providerHive.workers, [
    "word_count",
    "sentence_count",
    "paragraph_count",
    "terminal_punctuation",
    "character_count",
    "line_count",
    "blank_line_count",
    "candidate_tokens",
  ]);
});
