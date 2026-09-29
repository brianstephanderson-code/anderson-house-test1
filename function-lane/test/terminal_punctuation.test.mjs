import test from "node:test";
import assert from "node:assert/strict";
import { hasTerminalPunctuation } from "../core/terminal_punctuation.mjs";

test("empty text is false", () => assert.equal(hasTerminalPunctuation(""), false));
test("plain words are false", () => assert.equal(hasTerminalPunctuation("Many hands work"), false));
test("period is true", () => assert.equal(hasTerminalPunctuation("Many hands work."), true));
test("quoted question is true", () => assert.equal(hasTerminalPunctuation('Ready?"'), true));
