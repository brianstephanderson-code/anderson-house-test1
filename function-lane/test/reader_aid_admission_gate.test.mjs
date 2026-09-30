import test from 'node:test';
import assert from 'node:assert/strict';
import { readerAidAdmissionGate, planReaderAidAssembly } from '../core/reader_aid_admission_gate.mjs';

const slot = { job_id: 'SH-001-01', paragraph_id: 'P004' };

test('admits only an explicitly verified reader aid with a verified passport', () => {
  const result = readerAidAdmissionGate({
    attachmentSlot: slot,
    researchReturn: {
      job_id: 'SH-001-01',
      term: 'CASTLE OF INDOLENCE',
      outcome: 'VERIFIED_READER_AID',
      reader_aid_text: 'A short verified note.',
      verification_passport: {
        state: 'verified',
        sources: [{ id: 'S1' }, { id: 'S2' }],
      },
    },
  }).readerAidAdmission;
  assert.equal(result.state, 'READY_FOR_ASSEMBLY');
  assert.equal(result.admitted, true);
  assert.equal(result.sourceMutationAllowed, false);
  assert.deepEqual(result.readerAid.sourceIds, ['S1', 'S2']);
});

test('does not insert a NO_MATERIAL_AID return', () => {
  const result = readerAidAdmissionGate({
    attachmentSlot: slot,
    researchReturn: { job_id: 'SH-001-01', outcome: 'NO_MATERIAL_AID' },
  }).readerAidAdmission;
  assert.equal(result.state, 'CLOSED_NO_INSERT');
  assert.equal(result.admitted, false);
});

test('sends a RECAST back to research without insertion', () => {
  const result = readerAidAdmissionGate({
    attachmentSlot: slot,
    researchReturn: {
      job_id: 'SH-001-01',
      outcome: 'RECAST',
      missing_evidence: 'period usage',
    },
  }).readerAidAdmission;
  assert.equal(result.state, 'RETURN_TO_RESEARCH');
  assert.equal(result.reason, 'period usage');
});

test('holds a claimed verified aid if its verification passport is not verified', () => {
  const result = readerAidAdmissionGate({
    attachmentSlot: slot,
    researchReturn: {
      job_id: 'SH-001-01',
      outcome: 'VERIFIED_READER_AID',
      reader_aid_text: 'Premature note.',
      verification_passport: { state: 'single-road' },
    },
  }).readerAidAdmission;
  assert.equal(result.state, 'HOLD_VERIFICATION');
  assert.equal(result.admitted, false);
});

test('rejects cross-marriage to the wrong job slot', () => {
  assert.throws(
    () => readerAidAdmissionGate({
      attachmentSlot: slot,
      researchReturn: { job_id: 'SH-001-02', outcome: 'NO_MATERIAL_AID' },
    }),
    /does not match attachment slot/,
  );
});

test('assembly planner prevents duplicate returns for one job', () => {
  assert.throws(
    () => planReaderAidAssembly({
      attachmentSlots: [slot],
      researchReturns: [
        { job_id: 'SH-001-01', outcome: 'NO_MATERIAL_AID' },
        { job_id: 'SH-001-01', outcome: 'NO_MATERIAL_AID' },
      ],
    }),
    /duplicate research return/,
  );
});
