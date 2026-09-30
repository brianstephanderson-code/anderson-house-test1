// HANDOFF CONTINUITY VERIFICATION GATE
// After a replacement resumes from a verified checkpoint, prove that no work, evidence, or contract meaning was lost in transit.

export function handoffContinuityVerificationGate({handoffPacket={},resumedState={}}={}) {
  const sameContract=JSON.stringify(handoffPacket.functionContract??null)===JSON.stringify(resumedState.functionContract??null);
  const sameInputs=JSON.stringify(handoffPacket.inputs??null)===JSON.stringify(resumedState.inputs??null);
  const sameCompleted=JSON.stringify(handoffPacket.completedWork??null)===JSON.stringify(resumedState.completedWork??null);
  const sameEvidence=JSON.stringify(handoffPacket.evidence??[])===JSON.stringify(resumedState.evidence??[]);
  const startsAtRemaining=JSON.stringify(handoffPacket.remainingWork??null)===JSON.stringify(resumedState.startingWork??null);
  const continuous=sameContract&&sameInputs&&sameCompleted&&sameEvidence&&startsAtRemaining;
  return {handoffContinuityVerification:{
    checks:{sameContract,sameInputs,sameCompleted,sameEvidence,startsAtRemaining},
    state:continuous?'continuity-verified':'handoff-discontinuity',
    action:continuous?'release-replacement-to-work':'stop-and-reconcile-handoff',
    rule:'A HANDOFF IS NOT DONE WHEN THE NEXT WORKER RECEIVES IT; IT IS DONE WHEN CONTINUITY IS VERIFIED'
  }};
}
