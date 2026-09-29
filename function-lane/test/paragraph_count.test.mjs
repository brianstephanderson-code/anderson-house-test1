import test from "node:test";
import assert from "node:assert/strict";
import { countParagraphs, paragraphResultFor } from "../core/paragraph_count.mjs";

test("counts book paragraphs separated by blank lines", () => {
  const text = "First paragraph.\nStill first.\n\nSecond paragraph.\n\n\nThird paragraph.";
  assert.equal(countParagraphs(text), 3);
});

test("ignores surrounding whitespace and empty text", () => {
  assert.equal(countParagraphs("  \n\n  "), 0);
  assert.equal(countParagraphs("  One paragraph.  "), 1);
});

test("returns the standard paragraph result envelope", () => {
  assert.deepEqual(paragraphResultFor("One.\n\nTwo."), { paragraphs: 2 });
});
