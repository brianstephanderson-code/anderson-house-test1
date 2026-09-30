// RELATIONSHIP-UNIVERSE FANOUT GATE
// When the relationship type is unknown, cast the same gap into many independent universes at once.
// Each bee returns possible bridges with provenance; no universe gets priority merely because it is familiar.

export function relationshipUniverseFanoutGate({gap={},universes=[]}={}) {
  const unique=[...new Set(universes.filter(Boolean))];
  const jobs=unique.map(universe=>({
    id:`relationship-survey::${universe}`,
    function:'search-for-bridge',
    universe,
    gap,
    doneContract:'return-candidate-bridges-with-provenance'
  }));

  return {
    relationshipUniverseFanout:{
      gap,jobs,parallelCapacity:jobs.length,
      state:jobs.length?'relationship-fanout-ready':'discover-more-relationship-universes',
      selection:null,
      rule:'WHEN THE RELATIONSHIP IS UNKNOWN, CAST THE SAME GAP SIDEWAYS INTO MANY UNIVERSES'
    }
  };
}
