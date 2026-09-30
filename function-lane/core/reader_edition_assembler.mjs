// READER EDITION ASSEMBLER
// Joins verified reader-aid admissions to stable paragraph anchors.
// It preserves every source paragraph byte-for-byte and keeps support separate.

function splitParagraphs(text) {
  if (typeof text !== 'string' || !text.trim()) throw new Error('source text is required');
  return text.split(/\n\s*\n/).filter((p) => p.trim().length > 0);
}

export function assembleReaderEdition({
  sourceText,
  admissions = [],
} = {}) {
  const paragraphs = splitParagraphs(sourceText);
  const ids = paragraphs.map((_, i) => `P${String(i + 1).padStart(3, '0')}`);
  const validIds = new Set(ids);

  const seenJobs = new Set();
  const supportByParagraph = new Map();

  for (const item of admissions) {
    const jobId = String(item.jobId ?? item.job_id ?? '');
    const paragraphId = String(item.paragraphId ?? item.paragraph_id ?? '');
    const state = String(item.state ?? '');

    if (!jobId) throw new Error('admission jobId is required');
    if (seenJobs.has(jobId)) throw new Error(`duplicate admitted job: ${jobId}`);
    seenJobs.add(jobId);

    if (state !== 'READY_FOR_ASSEMBLY') continue;
    if (!validIds.has(paragraphId)) throw new Error(`unknown paragraphId: ${paragraphId}`);
    if (item.sourceMutationAllowed === true) throw new Error('source mutation cannot be admitted');

    const aid = item.readerAid ?? item.reader_aid ?? {};
    const text = String(aid.text ?? '').trim();
    if (!text) throw new Error(`reader aid text missing for ${jobId}`);

    const record = {
      jobId,
      paragraphId,
      term: String(aid.term ?? ''),
      text,
      sourceIds: Array.isArray(aid.sourceIds) ? [...aid.sourceIds] : [],
    };
    if (!supportByParagraph.has(paragraphId)) supportByParagraph.set(paragraphId, []);
    supportByParagraph.get(paragraphId).push(record);
  }

  const blocks = paragraphs.map((text, i) => {
    const paragraphId = ids[i];
    return {
      paragraphId,
      sourceText: text,
      readerAids: supportByParagraph.get(paragraphId) ?? [],
    };
  });

  return {
    readerEditionAssembly: {
      state: 'READER_EDITION_ASSEMBLED',
      sourceTextUnchanged: true,
      sourceParagraphCount: paragraphs.length,
      admittedAidCount: blocks.reduce((n, b) => n + b.readerAids.length, 0),
      blocks,
      renderRule: 'Render sourceText as the primary layer; render readerAids as separate subordinate support.',
      nextState: 'QA_ASSEMBLED_READER_EDITION',
    },
  };
}

export function verifyAssemblySourceIntegrity({
  sourceText,
  assembly,
} = {}) {
  if (typeof sourceText !== 'string') throw new Error('source text is required');
  const blocks = assembly?.readerEditionAssembly?.blocks;
  if (!Array.isArray(blocks)) throw new Error('reader edition assembly blocks are required');

  const original = splitParagraphs(sourceText);
  const rebuilt = blocks.map((b) => b.sourceText);

  return {
    assemblySourceIntegrity: {
      state:
        original.length === rebuilt.length &&
        original.every((p, i) => p === rebuilt[i])
          ? 'PASS'
          : 'FAIL',
      sourceParagraphCount: original.length,
      assembledParagraphCount: rebuilt.length,
      rule: 'SUPPORT MAY JOIN THE READER EDITION; SOURCE PARAGRAPHS MAY NOT CHANGE',
    },
  };
}
