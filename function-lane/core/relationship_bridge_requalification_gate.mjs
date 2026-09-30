// RELATIONSHIP BRIDGE REQUALIFICATION GATE
// A quarantined bridge/context pair is not dead. Re-test the same bridge in the same context boundary.
// Restore only after a clean recovery streak.

export function relationshipBridgeRequalificationGate({bridgeId='',contextKey='',quarantined=false,retests=[],requiredCleanRuns=3}={}) {
  const completed=retests.filter(r=>r?.completed===true && (!r.contextKey || r.contextKey===contextKey));
  const clean=r=>r.gapClosed===true && r.contextPreserved===true && r.evidenceSupported===true && r.extraAssumptions!==true && (r.errors??[]).length===0;
  let streak=0;
  for (let i=completed.length-1;i>=0;i--) {
    if (!clean(completed[i])) break;
    streak++;
  }
  let action='bridge-not-quarantined';
  if (quarantined) action=streak>=requiredCleanRuns?'restore-bridge-context-pair':'keep-bridge-context-quarantined';

  return {relationshipBridgeRequalification:{
    bridgeId,contextKey,quarantined,completedRetests:completed.length,cleanRecoveryStreak:streak,requiredCleanRuns,action,
    rule:'RETEST THE BRIDGE INSIDE ITS PROVEN CONTEXT; RESTORE TRUST ONLY AFTER CLEAN GAP CLOSURES'
  }};
}
