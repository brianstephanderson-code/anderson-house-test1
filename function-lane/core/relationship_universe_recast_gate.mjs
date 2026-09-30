// RELATIONSHIP-UNIVERSE RECAST GATE
// When a bridge cannot be found in the current relationship universe, do not keep forcing the same cast.
// Recast the SAME gap through materially different relationship universes.

export function relationshipUniverseRecastGate({gap={},triedUniverses=[],candidateUniverses=[]}={}) {
  const tried=new Set(triedUniverses);
  const queue=candidateUniverses.filter(u=>u && !tried.has(u));

  return {
    relationshipUniverseRecast:{
      gap,
      triedUniverses:[...tried],
      recastQueue:queue,
      state:queue.length?'recast-in-new-universe':'open-new-universe-search',
      examples:['semantic','phonetic','orthographic','structural','temporal','cultural','functional','causal','analogical'],
      rule:'KEEP THE GAP; CHANGE THE RELATIONSHIP UNIVERSE'
    }
  };
}
