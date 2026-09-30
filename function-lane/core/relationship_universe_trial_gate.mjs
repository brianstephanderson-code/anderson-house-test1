// RELATIONSHIP UNIVERSE TRIAL GATE
// A newly proposed universe must prove it is a repeatable relationship class, not a one-off clever label.
// Test it across multiple gaps and require explicit relation rules + provenance.

export function relationshipUniverseTrialGate({universe={},trials=[],requiredCleanTrials=3}={}) {
  const completed=trials.filter(t=>t?.completed===true);
  const clean=t=>t.bridgeFound===true && t.relationRuleApplied===true && t.contextPreserved===true && t.provenancePresent===true && t.extraAssumptions!==true;
  const cleanCount=completed.filter(clean).length;
  const distinctGaps=new Set(completed.filter(clean).map(t=>t.gapId).filter(Boolean)).size;
  const proven=cleanCount>=requiredCleanTrials && distinctGaps>=requiredCleanTrials;

  return {relationshipUniverseTrial:{
    universe:universe.name??null,
    completedTrials:completed.length,
    cleanTrials:cleanCount,
    distinctCleanGaps:distinctGaps,
    requiredCleanTrials,
    state:proven?'relationship-universe-proven':'relationship-universe-unproven',
    action:proven?'add-to-universe-pool':'keep-in-trial',
    rule:'A NEW UNIVERSE MUST REPEAT ACROSS DIFFERENT GAPS; ONE CLEVER CONNECTION DOES NOT MAKE A UNIVERSE'
  }};
}
