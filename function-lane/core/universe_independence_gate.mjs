// UNIVERSE INDEPENDENCE GATE
// Different carriers are not automatically independent evidence.
// A practice, interview, website and book may all descend from the same underlying source.

export function universeIndependenceGate(findings = []) {
  const roots = new Map();
  const unresolved = [];

  for (const finding of findings) {
    const id = finding.id ?? 'unknown';
    const root = finding.ancestryRoot ?? null;
    if (!root) {
      unresolved.push(id);
      continue;
    }
    if (!roots.has(root)) roots.set(root, []);
    roots.get(root).push({id, universe:finding.universe ?? 'unknown'});
  }

  const families=[...roots.entries()].map(([ancestryRoot,members])=>({
    ancestryRoot,
    members,
    universes:[...new Set(members.map(x=>x.universe))],
  }));

  const crossUniverseEchoes=families.filter(f=>f.universes.length>1);

  return {
    universeIndependence:{
      evidenceFamilies:families,
      independentRoots:families.length,
      crossUniverseEchoes,
      unresolvedAncestry:unresolved,
      state: unresolved.length ? 'trace-universe-ancestry' : 'ready',
      rule:'DIFFERENT CARRIERS DO NOT GUARANTEE DIFFERENT ORIGINS',
    }
  };
}
