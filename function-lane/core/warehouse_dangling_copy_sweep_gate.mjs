// WAREHOUSE DANGLING COPY SWEEP GATE
// After a verified trace is married to its original, sweep temporary communication copies.
// A copy is closable only when its job loop is closed and its useful evidence is preserved in the married trace.

export function warehouseDanglingCopySweepGate({copies=[],closedJobIds=[],preservedEvidence=[]}={}) {
  const closed=new Set(closedJobIds);
  const evidence=new Set(preservedEvidence);
  const results=copies.filter(c=>c?.copyId).map(c=>{
    const loopClosed=closed.has(c.jobId);
    const evidenceSafe=(c.evidence??[]).every(e=>evidence.has(e));
    const closable=loopClosed&&evidenceSafe;
    return {copyId:c.copyId,jobId:c.jobId,closable,reason:!loopClosed?'job-loop-open':(!evidenceSafe?'evidence-not-preserved':'married-and-preserved')};
  });
  return {warehouseDanglingCopySweep:{
    close:results.filter(r=>r.closable).map(r=>r.copyId),
    hold:results.filter(r=>!r.closable).map(r=>({copyId:r.copyId,reason:r.reason})),
    state:results.some(r=>!r.closable)?'dangling-copies-remain':'copy-loops-clean',
    rule:'CLOSE TEMPORARY COPIES ONLY AFTER THEIR ORIGINAL LOOP IS CLOSED AND THEIR USEFUL EVIDENCE IS SAFE'
  }};
}
