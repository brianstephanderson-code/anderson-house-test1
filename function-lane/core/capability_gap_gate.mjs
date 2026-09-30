// CAPABILITY GAP GATE
// When no free bee can perform an atomic function, describe the missing capability instead of binding the job to a person.
// The gap itself becomes an O-search target: train, attach tool, route, or find another capable bee.

export function capabilityGapGate({job={},bees=[]}={}) {
  const required=[...(job.requires??[])];
  const analyses=bees.map(bee=>{
    const has=new Set(bee.capabilities??[]);
    const missing=required.filter(r=>!has.has(r));
    return {beeId:bee.id??null,missing,fit:missing.length===0,state:bee.state??'unknown'};
  });
  const capable=analyses.filter(x=>x.fit);
  const missingUniverse=[...new Set(analyses.flatMap(x=>x.missing))];

  return {
    capabilityGap:{
      jobId:job.id??null,required,capableBees:capable.map(x=>x.beeId),analyses,missingUniverse,
      state:capable.length?'capability-present':'open-capability-o-gate',
      candidateRepairs:['route-to-capable-bee','attach-approved-tool','train-and-test-capability','find-external-capability'],
      rule:'WHEN THE BEE CANNOT FIT THE FUNCTION, SEARCH FOR THE MISSING CAPABILITY; DO NOT FORCE THE BEE'
    }
  };
}
