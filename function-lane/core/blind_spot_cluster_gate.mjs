// BLIND-SPOT CLUSTER GATE
// Repeated unresolved gap signatures may be surface forms of the same deeper missing relationship.
// Cluster by shared unmet requirements before opening separate universe-discovery jobs.

export function blindSpotClusterGate({blindSpots=[]}={}) {
  const clusters=new Map();
  for (const b of blindSpots) {
    const needs=[...(b.unmetRequirements??[])].filter(Boolean).sort();
    const key=needs.length?needs.join('|'):`signature:${b.signature??'unknown'}`;
    if (!clusters.has(key)) clusters.set(key,{clusterKey:key,unmetRequirements:needs,signatures:[],examples:[],count:0});
    const c=clusters.get(key);
    if (b.signature) c.signatures.push(b.signature);
    c.examples.push(...(b.examples??[]));
    c.count+=b.count??1;
  }
  const grouped=[...clusters.values()].map(c=>({...c,signatures:[...new Set(c.signatures)],examples:[...new Set(c.examples)],action:'cast-one-deeper-universe-discovery'}));
  return {blindSpotCluster:{
    clusters:grouped,
    state:grouped.length?'deeper-patterns-ready':'no-blind-spots-to-cluster',
    rule:'CLUSTER FAILURES BY THE FUNCTION THEY ARE MISSING; MANY SURFACE HOLES MAY BE ONE DEEPER HOLE'
  }};
}
