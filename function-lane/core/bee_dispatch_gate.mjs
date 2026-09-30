// BEE DISPATCH GATE
// Break a research job into small independent functions and dispatch only when dependencies are ready.
// Compile the flow, not the bees.

export function beeDispatchGate({jobs=[]}={}) {
  const ids=new Set(jobs.map(j=>j.id).filter(Boolean));
  const ready=[];
  const waiting=[];
  const invalid=[];

  for (const job of jobs) {
    const deps=job.dependsOn ?? [];
    const missing=deps.filter(d=>!ids.has(d));
    if (!job.id || !job.function || missing.length) {
      invalid.push({id:job.id ?? null,missingDependencies:missing});
      continue;
    }
    const blocked=deps.some(d=>jobs.find(x=>x.id===d)?.state!=='done');
    if (blocked) waiting.push(job.id);
    else if (job.state!=='done') ready.push(job.id);
  }

  return {
    beeDispatch:{
      ready,waiting,invalid,
      parallelCapacity:ready.length,
      state:invalid.length?'repair-flow':'dispatch-ready',
      rule:'KEEP THE BEES SMALL; COMPILE THE FLOW, NOT THE FUNCTIONS'
    }
  };
}
