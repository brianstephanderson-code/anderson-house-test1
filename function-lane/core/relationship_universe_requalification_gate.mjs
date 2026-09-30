// RELATIONSHIP UNIVERSE REQUALIFICATION GATE
// A quarantined universe/scope pair may return after controlled retests across distinct gaps.
// Restore the lens only inside the same scope where it was repaired.

export function relationshipUniverseRequalificationGate({universe='',scopeKey='',quarantined=false,retests=[],requiredCleanGaps=3}={}) {
  const measured=retests.filter(r=>r?.completed===true && (!r.scopeKey || r.scopeKey===scopeKey));
  const clean=r=>r.validBridgeProduced===true && r.contextPreserved===true && r.provenancePreserved===true && r.extraAssumptions!==true && (r.errors??[]).length===0;
  const cleanRuns=measured.filter(clean);
  const distinctCleanGaps=new Set(cleanRuns.map(r=>r.gapId).filter(Boolean)).size;
  const recovered=distinctCleanGaps>=requiredCleanGaps;
  let action='universe-not-quarantined';
  if (quarantined) action=recovered?'restore-universe-scope-pair':'keep-universe-scope-quarantined';

  return {relationshipUniverseRequalification:{
    universe,scopeKey,quarantined,completedRetests:measured.length,distinctCleanGaps,requiredCleanGaps,action,
    rule:'REPROVE THE LENS ACROSS DIFFERENT GAPS IN THE SAME SCOPE BEFORE RESTORING IT'
  }};
}
