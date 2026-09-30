// HANDOFF DUPLICATE-WORK GATE
// After a verified handoff, prevent the replacement from redoing already accepted work unless that work was explicitly invalidated.

export function handoffDuplicateWorkGate({completedWork=[],plannedWork=[],invalidatedWork=[]}={}) {
  const done=new Set(completedWork);
  const invalid=new Set(invalidatedWork);
  const duplicates=plannedWork.filter(step=>done.has(step) && !invalid.has(step));
  const legitimateRedo=plannedWork.filter(step=>done.has(step) && invalid.has(step));
  const remaining=plannedWork.filter(step=>!done.has(step) || invalid.has(step));
  return {handoffDuplicateWork:{
    duplicates,legitimateRedo,remaining,
    state:duplicates.length?'duplicate-work-blocked':'plan-clean',
    action:duplicates.length?'remove-accepted-work-from-plan':'release-plan',
    rule:'DO NOT PAY TWICE FOR VERIFIED WORK; REDO IT ONLY WHEN THE OLD RESULT HAS BEEN EXPLICITLY INVALIDATED'
  }};
}
