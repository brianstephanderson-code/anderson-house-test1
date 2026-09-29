import test from "node:test";
import assert from "node:assert/strict";
import { blankLineResultFor } from "../core/blank_line_count.mjs";

test("blank line count finds empty and whitespace-only layout lines", () => {
  assert.deepEqual(blankLineResultFor(""), { blankLines: 0 });
  assert.deepEqual(blankLineResultFor("Chapter One\n\nFirst paragraph."), { blankLines: 1 });
  assert.deepEqual(blankLineResultFor("One\r\n  \r\nTwo"), { blankLines: 1 });
  assert.deepEqual(blankLineResultFor("One\rTwo"), { blankLines: 0 });
});
