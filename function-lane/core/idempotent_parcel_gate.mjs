// IDEMPOTENT PARCEL GATE
// Retries, rescued stragglers and duplicate deliveries must not create duplicate evidence or duplicate downstream work.
// Same logical job + same result identity is accepted once.

export function idempotentParcelGate({parcels=[]}={}) {
  const seen=new Set();
  const accepted=[];
  const duplicates=[];
  const conflicts=[];

  for (const p of parcels) {
    if (!p.jobId) continue;
    const resultKey=p.resultKey ?? JSON.stringify(p.result ?? null);
    const logicalKey=`${p.jobId}::${resultKey}`;
    if (seen.has(logicalKey)) {
      duplicates.push(p);
      continue;
    }
    const prior=accepted.find(x=>x.jobId===p.jobId);
    if (prior) {
      conflicts.push({jobId:p.jobId,first:prior,next:p});
      continue;
    }
    seen.add(logicalKey);
    accepted.push(p);
  }

  return {
    idempotentParcel:{
      accepted,duplicates,conflicts,
      state:conflicts.length?'route-result-conflict':'deduplicated',
      rule:'RETRY THE WORK IF NEEDED; COUNT THE LOGICAL RESULT ONCE'
    }
  };
}
