// WORK-STEALING GATE
// Free capable bees may temporarily take ready work from another queue.
// Bees belong to the hive, not permanently to a department.

export function workStealingGate({freeBees=[],queues=[]}={}) {
  const assignments=[];
  const remaining=queues.map(q=>({...q,jobs:[...(q.jobs??[])]}));

  const ordered=[...remaining].sort((a,b)=>(b.jobs?.length??0)-(a.jobs?.length??0));
  for (const bee of freeBees) {
    const caps=new Set(bee.capabilities??[]);
    let chosen=null;
    for (const queue of ordered) {
      const index=(queue.jobs??[]).findIndex(job=>(job.requires??[]).every(r=>caps.has(r)) && job.ready!==false);
      if (index>=0) {
        const [job]=queue.jobs.splice(index,1);
        chosen={beeId:bee.id,jobId:job.id,fromQueue:queue.id};
        assignments.push(chosen);
        break;
      }
    }
  }

  return {
    workStealing:{
      assignments,
      state:assignments.length?'work-stolen':'no-safe-steal',
      rule:'FREE CAPABLE BEES MAY CROSS QUEUES; CAPABILITY AND READINESS STILL RULE'
    }
  };
}
