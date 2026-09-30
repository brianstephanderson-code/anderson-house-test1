// RELATIONSHIP UNIVERSE DISCOVERY GATE
// If known relationship universes fail, search for NEW kinds of relationship rather than endlessly recasting familiar ones.
// The output is candidate universe definitions, not bridges yet.

export function relationshipUniverseDiscoveryGate({gap={},knownUniverses=[],observations=[]}={}) {
  const known=new Set(knownUniverses);
  const candidates=[];
  for (const o of observations) {
    const name=o?.proposedUniverse;
    if (!name || known.has(name)) continue;
    candidates.push({
      universe:name,
      clue:o.clue??null,
      relationRule:o.relationRule??null,
      provenance:o.provenance??null,
      status:'unproven-universe'
    });
  }
  return {relationshipUniverseDiscovery:{
    gap,
    candidates,
    state:candidates.length?'universe-trials-required':'widen-observation-net',
    rule:'WHEN KNOWN UNIVERSES FAIL, SEARCH FOR A NEW KIND OF RELATIONSHIP; DO NOT FORCE THE OLD MAP'
  }};
}
