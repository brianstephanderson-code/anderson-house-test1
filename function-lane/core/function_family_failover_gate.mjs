// FUNCTION FAMILY FAILOVER GATE
// When the preferred family member is unavailable or degraded, hand the job to another proven fit.
// If none fits, preserve the job and return it to discovery rather than forcing a weak worker.

export function functionFamilyFailoverGate({job={},preferredFunction='',members=[]}={}) {
  const needs=job.requirements??[];
  const fit=m=>m?.proven===true && m.available!==false && m.health!=='degraded' && (m.satisfies??[]).every(r=>needs.includes(r)) && (!(m.signatures??[]).length || m.signatures.includes(job.signature));
  const preferred=members.find(m=>m.functionId===preferredFunction);
  if (preferred && fit(preferred)) return {functionFamilyFailover:{jobId:job.id??null,route:preferredFunction,mode:'preferred',state:'routed',rule:'KEEP THE JOB MOVING WITH A PROVEN FIT; NEVER FORCE A DEGRADED WORKER'}};
  const alternates=members.filter(m=>m.functionId!==preferredFunction && fit(m));
  return {functionFamilyFailover:{
    jobId:job.id??null,
    route:alternates.length===1?alternates[0].functionId:null,
    candidates:alternates.map(m=>m.functionId),
    mode:alternates.length?'failover':'none',
    state:alternates.length?'routed':'hold-job-and-open-discovery',
    rule:'KEEP THE JOB MOVING WITH A PROVEN FIT; NEVER FORCE A DEGRADED WORKER'
  }};
}
