// VERIFICATION GATE
// Every Bridge Search return must pass here before Warehouse admission.
// Finding a bridge and verifying a bridge are separate functions.

export function verificationGate({ claim, sources = [], contextFit = 'pending', contradictionCheck = 'pending' } = {}) {
  if (!claim) throw new Error('claim is required');

  const normalized = sources.map((s = {}) => ({
    id: s.id ?? null,
    origin: s.origin ?? null,
    kind: s.kind ?? 'unknown',
    supportsExactClaim: s.supportsExactClaim ?? 'pending',
    provenanceChecked: s.provenanceChecked ?? false,
  }));

  const independentOrigins = new Set(normalized.map((s) => s.origin).filter(Boolean));
  const hasSupportingSource = normalized.some((s) => s.supportsExactClaim === true);
  const provenanceReady = normalized.length > 0 && normalized.every((s) => s.provenanceChecked === true);

  let state = 'recast';
  if (hasSupportingSource && provenanceReady && contextFit === true && contradictionCheck === true) {
    state = independentOrigins.size >= 2 ? 'verified' : 'single-road';
  } else if (hasSupportingSource) {
    state = 'uncertain';
  }

  return {
    verification: {
      claim,
      sources: normalized,
      independentOriginCount: independentOrigins.size,
      contextFit,
      contradictionCheck,
      state,
      rule: 'FIND BRIDGE != VERIFY BRIDGE; repeated copies of one origin count as one evidence road',
    },
  };
}
