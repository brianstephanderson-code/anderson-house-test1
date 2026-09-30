// CAPABILITY REQUALIFICATION GATE
// A suspended skill may return without replacing the bee.
// Retest only the affected capability on controlled parcels and restore after a clean streak.

export function capabilityRequalificationGate({beeId='',capability='',suspended=false,retestRuns=[],requiredCleanRuns=2}={}) {
  const completed=retestRuns.filter(r=>r?.completed===true && (!r.capability || r.capability===capability));
  const clean=r=>r.doneSatisfied===true && r.evidenceIntegrity===true && r.contextPreserved===true && (r.errors??[]).length===0;
  let streak=0;
  for (let i=completed.length-1;i>=0;i--) {
    if (!clean(completed[i])) break;
    streak++;
  }

  let action='capability-not-suspended';
  if (suspended) action=streak>=requiredCleanRuns?'restore-capability':'keep-capability-suspended';

  return {
    capabilityRequalification:{
      beeId,capability,suspended,completedRetests:completed.length,cleanRecoveryStreak:streak,requiredCleanRuns,action,
      beeStatus:'retain-other-proven-capabilities',
      rule:'REPAIR AND REPROVE THE SKILL; RESTORE IT WITHOUT REBUILDING THE BEE'
    }
  };
}
