import test from 'node:test';
import assert from 'node:assert/strict';
import { buildReaderEditionShell } from '../core/reader_edition_shell.mjs';

test('builds stable paragraph anchors without embedding or changing source text', () => {
  const text = 'First paragraph.\n\nSecond paragraph.\n\nThird paragraph.';
  const result = buildReaderEditionShell({
    text,
    supportCandidates: [
      { jobId: 'J1', term: 'First', paragraphId: 'P001', state: 'READY' },
      { jobId: 'J2', term: 'Second', paragraphId: 'P002', state: 'VERIFIED_READER_AID' },
    ],
  }).readerEditionShell;

  assert.equal(result.state, 'SHELL_READY');
  assert.equal(result.metrics.paragraphCount, 3);
  assert.equal(result.metrics.wordCount, 6);
  assert.deepEqual(result.paragraphs.map((p) => p.paragraphId), ['P001', 'P002', 'P003']);
  assert.equal(result.sourceIntegrity.sourceTextUnchanged, true);
  assert.equal(result.sourceIntegrity.sourceTextEmbedded, false);
  assert.equal(result.supportSlots[0].readerFacingEligible, false);
  assert.equal(result.supportSlots[1].readerFacingEligible, true);
});

test('rejects support aimed at a paragraph that does not exist', () => {
  assert.throws(
    () => buildReaderEditionShell({
      text: 'Only one paragraph.',
      supportCandidates: [{ jobId: 'J1', paragraphId: 'P002', state: 'READY' }],
    }),
    /unknown paragraphId/,
  );
});
