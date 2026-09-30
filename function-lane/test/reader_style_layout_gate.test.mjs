import test from 'node:test';
import assert from 'node:assert/strict';
import { buildReaderStyleLayoutProfile } from '../core/reader_style_layout_gate.mjs';

const shell = {
  state: 'SHELL_READY',
  sourceIntegrity: { sha256: 'abc123', sourceTextUnchanged: true },
  supportSlots: [
    { jobId: 'J1', paragraphId: 'P001', state: 'READY', readerFacingEligible: false },
    { jobId: 'J2', paragraphId: 'P002', state: 'VERIFIED_READER_AID', readerFacingEligible: true },
  ],
};

test('creates platform-neutral reader edition style/layout rules', () => {
  const result = buildReaderStyleLayoutProfile({ shell });
  assert.equal(result.state, 'STYLE_LAYOUT_RULES_READY');
  assert.equal(result.sourceIntegrity.sha256, 'abc123');
  assert.equal(result.renderContract.paragraphIdsPreserved, true);
  assert.equal(result.renderContract.vendorSpecificSizingDeferred, true);
  assert.equal(result.profile.readerAidPolicy.mayReplaceSourceText, false);
  assert.equal(result.profile.readerAidPolicy.mayInterruptSourceParagraph, false);
});

test('allows semantic-role overrides without collapsing the roles', () => {
  const result = buildReaderStyleLayoutProfile({
    shell,
    overrides: { roles: { epigraph: { emphasis: 'light' } } },
  });
  assert.equal(result.profile.roles.epigraph.emphasis, 'light');
  assert.equal(result.profile.roles.body.kind, 'body');
});

test('rejects mutated source state', () => {
  assert.throws(
    () => buildReaderStyleLayoutProfile({
      shell: { ...shell, sourceIntegrity: { sha256: 'abc123', sourceTextUnchanged: false } },
    }),
    /source integrity/,
  );
});

test('rejects a reader-facing aid that is not verified', () => {
  assert.throws(
    () => buildReaderStyleLayoutProfile({
      shell: {
        ...shell,
        supportSlots: [{ jobId: 'J3', paragraphId: 'P003', state: 'READY', readerFacingEligible: true }],
      },
    }),
    /not verified/,
  );
});
