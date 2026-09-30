// FUNCTION REQUALIFICATION GATE
// Degraded functions are quarantined, not forgotten.
// Re-test them on controlled parcels; restore only after a clean recovery streak.

export function functionRequalificationGate({functionId='',quarantined=false,retestRuns=[],requiredCleanRuns=3}={}) {
  const completed=retestRuns.filter(r=>r?.completed===true);
  const clean=r=>r.doneSatisfied===true && r.evidenceIntegrity===true && r.contextPreserved===true && (r.errors??[]).length===0;
  let streak=0;
  for (let i=completed.length-1;i>=0;i--) {
    if (!clean(completed[i])) break;
    streak++;
  }

  let action='not-quarantined';
  if (quarantined) action=streak>=requiredCleanRuns?'restore-to-proven-pool':'keep-quarantined';

  return {
    functionRequalification:{
      functionId,quarantined,completedRetests:completed.length,cleanRecoveryStreak:streak,
      requiredCleanRuns,action,
      rule:'DEGRADED IS NOT DEAD; REPROVE THE FUNCTION BEFORE RESTORING TRUST'
    }
  };
}
