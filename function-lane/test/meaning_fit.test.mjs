import test from 'node:test';
import assert from 'node:assert/strict';
import { meaningFit } from '../core/meaning_fit.mjs';

test('Meaning Fit refuses to choose a glossary definition before context evidence', () => {
  const result = meaningFit({
    term: 'St. Nicholas',
    context: 'Dutch navigators invoke St. Nicholas while crossing the Tappan Zee.',
    candidateMeanings: ['a referenced protective religious figure', 'a place name', 'a publication title'],
  }).meaningFit;

  assert.equal(result.term, 'St. Nicholas');
  assert.equal(result.candidateMeanings.length, 3);
  assert.ok(result.candidateMeanings.every((x) => x.status === 'unverified'));
  assert.ok(result.allowedDoneStates.includes('verified-contextual-meaning'));
  assert.match(result.rule, /FUNCTION FIRST/);
});
