import test from 'node:test';
import assert from 'node:assert/strict';
import { buildReaderAidStressPlan } from '../core/reader_aid_stress_gate.mjs';

test('builds a deterministic non-reader-facing stress load without claiming research jobs', () => {
  const result = buildReaderAidStressPlan({
    jobs: [
      { job_id: 'J1', function_class: 'lexical' },
      { job_id: 'J2', function_class: 'named_reference' },
      { job_id: 'J3', function_class: 'cultural_lexical' },
    ],
    attachmentSlots: [
      { job_id: 'J1', paragraph_id: 'P005' },
      { job_id: 'J2', paragraph_id: 'P006' },
      { job_id: 'J3', paragraph_id: 'P007' },
    ],
  });
  assert.equal(result.state, 'READER_AID_STRESS_PLAN_READY');
  assert.equal(result.syntheticOnly, true);
  assert.equal(result.aidCount, 3);
  assert.equal(result.syntheticWordLoad, 28 + 55 + 65);
  assert.deepEqual(result.aids.map((x) => x.paragraphId), ['P005', 'P006', 'P007']);
});

test('requires every stress parcel to have a stable attachment slot', () => {
  assert.throws(
    () => buildReaderAidStressPlan({
      jobs: [{ job_id: 'J1', function_class: 'lexical' }],
      attachmentSlots: [],
    }),
    /attachmentSlots are required/,
  );
});
