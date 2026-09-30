import test from 'node:test';
import assert from 'node:assert/strict';
import { cleanCandidateTokens } from '../core/candidate_cleaner.mjs';

test('candidate cleaner separates useful names from obvious extraction noise', () => {
  const input = {
    namedReferences: ['Tappan Zee', 'St. Nicholas', 'High German', 'Tarry Town. This', 'AMONG THE PAPERS'],
    wordCandidates: ['apparition', 'bewitched'],
  };
  const result = cleanCandidateTokens(input).candidateCleaner;
  const byName = Object.fromEntries(result.namedReferences.map((x) => [x.value, x.bucket]));
  assert.equal(byName['Tappan Zee'], 'keep');
  assert.equal(byName['St. Nicholas'], 'keep');
  assert.equal(byName['High German'], 'keep');
  assert.equal(byName['Tarry Town. This'], 'reject');
  assert.equal(byName['AMONG THE PAPERS'], 'reject');
  assert.ok(result.wordCandidates.every((x) => x.bucket === 'maybe'));
});
