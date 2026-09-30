// HANDOFF COMPLETION RECONCILIATION GATE
// At job completion, reconcile the original DONE contract against work produced across every worker/handoff.
// Worker changes must disappear from the customer's view: one job in, one verified DONE out.

export function handoffCompletionReconciliationGate({doneContract=[],completedUnits=[],evidenceByUnit={}}={}) {
  const completed=new Set(completedUnits);
  const missing=doneContract.filter(unit=>!completed.has(unit));
  const withoutEvidence=doneContract.filter(unit=>completed.has(unit) && !(evidenceByUnit[unit]?.length));
  const extras=completedUnits.filter(unit=>!doneContract.includes(unit));
  const closed=!missing.length&&!withoutEvidence.length;
  return {handoffCompletionReconciliation:{
    missing,withoutEvidence,extras,
    state:closed?'job-done-verified':'job-not-closed',
    action:closed?'return-done':'reopen-only-missing-or-unverified-units',
    rule:'RECONCILE THE WHOLE JOB AGAINST THE ORIGINAL DONE; HANDOFFS MAY CHANGE WORKERS, NEVER THE PROMISED RESULT'
  }};
}
