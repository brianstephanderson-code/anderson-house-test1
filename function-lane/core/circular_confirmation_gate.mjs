// CIRCULAR CONFIRMATION GATE
// Detect evidence chains that eventually cite themselves.
// A citation loop is not independent confirmation.

export function circularConfirmationGate(edges = []) {
  const graph = new Map();
  for (const {from,to} of edges) {
    if (!from || !to) continue;
    if (!graph.has(from)) graph.set(from, []);
    graph.get(from).push(to);
  }

  const cycles = [];
  const seenCycles = new Set();

  function canonicalCycle(path) {
    const ring = path.slice(0,-1);
    const rotations = ring.map((_,i)=>[...ring.slice(i),...ring.slice(0,i)]);
    const best = rotations.map(r=>r.join('->')).sort()[0];
    return best;
  }

  function walk(node, path = []) {
    const at = path.indexOf(node);
    if (at !== -1) {
      const cycle = [...path.slice(at), node];
      const key = canonicalCycle(cycle);
      if (!seenCycles.has(key)) {
        seenCycles.add(key);
        cycles.push(cycle);
      }
      return;
    }
    for (const next of graph.get(node) ?? []) walk(next, [...path,node]);
  }

  for (const node of graph.keys()) walk(node, []);

  const members = [...new Set(cycles.flat())];
  return {
    circularConfirmation: {
      state: cycles.length ? 'circular-evidence' : 'clear',
      cycles,
      members,
      rule: 'A LOOP IS NOT A SECOND ROAD',
    },
  };
}
