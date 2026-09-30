import test from 'node:test';
import assert from 'node:assert/strict';
import {
  assembleReaderEdition,
  verifyAssemblySourceIntegrity,
} from '../core/reader_edition_assembler.mjs';

const source = 'Alpha source paragraph.\n\nBeta source paragraph.\n\nGamma source paragraph.';

test('assembles verified support beside source without changing source paragraphs', () => {
  const result = assembleReaderEdition({
    sourceText: source,
    admissions: [
      {
        jobId: 'SH-001-01',
        paragraphId: 'P002',
        state: 'READY_FOR_ASSEMBLY',
        sourceMutationAllowed: false,
        readerAid: {
          term: 'Beta',
          text: 'A verified reader aid.',
          sourceIds: ['S1', 'S2'],
        },
      },
    ],
  }).readerEditionAssembly;

  assert.equal(result.state, 'READER_EDITION_ASSEMBLED');
  assert.equal(result.sourceTextUnchanged, true);
  assert.equal(result.sourceParagraphCount, 3);
  assert.equal(result.admittedAidCount, 1);
  assert.equal(result.blocks[1].sourceText, 'Beta source paragraph.');
  assert.equal(result.blocks[1].readerAids[0].jobId, 'SH-001-01');
});

test('ignores held/non-admitted returns rather than leaking them into reader-facing support', () => {
  const result = assembleReaderEdition({
    sourceText: source,
    admissions: [
      {
        jobId: 'SH-001-02',
        paragraphId: 'P001',
        state: 'HOLD_VERIFICATION',
      },
    ],
  }).readerEditionAssembly;

  assert.equal(result.admittedAidCount, 0);
});

test('rejects duplicate job identities', () => {
  assert.throws(
    () => assembleReaderEdition({
      sourceText: source,
      admissions: [
        { jobId: 'J1', paragraphId: 'P001', state: 'HOLD' },
        { jobId: 'J1', paragraphId: 'P002', state: 'HOLD' },
      ],
    }),
    /duplicate admitted job/,
  );
});

test('rejects source-mutation permission on an admitted aid', () => {
  assert.throws(
    () => assembleReaderEdition({
      sourceText: source,
      admissions: [
        {
          jobId: 'J1',
          paragraphId: 'P001',
          state: 'READY_FOR_ASSEMBLY',
          sourceMutationAllowed: true,
          readerAid: { text: 'Aid.' },
        },
      ],
    }),
    /source mutation/,
  );
});

test('source integrity verifier catches a changed source paragraph', () => {
  const assembly = assembleReaderEdition({
    sourceText: source,
    admissions: [],
  });
  assembly.readerEditionAssembly.blocks[1].sourceText = 'Changed.';
  const check = verifyAssemblySourceIntegrity({ sourceText: source, assembly });
  assert.equal(check.assemblySourceIntegrity.state, 'FAIL');
});

test('source integrity verifier passes a clean assembly', () => {
  const assembly = assembleReaderEdition({
    sourceText: source,
    admissions: [],
  });
  const check = verifyAssemblySourceIntegrity({ sourceText: source, assembly });
  assert.equal(check.assemblySourceIntegrity.state, 'PASS');
});
