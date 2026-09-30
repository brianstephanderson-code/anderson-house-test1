// FUNCTION HEALTH GATE
// A function being proven once does not make it permanently healthy.
// Watch recent executions for contract failures and remove degraded roads from active routing.

export function functionHealthGate({functionId='',recentRuns=[],maxFailureRate=0.2,minRuns=3}={}) {
  const measured=recentRuns.filter(r=>r && r.completed===true);
  const failures=measured.filter(r=>r.doneSatisfied!==true || r.evidenceIntegrity===false || r.contextPreserved===false || (r.errors??[]).length>0);
  const failureRate=measured.length ? failures.length/measured.length : null;

  let state='insufficient-history';
  if (measured.length>=minRuns) state=failureRate>maxFailureRate?'degraded':'healthy';

  return {
    functionHealth:{
      functionId,
      measuredRuns:measured.length,
      failures:failures.length,
      failureRate,
      state,
      routingAction:state==='degraded'?'remove-from-active-pool':'keep-current-status',
      rule:'PROVEN ONCE IS NOT PROVEN FOREVER; KEEP TESTING THE FUNCTION IN USE'
    }
  };
}
