// HANDOFF TRACE COMPRESSION GATE
// Many worker changes can create noisy internal history. Compress the chain into one auditable job trace
// while preserving every verified checkpoint, evidence reference, and ownership change.

export function handoffTraceCompressionGate({jobId='',events=[]}={}) {
  const ordered=[...events].filter(e=>e?.sequence!=null).sort((a,b)=>a.sequence-b.sequence);
  const checkpoints=ordered.filter(e=>e.type==='checkpoint' && e.verified===true).map(e=>e.id).filter(Boolean);
  const handoffs=ordered.filter(e=>e.type==='handoff').map(e=>({from:e.from,to:e.to,checkpointId:e.checkpointId??null}));
  const evidence=[...new Set(ordered.flatMap(e=>e.evidence??[]))];
  const owners=[...new Set(ordered.flatMap(e=>[e.owner,e.from,e.to]).filter(Boolean))];
  const complete=ordered.length===events.length && handoffs.every(h=>h.from&&h.to&&h.checkpointId);
  return {handoffTraceCompression:{
    jobId,trace:{checkpoints,handoffs,evidence,owners,eventCount:ordered.length},
    state:complete?'compressed-trace-ready':'trace-gap',
    action:complete?'archive-one-job-trace':'reconcile-trace-before-archive',
    rule:'COMPRESS THE NOISE, NOT THE PROOF; ONE JOB TRACE MUST STILL SHOW EVERY VERIFIED HANDOFF'
  }};
}
