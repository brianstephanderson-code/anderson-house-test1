// UNCERTAINTY LAUNDERING GATE
// Detect when cautious source language becomes stronger as a claim passes through later sources.
// Confidence may stay the same or weaken without new evidence; it may strengthen only with explicit new evidence.

const strength = { unknown:0, possible:1, probable:2, asserted:3, certain:4 };

export function uncertaintyLaunderingGate(chain = []) {
  const violations = [];
  for (let i=1; i<chain.length; i++) {
    const prev = chain[i-1] ?? {};
    const curr = chain[i] ?? {};
    const before = strength[prev.claimStrength ?? 'unknown'] ?? 0;
    const after = strength[curr.claimStrength ?? 'unknown'] ?? 0;
    if (after > before && curr.newIndependentEvidence !== true) {
      violations.push({
        from: prev.id ?? `step-${i}`,
        to: curr.id ?? `step-${i+1}`,
        fromStrength: prev.claimStrength ?? 'unknown',
        toStrength: curr.claimStrength ?? 'unknown',
      });
    }
  }

  return {
    uncertaintyLaundering: {
      state: violations.length ? 'confidence-inflation' : 'clean',
      violations,
      rule: 'CERTAINTY MAY NOT INCREASE WITHOUT NEW EVIDENCE',
    },
  };
}
