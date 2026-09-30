// STRAGGLER RESCUE GATE
// One slow bee should not hold a required join forever.
// If a job exceeds its expected window, duplicate the same atomic job to another capable bee.
// First valid return wins; late duplicate is closed, not double-counted.

export function stragglerRescueGate({jobs=[],now=Date.now(),rescueAfterMs=60000}={}) {
  const rescue=[];
  const healthy=[];
  for (const job of jobs) {
    if (job.state!=='working' || !job.startedAt) continue;
    const age=now-job.startedAt;
    if (age>=rescueAfterMs && job.requiredForJoin===true) rescue.push({jobId:job.id,ageMs:age,action:'duplicate-to-free-capable-bee'});
    else healthy.push(job.id);
  }
  return {
    stragglerRescue:{
      rescue,healthy,
      state:rescue.length?'rescue-stragglers':'no-rescue-needed',
      completionRule:'first-valid-return-wins',
      duplicateRule:'late-duplicate-close-without-double-counting',
      rule:'RESCUE THE SLOW REQUIRED JOB; DO NOT MAKE THE JOIN WAIT FOR ONE BEE'
    }
  };
}
