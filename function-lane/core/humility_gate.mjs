// HUMILITY GATE
// No finding, including our own prior work, receives a VIP pass.
// DONE means verified under stated evidence + machinery, not frozen forever.

export function humilityGate({
  finding = '',
  origin = 'unknown',
  evidencePassport = null,
  logicTrace = [],
  newEvidence = false,
  newTestFunction = false,
  contradiction = false,
} = {}) {
  const traceable = Boolean(finding && evidencePassport && Array.isArray(logicTrace) && logicTrace.length);
  const reopen = Boolean(newEvidence || newTestFunction || contradiction);

  let state = 'recast';
  if (traceable && reopen) state = 'reopen';
  else if (traceable) state = 'current-done';

  return {
    humilityGate: {
      finding,
      origin,
      traceable,
      reopen,
      state,
      rule: 'NO RESULT OWES US THE ANSWER WE EXPECTED',
      doneMeaning: 'verified under present evidence and present machinery',
    },
  };
}
