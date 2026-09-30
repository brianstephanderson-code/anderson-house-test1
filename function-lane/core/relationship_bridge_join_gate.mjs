// RELATIONSHIP BRIDGE JOIN GATE
// Bring candidate bridges from many relationship universes into one basket.
// Preserve universe + provenance, merge exact bridge repeats, and keep contradictions visible.

export function relationshipBridgeJoinGate({returns=[]}={}) {
  const map=new Map();
  const invalid=[];
  for (const r of returns) {
    for (const c of (r.candidates??[])) {
      if (!c.bridgeId || !c.provenance || !r.universe) { invalid.push({...c,universe:r.universe??null}); continue; }
      if (!map.has(c.bridgeId)) map.set(c.bridgeId,{bridgeId:c.bridgeId,claims:[],universes:new Set(),stances:new Set()});
      const x=map.get(c.bridgeId);
      x.claims.push({...c,universe:r.universe});
      x.universes.add(r.universe);
      if (c.stance) x.stances.add(c.stance);
    }
  }
  const candidates=[...map.values()].map(x=>({
    bridgeId:x.bridgeId,
    claims:x.claims,
    universes:[...x.universes],
    stances:[...x.stances],
    crossUniverse:x.universes.size>1,
    contested:x.stances.has('supports')&&x.stances.has('contradicts')
  }));
  return {relationshipBridgeJoin:{
    candidates,invalid,
    state:candidates.length?'bridge-test-ready':'recast-relationship-fanout',
    selection:null,
    rule:'JOIN THE BRIDGES; PRESERVE THEIR UNIVERSES, PROVENANCE, AND DISAGREEMENTS'
  }};
}
