import crypto from 'node:crypto';

function paragraphRecords(text) {
  const value = String(text);
  const parts = value.split(/\n\s*\n/).filter((p) => p.trim().length > 0);
  return parts.map((paragraph, index) => ({
    paragraphId: `P${String(index + 1).padStart(3, '0')}`,
    ordinal: index + 1,
    preview: paragraph.replace(/\s+/g, ' ').trim().slice(0, 120),
  }));
}

export function buildReaderEditionShell({ text, supportCandidates = [] } = {}) {
  if (typeof text !== 'string' || !text.trim()) throw new Error('text is required');

  const paragraphs = paragraphRecords(text);
  const validIds = new Set(paragraphs.map((p) => p.paragraphId));

  const supportSlots = supportCandidates.map((candidate) => {
    const jobId = String(candidate.jobId ?? '');
    const paragraphId = String(candidate.paragraphId ?? '');
    const state = String(candidate.state ?? 'READY');
    if (!jobId) throw new Error('support candidate jobId is required');
    if (!validIds.has(paragraphId)) throw new Error(`unknown paragraphId: ${paragraphId}`);

    return {
      jobId,
      term: String(candidate.term ?? ''),
      paragraphId,
      state,
      readerFacingEligible: state === 'VERIFIED_READER_AID',
    };
  });

  return {
    readerEditionShell: {
      state: 'SHELL_READY',
      sourceIntegrity: {
        sha256: crypto.createHash('sha256').update(text, 'utf8').digest('hex'),
        sourceTextUnchanged: true,
        sourceTextEmbedded: false,
      },
      metrics: {
        paragraphCount: paragraphs.length,
        wordCount: (text.match(/\S+/g) ?? []).length,
      },
      paragraphs,
      supportSlots,
      rules: [
        'MASTER NEVER WORKS. COPIES WORK.',
        'Reader-facing support attaches by stable paragraphId and jobId.',
        'Only VERIFIED_READER_AID slots may enter the reader-facing layer.',
        'NO_MATERIAL_AID and RECAST remain evidence but do not alter source text.',
      ],
    },
  };
}
