// O-FANOUT GATE
// Give the same precisely described STATE -> DONE hole to many independent survey bees.
// Each bee searches a different function-source universe; candidates return to one common fit test.

export function oFanoutGate({hole={},surveyDoors=[]}={}) {
  const valid=surveyDoors.filter(d=>d.id && d.universe);
  const universes=[...new Set(valid.map(d=>d.universe))];
  const duplicateUniverses=valid.length-universes.length;
  const jobs=valid.map(d=>({
    id:d.id,
    function:'survey-function-candidates',
    universe:d.universe,
    hole,
    doneContract:'return-candidate-functions-with-provenance'
  }));

  return {
    oFanout:{
      hole,jobs,universes,duplicateUniverses,
      parallelCapacity:jobs.length,
      state:jobs.length?'o-fanout-ready':'open-more-function-universes',
      rule:'CAST THE SAME HOLE INTO MANY FUNCTION UNIVERSES; LET FIT, NOT FAMILIARITY, CHOOSE'
    }
  };
}
