// EXTERNAL EXPLANATION GATE
// Other glossaries, annotations, study notes and reader explanations are candidate bridges.
// Their conclusion gets no special authority: test the logic before admitting it as evidence.

export function testExternalExplanation({
  term = '',
  proposedMeaning = '',
  source = '',
  logicTrace = [],
  contextFit = 'pending',
  provenanceTraceable = false,
} = {}) {
  const hasCandidate = Boolean(term && proposedMeaning && source);
  const hasLogic = Array.isArray(logicTrace) && logicTrace.length > 0;
  const logicTestable = hasCandidate && hasLogic;

  let state = 'recast';
  if (logicTestable && contextFit === 'yes' && provenanceTraceable) state = 'candidate-supported';
  else if (logicTestable && contextFit === 'no') state = 'rejected';
  else if (logicTestable) state = 'logic-pending';

  return {
    externalExplanation: {
      term,
      proposedMeaning,
      source,
      logicTrace,
      contextFit,
      provenanceTraceable,
      state,
      rule: "OTHER PEOPLE'S ANSWERS ARE PARCELS TOO",
    },
  };
}
