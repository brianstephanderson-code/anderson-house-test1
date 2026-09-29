import test from "node:test";
import assert from "node:assert/strict";
import { characterResultFor } from "../core/character_count.mjs";

test("character count empty", () => {
  assert.deepEqual(characterResultFor(""), { characters: 0 });
});

test("character count preserves spaces and punctuation", () => {
  assert.deepEqual(characterResultFor("Hi, Sam!"), { characters: 8 });
});
