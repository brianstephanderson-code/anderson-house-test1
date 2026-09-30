// PERIOD FIT GATE
// A definition can be correct in one era and wrong for the author's era.
// Modern evidence may explain today's reader, but it does not automatically establish historical meaning.

export function periodFitGate({
  authorYear = null,
  evidenceYear = null,
  periodUsageVerified = false,
  semanticShiftKnown = false,
  sameSenseDemonstrated = false,
  sourceId = '',
} = {}) {
  const dated = Number.isFinite(authorYear) && Number.isFinite(evidenceYear);
  const distanceYears = dated ? Math.abs(evidenceYear - authorYear) : null;

  let state = 'recast-period-evidence';
  if (periodUsageVerified) state = 'period-fit';
  else if (semanticShiftKnown && !sameSenseDemonstrated) state = 'period-mismatch-risk';
  else if (sameSenseDemonstrated) state = 'sense-bridged-across-time';

  return {
    periodFit: {
      sourceId,
      authorYear,
      evidenceYear,
      distanceYears,
      state,
      rule: 'CORRECT SOMEWHERE IN TIME IS NOT CORRECT HERE IN TIME',
    },
  };
}
