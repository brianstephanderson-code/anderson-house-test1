// RELATIONSHIP BRIDGE HEALTH GATE
// A proven bridge can drift as language, sources, conventions, or context change.
// Monitor real uses and quarantine only the degraded bridge/context pairing.

export function relationshipBridgeHealthGate({bridgeId='',contextKey='',recentUses=[],maxFailureRate=0.2,minUses=3}={}) {
  const measured=recentUses.filter(x=>x?.completed===true && (!x.contextKey || x.contextKey===contextKey));
  const bad=x=>x.gapClosed!==true || x.contextPreserved===false || x.evidenceSupported===false || x.extraAssumptions===true;
  const failures=measured.filter(bad);
  const failureRate=measured.length?failures.length/measured.length:null;
  let state='insufficient-history';
  if (measured.length>=minUses) state=failureRate>maxFailureRate?'bridge-degraded':'bridge-healthy';

  return {relationshipBridgeHealth:{
    bridgeId,contextKey,measuredUses:measured.length,failures:failures.length,failureRate,state,
    action:state==='bridge-degraded'?'quarantine-bridge-context-pair':'keep-current-status',
    rule:'PROVEN BRIDGES MUST KEEP PROVING THEMSELVES IN THE CONTEXTS WHERE THEY ARE USED'
  }};
}
