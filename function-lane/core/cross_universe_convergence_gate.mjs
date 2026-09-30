// CROSS-UNIVERSE CONVERGENCE GATE
// Independent carrier universes that converge on the same specific, non-trivial detail
// deserve attention, but convergence is corroboration to investigate, not automatic truth.

export function crossUniverseConvergenceGate({findings=[]}={}) {
  const usable=findings.filter(x=>x.detail && x.universe && x.ancestryRoot && x.contextFit===true);
  const byDetail=new Map();
  for (const f of usable) {
    if (!byDetail.has(f.detail)) byDetail.set(f.detail,[]);
    byDetail.get(f.detail).push(f);
  }

  const convergences=[];
  for (const [detail,items] of byDetail) {
    const universes=[...new Set(items.map(x=>x.universe))];
    const roots=[...new Set(items.map(x=>x.ancestryRoot))];
    const unexpected=items.some(x=>x.unexpectedDetail===true);
    if (universes.length>=2 && roots.length>=2) {
      convergences.push({detail,universes,independentRoots:roots.length,unexpected});
    }
  }

  return {
    crossUniverseConvergence:{
      state:convergences.length ? 'independent-convergence-found' : 'no-qualified-convergence',
      convergences,
      rule:'INDEPENDENT CONVERGENCE IS A CLUE TO VERIFY, NOT A LICENSE TO STOP THINKING'
    }
  };
}
