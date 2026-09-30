// RELATIONSHIP UNIVERSE POOL GATE
// Keep proven relationship universes as reusable search capabilities, with scope and provenance intact.
// Route a gap only into universes whose proven scope fits the current context.

export function relationshipUniversePoolGate({universes=[],contextTags=[]}={}) {
  const context=new Set(contextTags);
  const proven=universes.filter(u=>u?.proven===true && u.available!==false);
  const compatible=proven.filter(u=>(u.scopeRequires??[]).every(tag=>context.has(tag)));

  return {relationshipUniversePool:{
    proven:proven.map(u=>u.name),
    compatible:compatible.map(u=>u.name),
    provenance:Object.fromEntries(compatible.map(u=>[u.name,u.provenance??null])),
    state:compatible.length?'universe-routes-available':'discover-or-retest-universes',
    rule:'REUSE PROVEN UNIVERSES WITHIN THEIR PROVEN SCOPE; DO NOT TURN A SEARCH LENS INTO A UNIVERSAL LAW'
  }};
}
