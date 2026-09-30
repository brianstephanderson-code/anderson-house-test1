// CAPABILITY BOUNDARY SPLIT GATE
// Repeated failures at one edge of a parent capability may indicate a distinct child function.
// Split only the failing boundary pattern; keep the healthy parent intact.

export function capabilityBoundarySplitGate({functionId='',boundarySignals=[],minRepeats=2}={}) {
  const groups=new Map();
  for (const s of boundarySignals) {
    const key=s?.signature;
    if (!key) continue;
    if (!groups.has(key)) groups.set(key,{signature:key,count:0,requirements:new Set(),examples:[]});
    const g=groups.get(key); g.count++;
    for (const r of (s.requirements??[])) g.requirements.add(r);
    if (s.id) g.examples.push(s.id);
  }
  const childCandidates=[...groups.values()].filter(g=>g.count>=minRepeats).map(g=>({
    parentFunction:functionId,
    boundarySignature:g.signature,
    repeats:g.count,
    requirements:[...g.requirements],
    examples:g.examples,
    action:'open-child-function-discovery'
  }));
  return {capabilityBoundarySplit:{
    functionId,childCandidates,
    state:childCandidates.length?'child-function-candidates-found':'keep-observing-boundary',
    parentAction:'keep-healthy-parent-active',
    rule:'WHEN ONE EDGE REPEATEDLY FAILS, GROW A CHILD FUNCTION FOR THAT EDGE; DO NOT BREAK THE HEALTHY PARENT'
  }};
}
