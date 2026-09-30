// DEEPER-HOLE FUNCTION CAST GATE
// Once surface failures cluster around the same unmet requirement, search for the FUNCTION that would close the deeper hole.
// Search function-first, not product/name-first.

export function deeperHoleFunctionCastGate({cluster={},candidateFunctions=[]}={}) {
  const requirements=[...(cluster.unmetRequirements??[])];
  const casts=candidateFunctions.filter(Boolean).map(fn=>({
    candidateFunction:fn,
    mustSatisfy:requirements,
    testAgainstSignatures:[...(cluster.signatures??[])],
    examples:[...(cluster.examples??[])],
    doneContract:'close-multiple-surface-holes-with-one-repeatable-function'
  }));
  return {deeperHoleFunctionCast:{
    clusterKey:cluster.clusterKey??null,
    casts,
    state:casts.length?'function-casts-ready':'open-function-discovery',
    selection:null,
    rule:'WHEN MANY HOLES SHARE ONE MISSING NEED, CAST FOR THE FUNCTION THAT SATISFIES THE NEED'
  }};
}
