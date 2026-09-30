const DEFAULT_WORD_TARGETS = Object.freeze({
  lexical: 28,
  named_reference: 55,
  historical_lexical: 45,
  cultural_lexical: 65,
});

export function buildReaderAidStressPlan({ jobs = [], attachmentSlots = [] } = {}) {
  if (!Array.isArray(jobs) || jobs.length === 0) throw new Error('jobs are required');
  if (!Array.isArray(attachmentSlots) || attachmentSlots.length === 0) throw new Error('attachmentSlots are required');

  const slots = new Map(attachmentSlots.map((x) => [String(x.job_id ?? x.jobId), x]));
  const aids = jobs.map((job) => {
    const jobId = String(job.job_id ?? job.jobId ?? '');
    const slot = slots.get(jobId);
    if (!jobId || !slot) throw new Error(`missing attachment slot for ${jobId || 'unknown job'}`);
    const functionClass = String(job.function_class ?? job.functionClass ?? 'lexical');
    const targetWords = DEFAULT_WORD_TARGETS[functionClass] ?? DEFAULT_WORD_TARGETS.lexical;
    return {
      jobId,
      paragraphId: String(slot.paragraph_id ?? slot.paragraphId),
      functionClass,
      targetWords,
      syntheticOnly: true,
    };
  });

  return {
    state: 'READER_AID_STRESS_PLAN_READY',
    syntheticOnly: true,
    aidCount: aids.length,
    syntheticWordLoad: aids.reduce((n, x) => n + x.targetWords, 0),
    aids,
    rules: [
      'Synthetic stress text measures layout capacity only; it is never reader-facing content.',
      'Research ownership and verification state are untouched.',
      'Source paragraphs remain unchanged.',
      'Final pagination must be rerun after verified reader aids replace synthetic load.',
    ],
  };
}
