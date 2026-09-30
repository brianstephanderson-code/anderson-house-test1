// HANDOFF-GAP O-GATE
// When two proven functions cannot exchange a parcel cleanly, treat the JOINT as the missing function.
// Describe what must be preserved/transformed at the boundary, then cast for a bridge/adapter function.

export function handoffGapOGate({fromFunction={},toFunction={},handoff={}}={}) {
  const required=[];
  if (handoff.statePreserved!==true) required.push('preserve-state');
  if (handoff.evidencePreserved!==true) required.push('preserve-evidence');
  if (handoff.contextPreserved!==true) required.push('preserve-context');
  if (handoff.nextCapabilityMatches!==true) required.push('translate-next-capability-contract');

  return {
    handoffGapO:{
      fromFunction:fromFunction.id??null,
      toFunction:toFunction.id??null,
      hole:{requires:required},
      state:required.length?'cast-for-handoff-function':'joint-fits',
      candidateFunctionTypes:['adapter','translator','normalizer','evidence-wrapper','context-carrier'],
      rule:'IF TWO GOOD FUNCTIONS DO NOT JOIN, SEARCH FOR THE MISSING FUNCTION IN THE JOINT'
    }
  };
}
