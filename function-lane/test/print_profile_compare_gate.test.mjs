import test from 'node:test';
import assert from 'node:assert/strict';
import { comparePrintProfiles } from '../core/print_profile_compare_gate.mjs';

const candidates = [
  { id: '5x8', trimInches: [5, 8], pageCount: 62, printCostUsd: 2.30 },
  { id: '5.5x8.5', trimInches: [5.5, 8.5], pageCount: 58, printCostUsd: 2.30 },
  { id: '6x9', trimInches: [6, 9], pageCount: 53, printCostUsd: 2.30 },
];

test('does not pretend equal printing cost selects a trim', () => {
  const result = comparePrintProfiles({ candidates, wordCount: 12214 });
  assert.equal(result.costTie, true);
  assert.equal(result.decision, 'NO_FINAL_TRIM_YET');
  assert.equal(result.state, 'READER_PROOF_REQUIRED');
  assert.equal(result.candidates[0].wordsPerPage, 197);
  assert.equal(result.candidates[1].wordsPerPage, 210.6);
  assert.equal(result.candidates[2].wordsPerPage, 230.5);
});

test('preserves mixed operator evidence as uncertainty rather than laundering it into a winner', () => {
  const result = comparePrintProfiles({
    candidates,
    wordCount: 12214,
    operatorEvidence: [
      { preference: 'smaller', note: 'some fiction operators prefer 5x8 or 5.5x8.5' },
      { preference: 'larger', note: 'some operators prefer 6x9' },
    ],
  });
  assert.ok(result.missing.includes('operator preference is mixed and subjective'));
  assert.equal(result.nextState, 'RUN_READER_AID_STRESS_AND_PHYSICAL_PROOF');
});

test('can advance to selection only after physical proof exists', () => {
  const result = comparePrintProfiles({
    candidates,
    wordCount: 12214,
    physicalProofAvailable: true,
  });
  assert.equal(result.state, 'COMPARE_READY');
  assert.equal(result.nextState, 'SELECT_OR_RECAST_PRINT_PROFILE');
});
