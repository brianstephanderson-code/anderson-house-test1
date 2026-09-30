// WAREHOUSE TRACE MARRIAGE GATE
// A completed job trace must marry back to exactly one original job before archival.
// Copies may travel; the warehouse closes the loop by linking them to their source.

export function warehouseTraceMarriageGate({trace={},originalJobs=[]}={}) {
  const matches=originalJobs.filter(j=>j?.jobId && j.jobId===trace.jobId);
  const original=matches.length===1?matches[0]:null;
  const proofReady=(trace.checkpoints??[]).length>0 && (trace.evidence??[]).length>0;
  const married=!!original && proofReady;
  return {warehouseTraceMarriage:{
    jobId:trace.jobId??null,
    originalMatches:matches.length,
    originalRef:original?.originalRef??null,
    proofReady,
    state:married?'loop-closed':'marriage-gap',
    action:married?'archive-with-original':'hold-trace-and-reconcile-original',
    rule:'COPIES MAY TRAVEL THROUGH THE HIVE; THE WAREHOUSE CLOSES THE LOOP BY MARRYING THE VERIFIED TRACE BACK TO ONE ORIGINAL'
  }};
}
