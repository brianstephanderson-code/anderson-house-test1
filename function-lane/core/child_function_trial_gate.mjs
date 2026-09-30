// CHILD FUNCTION TRIAL GATE
// A proposed specialist child must solve the repeated boundary failures that created it
// without pretending to replace the healthy parent capability.

export function childFunctionTrialGate({parentFunction='',candidateChild='',boundarySignature='',trials=[],requiredCleanRuns=3}={}) {
  const measured=trials.filter(t=>t?.completed===true && (!t.signature || t.signature===boundarySignature));
  const clean=t=>t.holeClosed===true && t.requirementsSatisfied===true && t.contextPreserved===true && t.provenancePreserved===true && t.extraAssumptions!==true;
  const cleanRuns=measured.filter(clean).length;
  const proven=cleanRuns>=requiredCleanRuns;
  return {childFunctionTrial:{
    parentFunction,candidateChild,boundarySignature,completedTrials:measured.length,cleanRuns,requiredCleanRuns,
    state:proven?'child-function-proven':'child-function-unproven',
    action:proven?'attach-child-to-parent':'keep-testing-or-recast-child',
    parentAction:'keep-healthy-parent-active',
    rule:'PROVE THE CHILD ON THE PARENT EDGE THAT CREATED IT; SPECIALIZE THE FAILURE WITHOUT REPLACING THE HEALTHY PARENT'
  }};
}
