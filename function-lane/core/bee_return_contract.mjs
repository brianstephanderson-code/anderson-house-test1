// BEE RETURN CONTRACT
// Every atomic worker returns the same small parcel shape so downstream functions do not care who produced it.

export function beeReturnContract({
  jobId='',
  functionName='',
  workerId='',
  state='',
  result=null,
  evidenceRefs=[],
  confidence='unknown',
  caveats=[],
  nextSuggestedFunction='',
}={}) {
  const allowedStates=new Set(['done','not-found','conflict','recast']);
  const missing=[];
  if (!jobId) missing.push('jobId');
  if (!functionName) missing.push('functionName');
  if (!workerId) missing.push('workerId');
  if (!allowedStates.has(state)) missing.push('validState');
  if (state==='done' && result===null) missing.push('result');

  return {
    beeReturn:{
      accepted:missing.length===0,
      missing,
      parcel:{jobId,functionName,workerId,state,result,evidenceRefs,confidence,caveats,nextSuggestedFunction},
      rule:'STANDARDIZE THE RETURN PARCEL, NOT THE WORKER'
    }
  };
}
