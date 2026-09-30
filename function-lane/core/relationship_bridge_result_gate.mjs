// RELATIONSHIP BRIDGE RESULT GATE
// Qualify candidate bridges only when they close the original gap under the shared trial contract.
// Preserve failed and incomplete bridges as evidence; do not reward novelty or cross-universe popularity.

export function relationshipBridgeResultGate({results=[]}={}) {
  const qualified=[];
  const failed=[];
  const incomplete=[];

  for (const r of results) {
    const required=['bridgeId','leftConnectsToRight','contextPreserved','evidenceSupported','noExtraAssumptions'];
    if (required.some(k=>r[k]===undefined || r[k]===null)) { incomplete.push(r); continue; }
    const clean=r.leftConnectsToRight===true && r.contextPreserved===true && r.evidenceSupported===true && r.noExtraAssumptions===true;
    (clean?qualified:failed).push(r);
  }

  return {relationshipBridgeResult:{
    qualified,failed,incomplete,
    state:qualified.length?'qualified-bridges-found':'recast-relationship-universes',
    selection:null,
    rule:'QUALIFY THE BRIDGE BY GAP CLOSURE; KEEP FAILURES; DO NOT CONFUSE NOVELTY WITH FIT'
  }};
}
