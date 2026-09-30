function sameNumber(values) {
  return values.length > 0 && values.every((v) => v === values[0]);
}

export function comparePrintProfiles({
  candidates = [],
  wordCount,
  operatorEvidence = [],
  physicalProofAvailable = false,
} = {}) {
  if (!Array.isArray(candidates) || candidates.length < 2) {
    throw new Error('at least two print candidates are required');
  }
  if (!Number.isFinite(wordCount) || wordCount <= 0) {
    throw new Error('positive wordCount is required');
  }

  const normalized = candidates.map((c) => {
    if (!Array.isArray(c.trimInches) || c.trimInches.length !== 2) {
      throw new Error('candidate trimInches must be [width,height]');
    }
    if (!Number.isInteger(c.pageCount) || c.pageCount <= 0) {
      throw new Error('candidate pageCount must be a positive integer');
    }
    if (!Number.isFinite(c.printCostUsd) || c.printCostUsd <= 0) {
      throw new Error('candidate printCostUsd must be positive');
    }
    return {
      id: String(c.id ?? c.trimInches.join('x')),
      trimInches: c.trimInches,
      pageCount: c.pageCount,
      printCostUsd: c.printCostUsd,
      wordsPerPage: Math.round((wordCount / c.pageCount) * 10) / 10,
    };
  });

  const costTie = sameNumber(normalized.map((c) => c.printCostUsd));
  const evidenceIsMixed = operatorEvidence.some((x) => x.preference === 'smaller') &&
    operatorEvidence.some((x) => x.preference === 'larger');

  let state = 'COMPARE_READY';
  let decision = 'NO_FINAL_TRIM_YET';
  const missing = [];

  if (costTie) {
    missing.push('cost does not distinguish the current candidates');
  }
  if (evidenceIsMixed) {
    missing.push('operator preference is mixed and subjective');
  }
  if (!physicalProofAvailable) {
    missing.push('physical/reader proof is not yet available');
    state = 'READER_PROOF_REQUIRED';
  }

  return {
    state,
    decision,
    costTie,
    candidates: normalized,
    operatorEvidence,
    missing,
    nextState: physicalProofAvailable
      ? 'SELECT_OR_RECAST_PRINT_PROFILE'
      : 'RUN_READER_AID_STRESS_AND_PHYSICAL_PROOF',
  };
}
