// LEASE / RECLAIM GATE
// A bee borrows an atomic job for a limited lease; it never owns it forever.
// If the lease expires without a valid completion, the job returns to the ready pool.

export function leaseReclaimGate({jobs=[],now=Date.now()}={}) {
  const reclaimed=[];
  const leased=[];
  const completed=[];

  for (const job of jobs) {
    if (job.state==='done') { completed.push(job.id); continue; }
    if (job.state!=='working') continue;
    const expiresAt=job.leaseExpiresAt ?? null;
    if (expiresAt!==null && now>=expiresAt) {
      reclaimed.push({jobId:job.id,formerWorkerId:job.workerId??null,action:'return-to-ready-pool'});
    } else {
      leased.push(job.id);
    }
  }

  return {
    leaseReclaim:{
      reclaimed,leased,completed,
      state:reclaimed.length?'jobs-reclaimed':'leases-healthy',
      rule:'BEES BORROW JOBS; EXPIRED WORK RETURNS TO THE HIVE'
    }
  };
}
