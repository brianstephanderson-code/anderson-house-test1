// SAME-FUNCTION BEE FANOUT
// One function may be split across many independent casts.
// Example: TIME bees can separately inspect archives, oral transmission, objects, practice, place, language and environment.

export function beeFanoutGate({functionName='',casts=[]}={}) {
  const valid=casts.filter(c=>c.id && c.target);
  const targets=[...new Set(valid.map(c=>c.target))];
  const duplicateTargets=valid.length-targets.length;
  const dependencies=valid.filter(c=>(c.dependsOn??[]).length>0);

  return {
    beeFanout:{
      functionName,
      workerCount:valid.length,
      independentWorkerCount:valid.length-dependencies.length,
      targets,
      duplicateTargets,
      state:functionName && valid.length ? 'fanout-ready' : 'recast-fanout',
      rule:'ONE FUNCTION MAY HAVE MANY SMALL BEES CASTING DIFFERENT PARTS OF ITS UNIVERSE'
    }
  };
}
