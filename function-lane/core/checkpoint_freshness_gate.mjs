// CHECKPOINT FRESHNESS GATE
// A verified checkpoint can become stale if inputs, rules, evidence, or the function contract change before handoff.
// Resume only when the checkpoint still matches the current job state.

export function checkpointFreshnessGate({checkpoint={},current={}}={}) {
  const checks={
    verified:checkpoint.verified===true,
    inputVersion:checkpoint.inputVersion===current.inputVersion,
    contractVersion:checkpoint.contractVersion===current.contractVersion,
    ruleVersion:checkpoint.ruleVersion===current.ruleVersion,
    evidenceVersion:checkpoint.evidenceVersion===current.evidenceVersion
  };
  const stale=Object.entries(checks).filter(([,ok])=>!ok).map(([name])=>name);
  return {checkpointFreshness:{
    checkpointId:checkpoint.id??null,checks,stale,
    state:stale.length?'checkpoint-stale':'checkpoint-current',
    action:stale.length?'revalidate-from-last-safe-joint':'allow-resume',
    rule:'VERIFIED YESTERDAY IS NOT VERIFIED NOW IF THE JOB STATE CHANGED'
  }};
}
