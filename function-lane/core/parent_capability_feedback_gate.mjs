// PARENT CAPABILITY FEEDBACK GATE
// Reuse is also a new experiment. Feed each routed hole back into the capability's evidence.
// Success strengthens its proven family; failure exposes a boundary or a possible new child function.

export function parentCapabilityFeedbackGate({functionId='',uses=[]}={}) {
  const completed=uses.filter(u=>u?.completed===true);
  const good=u=>u.holeClosed===true && u.contextPreserved===true && u.provenancePreserved===true && u.extraAssumptions!==true;
  const successes=completed.filter(good);
  const failures=completed.filter(u=>!good(u));
  const learnedSignatures=[...new Set(successes.map(u=>u.signature).filter(Boolean))];
  const boundarySignals=[...new Set(failures.map(u=>u.signature).filter(Boolean))];

  return {parentCapabilityFeedback:{
    functionId,
    completedUses:completed.length,
    successes:successes.length,
    failures:failures.length,
    learnedSignatures,
    boundarySignals,
    state:failures.length?'boundary-review-required':'capability-evidence-strengthened',
    rule:'EVERY REUSE IS ALSO A TEST; SUCCESS EXPANDS EVIDENCE, FAILURE TEACHES THE FUNCTION WHERE IT STOPS'
  }};
}
