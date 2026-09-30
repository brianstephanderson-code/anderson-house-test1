// CROSS-UNIVERSE MARRIAGE GATE
// Findings from different carrier universes become powerful only when we test whether
// they are actually describing the same thing, time, place and function.

export function crossUniverseMarriageGate({findings=[]}={}) {
  const universes=[...new Set(findings.map(x=>x.universe).filter(Boolean))];
  const matched=findings.filter(x=>x.sameTarget===true && x.contextFit===true);
  const conflicts=findings.filter(x=>x.conflicts===true);
  let state='needs-more-universes';
  if (conflicts.length) state='hold-contradiction';
  else if (universes.length>=2 && matched.length>=2) state='marriage-candidate';
  return {
    crossUniverseMarriage:{
      state,universes,matchedCount:matched.length,conflicts,
      rule:'DIFFERENT UNIVERSES MAY CORROBORATE ONLY AFTER IDENTITY AND CONTEXT MATCH'
    }
  };
}
