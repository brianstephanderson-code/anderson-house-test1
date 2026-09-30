// ROUTE FAILURE / FALLBACK GATE
// If the active proven function becomes unavailable or fails its contract,
// immediately expose other compatible proven roads before reopening O-search.

export function routeFailureFallbackGate({activeFunctionId='',routePool=[],stateNeeds=[],failure=null}={}) {
  const needs=new Set(stateNeeds);
  const alternatives=routePool.filter(f=>{
    if (!f.functionId || f.functionId===activeFunctionId || f.available===false || f.qualified!==true) return false;
    const supports=new Set(f.supports??[]);
    return [...needs].every(n=>supports.has(n));
  });

  let action='continue-active-route';
  if (failure) action=alternatives.length?'reroute-to-proven-alternative':'open-o-gate';

  return {
    routeFailureFallback:{
      activeFunctionId,
      failure,
      alternatives:alternatives.map(f=>f.functionId),
      action,
      rule:'WHEN A ROAD FAILS, TRY ANOTHER PROVEN FIT BEFORE INVENTING A NEW ROAD'
    }
  };
}
