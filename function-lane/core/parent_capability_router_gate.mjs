// PARENT CAPABILITY ROUTER GATE
// Reuse promoted deeper functions when a new hole matches their proven requirements/scope.
// If no parent capability fits, do not force one: return the hole to discovery.

export function parentCapabilityRouterGate({hole={},capabilities=[]}={}) {
  const needs=new Set(hole.requirements??[]);
  const fits=capabilities.filter(c=>{
    if (!c?.functionId || c.available===false) return false;
    const satisfies=c.satisfies??[];
    const requirementFit=[...needs].every(n=>satisfies.includes(n));
    const familyFit=!c.signatureFamily?.length || c.signatureFamily.includes(hole.signature);
    return requirementFit && familyFit;
  });

  return {parentCapabilityRouter:{
    holeId:hole.id??null,
    routes:fits.map(c=>({functionId:c.functionId,proof:c.proof??null,provenance:c.provenance??[]})),
    state:fits.length?'parent-capability-routes-ready':'return-hole-to-function-discovery',
    selection:null,
    rule:'REUSE A PARENT FUNCTION ONLY WHEN THE NEW HOLE FITS ITS PROVEN BOUNDARY; OTHERWISE DISCOVER AGAIN'
  }};
}
