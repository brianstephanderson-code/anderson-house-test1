const HEADER_NOISE = /^(?:AMONG THE PAPERS|OF THE LATE|THE LEGEND|SLEEPY HOLLOW)$/i;
const SENTENCE_LEAK = /[.!?]\s+[A-Z]/;

export function cleanCandidateTokens(candidateTokens = {}) {
  const named = candidateTokens.namedReferences ?? [];
  const words = candidateTokens.wordCandidates ?? [];

  const namedReferences = named.map((value) => {
    let bucket = 'keep';
    let reason = 'plausible named reference';
    if (HEADER_NOISE.test(value.trim())) {
      bucket = 'reject';
      reason = 'title/header fragment';
    } else if (SENTENCE_LEAK.test(value)) {
      bucket = 'reject';
      reason = 'sentence-boundary leak';
    } else if (/^[A-Z\s]+$/.test(value) && value.length > 3) {
      bucket = 'maybe';
      reason = 'all-caps text may be heading rather than reference';
    }
    return { value, bucket, reason };
  });

  const wordCandidates = words.map((value) => ({
    value,
    bucket: 'maybe',
    reason: 'length nominates only; reader friction not yet proven',
  }));

  return {
    candidateCleaner: {
      namedReferences,
      wordCandidates,
      counts: {
        keep: namedReferences.filter((x) => x.bucket === 'keep').length,
        maybe: namedReferences.filter((x) => x.bucket === 'maybe').length + wordCandidates.length,
        reject: namedReferences.filter((x) => x.bucket === 'reject').length,
      },
    },
  };
}
