// DEEPER-HOLE FUNCTION TRIAL GATE
// A candidate deeper function must close several different surface holes in the cluster.
// One success is not enough: prove the shared function actually explains the cluster.

export function deeperHoleFunctionTrialGate({candidateFunction='',requirements=[],trials=[],requiredDistinctSignatures=2}={}) {
  const completed=trials.filter(t=>t?.completed===true);
  const clean=t=>t.holeClosed===true && t.requirementsSatisfied===true && t.contextPreserved===true && t.provenancePreserved===true && t.extraAssumptions!==true;
  const cleanTrials=completed.filter(clean);
  const signatures=new Set(cleanTrials.map(t=>t.signature).filter(Boolean));
  const proven=signatures.size>=requiredDistinctSignatures;
  return {deeperHoleFunctionTrial:{
    candidateFunction,requirements,
    completedTrials:completed.length,
    cleanTrials:cleanTrials.length,
    distinctClosedSignatures:signatures.size,
    state:proven?'deeper-function-proven':'deeper-function-unproven',
    action:proven?'promote-shared-function':'keep-testing-or-recast',
    rule:'A DEEPER FUNCTION MUST CLOSE DIFFERENT SURFACE HOLES; ONE SUCCESS DOES NOT EXPLAIN THE CLUSTER'
  }};
}
