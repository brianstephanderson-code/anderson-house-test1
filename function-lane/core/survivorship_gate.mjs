// SURVIVORSHIP GATE
// Agreement among accessible sources is not automatically agreement among all relevant sources.
// Record what portions of the evidence universe are missing, inaccessible or not digitized.

export function survivorshipGate({
  foundSources = 0,
  expectedSourceClasses = [],
  searchedSourceClasses = [],
  missingKnownSources = [],
  archiveSearchPerformed = false,
  nondigitalSearchConsidered = false,
  contrarySearchPerformed = false,
} = {}) {
  const searched = new Set(searchedSourceClasses);
  const unsearchedClasses = expectedSourceClasses.filter(x => !searched.has(x));
  const blindSpots = unsearchedClasses.length + missingKnownSources.length;

  let state = 'coverage-limited';
  if (foundSources === 0) state = 'no-surviving-evidence-found';
  else if (blindSpots > 0) state = 'survivorship-risk';
  else if (!archiveSearchPerformed || !contrarySearchPerformed) state = 'coverage-limited';
  else state = 'coverage-characterized';

  return {
    survivorship: {
      state,
      foundSources,
      unsearchedClasses,
      missingKnownSources,
      archiveSearchPerformed,
      nondigitalSearchConsidered,
      contrarySearchPerformed,
      rule: 'EVERYTHING WE FOUND AGREES DOES NOT MEAN EVERYONE AGREED',
    },
  };
}
