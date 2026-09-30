// IN-FLIGHT FUNCTION HANDOFF GATE
// If a worker/function becomes unavailable mid-job, preserve the job state and hand off only from a verified checkpoint.
// The replacement receives the function contract, inputs, completed work, evidence, and remaining work.

export function inflightFunctionHandoffGate({job={},fromFunction='',toFunction='',checkpoint={}}={}) {
  const verified=checkpoint?.verified===true;
  const completeState=verified && checkpoint.functionContract && checkpoint.inputs && checkpoint.completedWork && checkpoint.remainingWork;
  return {inflightFunctionHandoff:{
    jobId:job.id??null,fromFunction,toFunction,
    checkpointId:checkpoint.id??null,
    handoffPacket:completeState?{
      functionContract:checkpoint.functionContract,
      inputs:checkpoint.inputs,
      completedWork:checkpoint.completedWork,
      evidence:checkpoint.evidence??[],
      remainingWork:checkpoint.remainingWork
    }:null,
    state:completeState?'handoff-ready':'checkpoint-required',
    action:completeState?'resume-with-replacement':'preserve-job-and-rebuild-checkpoint',
    rule:'A REPLACEMENT DOES NOT START THE JOB AGAIN; IT RESUMES FROM THE LAST VERIFIED STATE'
  }};
}
