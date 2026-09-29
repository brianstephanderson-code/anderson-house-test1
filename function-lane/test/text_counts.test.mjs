import test from "node:test";
import assert from "node:assert/strict";
import { countSentences } from "../core/sentence_count.mjs";
import { countParagraphs } from "../core/paragraph_count.mjs";

test("sentence count empty", () => assert.equal(countSentences(""), 0));
test("sentence count three", () => assert.equal(countSentences("One. Two! Three?"), 3));
test("paragraph count empty", () => assert.equal(countParagraphs(""), 0));
test("paragraph count three", () => assert.equal(countParagraphs("One\n\nTwo\n\nThree"), 3));
