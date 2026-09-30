// RELATIONSHIP UNIVERSE HEALTH GATE
// A proven search universe can lose usefulness as contexts, conventions, sources, or observations change.
// Monitor outcomes per universe/scope pair; quarantine only the degraded lens.

export function relationshipUniverseHealthGate({universe='',scopeKey='',recentCasts=[],minCasts=4,maxFailureRate=0.25}={}) {
  const measured=recentCasts.filter(c=>c?.completed===true && (!c.scopeKey || c.scopeKey===scopeKey));
  const bad=c=>c.validBridgeProduced!==true || c.contextPreserved===false || c.provenancePreserved===false || c.extraAssumptions===true;
  const failures=measured.filter(bad);
  const failureRate=measured.length?failures.length/measured.length:null;
  let state='insufficient-history';
  if (measured.length>=minCasts) state=failureRate>maxFailureRate?'universe-degraded':'universe-healthy';

  return {relationshipUniverseHealth:{
    universe,scopeKey,measuredCasts:measured.length,failures:failures.length,failureRate,state,
    action:state==='universe-degraded'?'quarantine-universe-scope-pair':'keep-current-status',
    rule:'A SEARCH UNIVERSE MUST KEEP EARNING ITS PLACE; QUARANTINE THE LENS, NOT THE WHOLE MAP'
  }};
}
