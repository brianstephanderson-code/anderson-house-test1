// REGISTER FIT GATE
// Same word, time and place can perform a different function in a different domain/register.
// Match evidence to the communication universe actually active in the passage.

export function registerFitGate({
  targetRegister = '',
  evidenceRegister = '',
  domainUsageVerified = false,
  registerDifferenceKnown = false,
  sameSenseAcrossRegistersDemonstrated = false,
  sourceId = '',
} = {}) {
  let state = 'recast-domain-evidence';
  const exact = Boolean(targetRegister && evidenceRegister && targetRegister === evidenceRegister);

  if (domainUsageVerified || exact) state = 'register-fit';
  else if (registerDifferenceKnown && !sameSenseAcrossRegistersDemonstrated) state = 'register-mismatch-risk';
  else if (sameSenseAcrossRegistersDemonstrated) state = 'sense-bridged-across-registers';

  return {
    registerFit: {
      sourceId,
      targetRegister,
      evidenceRegister,
      state,
      rule: 'RIGHT WORD, WRONG UNIVERSE IS STILL WRONG',
    },
  };
}
