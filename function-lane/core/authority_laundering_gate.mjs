// AUTHORITY LAUNDERING GATE
// A prestigious repeater does not strengthen the underlying evidence merely by repeating it.
// Separate source authority from claim ancestry and independent evidence.

export function authorityLaunderingGate({
  sourceId = '',
  sourceAuthority = 'unknown',
  claimOriginId = '',
  originEvidenceStrength = 'unknown',
  addsIndependentEvidence = false,
  independentlyVerifiesClaim = false,
  presentedAsStrongerBecauseOfAuthority = false,
} = {}) {
  const addsSupport = addsIndependentEvidence || independentlyVerifiesClaim;
  let state = 'authority-neutral';

  if (presentedAsStrongerBecauseOfAuthority && !addsSupport) state = 'authority-laundering-risk';
  else if (addsSupport) state = 'new-support-added';
  else if (!claimOriginId) state = 'trace-claim-origin';

  return {
    authorityLaundering: {
      sourceId,
      sourceAuthority,
      claimOriginId,
      originEvidenceStrength,
      addsSupport,
      state,
      rule: 'PRESTIGE OF THE REPEATER DOES NOT UPGRADE THE ORIGINAL EVIDENCE',
    },
  };
}
