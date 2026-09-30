// FUNCTION ROUTE POOL GATE
// Keep multiple proven functions available for the same DONE contract.
// Route by current STATE constraints; do not hard-wire one permanent road.

export function functionRoutePoolGate({qualifiedFunctions=[],stateNeeds=[]}={}) {
  const needs=new Set(stateNeeds);
  const available=qualifiedFunctions.filter(f=>f.available!==false);
  const compatible=available.filter(f=>{
    const supports=new Set(f.supports??[]);
    return [...needs].every(n=>supports.has(n));
  });

  return {
    functionRoutePool:{
      available:available.map(f=>f.functionId),
      compatible:compatible.map(f=>f.functionId),
      state:compatible.length?'routes-available':'open-o-gate',
      permanentWinner:null,
      rule:'KEEP PROVEN ROADS; ROUTE BY CURRENT STATE, NOT BY PERMANENT FAVORITE'
    }
  };
}
