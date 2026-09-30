// RELATIONSHIP BRIDGE TRIAL GATE
// Candidate bridges must actually close the original gap under the original context.
// Test each bridge against the same gap and context; clever resemblance is not enough.

export function relationshipBridgeTrialGate({gap={},context={},candidates=[]}={}) {
  const trials=candidates.filter(c=>c.bridgeId).map(c=>({
    trialId:`bridge-trial::${c.bridgeId}`,
    bridgeId:c.bridgeId,
    gap,
    context,
    universes:c.universes??[],
    doneContract:['left-connects-to-right','context-preserved','evidence-supported','no-extra-assumptions'],
    status:'ready'
  }));
  return {relationshipBridgeTrial:{
    trials,
    parallelCapacity:trials.length,
    state:trials.length?'bridge-trials-ready':'recast-relationship-fanout',
    selection:null,
    rule:'A BRIDGE MUST CLOSE THE ORIGINAL GAP IN CONTEXT; RESEMBLANCE ALONE IS NOT A BRIDGE'
  }};
}
