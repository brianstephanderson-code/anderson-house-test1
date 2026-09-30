// GEOGRAPHY FIT GATE
// Correct in one place/community is not automatically correct in another.
// Match evidence to the author's relevant linguistic/cultural geography.

export function geographyFitGate({
  targetRegion = '',
  targetCommunity = '',
  evidenceRegion = '',
  evidenceCommunity = '',
  localUsageVerified = false,
  regionalDifferenceKnown = false,
  sameSenseAcrossRegionsDemonstrated = false,
  sourceId = '',
} = {}) {
  let state = 'recast-local-evidence';

  const exactRegion = Boolean(targetRegion && evidenceRegion && targetRegion === evidenceRegion);
  const exactCommunity = !targetCommunity || (evidenceCommunity && targetCommunity === evidenceCommunity);

  if (localUsageVerified || (exactRegion && exactCommunity)) state = 'geography-fit';
  else if (regionalDifferenceKnown && !sameSenseAcrossRegionsDemonstrated) state = 'regional-mismatch-risk';
  else if (sameSenseAcrossRegionsDemonstrated) state = 'sense-bridged-across-regions';

  return {
    geographyFit: {
      sourceId,
      targetRegion,
      targetCommunity,
      evidenceRegion,
      evidenceCommunity,
      state,
      rule: 'CORRECT SOMEWHERE IS NOT AUTOMATICALLY CORRECT HERE',
    },
  };
}
