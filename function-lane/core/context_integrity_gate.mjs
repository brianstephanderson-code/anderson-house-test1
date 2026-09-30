// CONTEXT INTEGRITY GATE
// A quotation/snippet must keep the surrounding context needed to preserve its function.
// Matching words are not enough if paragraph/chapter context changes the meaning.

export function contextIntegrityGate({
  sourceId = '',
  snippetVerified = false,
  surroundingContextChecked = false,
  contextSupportsClaim = null,
  qualifierLost = false,
  negationLost = false,
  speakerOrAttributionLost = false,
  ironyOrQuotationRisk = false,
} = {}) {
  const distortion = qualifierLost || negationLost || speakerOrAttributionLost;
  let state = 'recast-with-context';

  if (distortion || contextSupportsClaim === false) state = 'context-mismatch';
  else if (ironyOrQuotationRisk && !surroundingContextChecked) state = 'high-risk-recast';
  else if (snippetVerified && surroundingContextChecked && contextSupportsClaim === true) state = 'context-intact';

  return {
    contextIntegrity: {
      sourceId,
      state,
      distortion: { qualifierLost, negationLost, speakerOrAttributionLost },
      ironyOrQuotationRisk,
      rule: 'MATCHING WORDS DO NOT PROVE MATCHING FUNCTION',
    },
  };
}
