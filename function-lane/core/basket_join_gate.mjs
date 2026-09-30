// BASKET / JOIN GATE
// A downstream function waits only for the parcels it actually requires.
// Unrelated bees may keep working; the whole swarm never becomes a global barrier.

export function basketJoinGate({requiredJobIds=[],parcels=[]}={}) {
  const byJob=new Map(parcels.map(p=>[p.jobId,p]));
  const missing=requiredJobIds.filter(id=>!byJob.has(id));
  const arrived=requiredJobIds.filter(id=>byJob.has(id));
  const blockers=arrived.filter(id=>['conflict','recast'].includes(byJob.get(id)?.state));
  const usable=arrived.filter(id=>['done','not-found'].includes(byJob.get(id)?.state));

  let state='waiting-required-parcels';
  if (blockers.length) state='route-blockers';
  else if (missing.length===0) state='join-ready';

  return {
    basketJoin:{
      state,requiredJobIds,arrived,missing,usable,blockers,
      unrelatedParcelCount:parcels.filter(p=>!requiredJobIds.includes(p.jobId)).length,
      rule:'WAIT FOR REQUIRED PARCELS, NOT FOR THE WHOLE SWARM'
    }
  };
}
