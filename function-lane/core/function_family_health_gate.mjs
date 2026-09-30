// FUNCTION FAMILY HEALTH GATE
// Monitor parent and specialist children separately so one sick member does not stop the family.
// Quarantine only the degraded function and reroute its territory when another proven fit exists.

export function functionFamilyHealthGate({members=[],minUses=3,maxFailureRate=0.25}={}) {
  const health=members.filter(m=>m?.functionId).map(m=>{
    const uses=(m.uses??[]).filter(u=>u?.completed===true);
    const bad=uses.filter(u=>u.holeClosed!==true || u.contextPreserved===false || u.provenancePreserved===false || u.extraAssumptions===true);
    const rate=uses.length?bad.length/uses.length:null;
    let state='insufficient-history';
    if(uses.length>=minUses) state=rate>maxFailureRate?'degraded':'healthy';
    return {functionId:m.functionId,role:m.role??'member',uses:uses.length,failures:bad.length,failureRate:rate,state,action:state==='degraded'?'quarantine-member':'keep-active'};
  });
  return {functionFamilyHealth:{
    health,
    degraded:health.filter(h=>h.state==='degraded').map(h=>h.functionId),
    healthy:health.filter(h=>h.state==='healthy').map(h=>h.functionId),
    familyAction:health.some(h=>h.state==='healthy')?'keep-healthy-members-working':'open-family-recovery',
    rule:'MEASURE EACH FAMILY MEMBER SEPARATELY; QUARANTINE THE SICK FUNCTION, NOT THE WHOLE FAMILY'
  }};
}
