// UNIVERSE PORTFOLIO GAP GATE
// Inspect the whole proven universe pool for blind spots before a specific search fails.
// Repeated unresolved gap types reveal missing search lenses worth discovering proactively.

export function universePortfolioGapGate({unresolvedGaps=[],provenUniverses=[]}={}) {
  const counts=new Map();
  for (const g of unresolvedGaps) {
    const signature=g?.signature;
    if (!signature) continue;
    if (!counts.has(signature)) counts.set(signature,{signature,count:0,examples:[],failedUniverses:new Set()});
    const x=counts.get(signature);
    x.count++;
    if (g.id) x.examples.push(g.id);
    for (const u of (g.triedUniverses??[])) x.failedUniverses.add(u);
  }
  const blindSpots=[...counts.values()].filter(x=>x.count>=2).map(x=>({
    signature:x.signature,count:x.count,examples:x.examples,failedUniverses:[...x.failedUniverses],action:'open-universe-discovery'
  }));

  return {universePortfolioGap:{
    provenUniverseCount:provenUniverses.filter(u=>u?.proven===true).length,
    blindSpots,
    state:blindSpots.length?'portfolio-blind-spots-found':'no-repeated-blind-spot-yet',
    rule:'DO NOT WAIT FOR THE NEXT FAILURE; REPEATED UNRESOLVED GAP SHAPES REVEAL MISSING SEARCH UNIVERSES'
  }};
}
