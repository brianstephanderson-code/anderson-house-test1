// HANDOFF GATE
// Verify the joint between workers, not merely each worker.
// Uncertainty, contradictions, provenance and claim boundaries must survive handoff.

export function handoffGate({
  parcel = {},
  required = ['stateIn','resultOut','nextFunction'],
} = {}) {
  const missing = required.filter((key) => parcel[key] == null || parcel[key] === '');
  const claims = Array.isArray(parcel.claims) ? parcel.claims : [];
  const split = claims.length > 1 && parcel.atomic !== true;
  const uncertaintyLost = parcel.hadUncertainty === true && !parcel.uncertainty;
  const contradictionLost = parcel.hadContradiction === true && !parcel.contradiction;
  const provenanceLost = parcel.hadProvenance === true && (!Array.isArray(parcel.provenance) || parcel.provenance.length === 0);
  const boundaryLost = parcel.hadBoundary === true && !parcel.claimBoundary;
  const informationLoss = uncertaintyLost || contradictionLost || provenanceLost || boundaryLost;

  let state = 'accept';
  if (split) state = 'split';
  else if (missing.length || informationLoss) state = 'return';
  else if (parcel.sufficient === false) state = 'recast';

  return {
    handoff: {
      state,
      missing,
      informationLoss: { uncertaintyLost, contradictionLost, provenanceLost, boundaryLost },
      rule: 'UNCERTAINTY MUST SURVIVE THE HANDOFF',
    },
  };
}
