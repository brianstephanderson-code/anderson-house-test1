import test from "node:test";
import assert from "node:assert/strict";
import { lineResultFor } from "../core/line_count.mjs";

test("counts physical text lines across common newline forms", () => {
  assert.deepEqual(lineResultFor(""), { lines: 0 });
  assert.deepEqual(lineResultFor("one"), { lines: 1 });
  assert.deepEqual(lineResultFor("one\ntwo\nthree"), { lines: 3 });
  assert.deepEqual(lineResultFor("one\r\ntwo"), { lines: 2 });
  assert.deepEqual(lineResultFor("one\rtwo"), { lines: 2 });
  assert.deepEqual(lineResultFor("one\n"), { lines: 2 });
});
