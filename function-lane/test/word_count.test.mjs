import test from "node:test";
import assert from "node:assert/strict";
import { countWords } from "../core/word_count.mjs";

test("empty text", () => assert.equal(countWords(""), 0));
test("three words", () => assert.equal(countWords("many hands work"), 3));
test("whitespace", () => assert.equal(countWords("  many\n hands\twork  "), 3));
