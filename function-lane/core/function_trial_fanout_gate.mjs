// FUNCTION TRIAL FANOUT GATE
// Give every surviving candidate function the same STATE parcel and same DONE contract.
// Run candidates in parallel so fit is demonstrated by transformation, not by description or popularity.

export function functionTrialFanoutGate({stateParcel=null,doneContract=null,candidates=[]}={}) {
  const valid=candidates.filter(c=>c.functionId && c.verifiedForTrial!==false);
  const trials=valid.map(c=>({
    trialId:`trial::${c.functionId}`,
    functionId:c.functionId,
    stateParcel,
    doneContract,
    status:'ready',
    measurementContract:['doneSatisfied','evidenceIntegrity','contextPreserved','errors','elapsed']
  }));

  return {
    functionTrialFanout:{
      trials,
      parallelCapacity:trials.length,
      state:stateParcel && doneContract && trials.length ? 'parallel-trials-ready' : 'repair-trial-inputs',
      selection:null,
      rule:'SAME STATE, SAME DONE, DIFFERENT FUNCTIONS; LET OBSERVED TRANSFORMATION SUPPLY THE EVIDENCE'
    }
  };
}
