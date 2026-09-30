// CAPABILITY HEALTH GATE
// A bee proving a skill once does not grant that capability forever.
// Watch real executions of that capability and suspend only the drifting skill, not the whole bee.

export function capabilityHealthGate({beeId='',capability='',recentRuns=[],maxFailureRate=0.2,minRuns=3}={}) {
  const measured=recentRuns.filter(r=>r?.completed===true && r.capability===capability);
  const bad=r=>r.doneSatisfied!==true || r.evidenceIntegrity===false || r.contextPreserved===false || (r.errors??[]).length>0;
  const failures=measured.filter(bad);
  const failureRate=measured.length ? failures.length/measured.length : null;

  let state='insufficient-history';
  if (measured.length>=minRuns) state=failureRate>maxFailureRate?'capability-degraded':'capability-healthy';

  return {
    capabilityHealth:{
      beeId,capability,measuredRuns:measured.length,failures:failures.length,failureRate,state,
      action:state==='capability-degraded'?'suspend-capability-and-retest':'keep-capability-status',
      beeStatus:'retain-other-proven-capabilities',
      rule:'WHEN ONE SKILL DRIFTS, RETEST THE SKILL; DO NOT FIRE THE WHOLE BEE'
    }
  };
}
