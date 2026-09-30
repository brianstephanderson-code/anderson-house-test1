// CAPABILITY TRIAL GATE
// A claimed or newly attached skill is not trusted merely because it exists.
// Give the bee a controlled atomic test and verify the capability against the same DONE contract.

export function capabilityTrialGate({beeId='',capability='',trials=[],requiredCleanRuns=2}={}) {
  const completed=trials.filter(t=>t?.completed===true);
  const clean=t=>t.doneSatisfied===true && t.evidenceIntegrity===true && t.contextPreserved===true && (t.errors??[]).length===0;
  const cleanRuns=completed.filter(clean).length;
  const allClean=completed.length>=requiredCleanRuns && completed.every(clean);

  return {
    capabilityTrial:{
      beeId,capability,completedTrials:completed.length,cleanRuns,requiredCleanRuns,
      state:allClean?'capability-proven':'capability-unproven',
      action:allClean?'add-to-capability-profile':'do-not-route-live-work',
      rule:'A SKILL IS NOT A CAPABILITY UNTIL THE BEE PROVES IT ON THE FUNCTION'
    }
  };
}
