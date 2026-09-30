import test from 'node:test';
import assert from 'node:assert/strict';
import { routeEvidence } from '../core/evidence_router.mjs';

test('routes St. Nicholas to evidence doors without deciding its meaning', () => {
  const out = routeEvidence({term:'St. Nicholas', context:'Dutch navigators invoke St. Nicholas while crossing the Tappan Zee.'}).evidenceRoute;
  assert.equal(out.state,'needs-evidence');
  assert.ok(out.doors.includes('reference-identity'));
  assert.ok(out.doors.includes('historical-context'));
  assert.match(out.rule,/DO NOT INFER MEANING FROM SHAPE/);
});

test('routes a lexical candidate toward historical usage evidence', () => {
  const out = routeEvidence({term:'apparition', context:'A relevant Irving sentence containing apparition.'}).evidenceRoute;
  assert.ok(out.doors.includes('historical-dictionary'));
  assert.ok(out.doors.includes('usage-evidence'));
});
