// FUNCTION-GAP SURVEY / O-GATE
// Do not begin with a favorite function. Describe the STATE -> DONE hole, then cast for functions that fit it.

export function functionGapOGate({state={},requiredDone={},candidates=[]}={}) {
  const requiredInputs=new Set(state.provides??[]);
  const requiredOutputs=new Set(requiredDone.requires??[]);

  const tested=candidates.map(c=>{
    const accepts=new Set(c.accepts??[]);
    const produces=new Set(c.produces??[]);
    const stateFit=[...accepts].every(x=>requiredInputs.has(x));
    const doneFit=[...requiredOutputs].every(x=>produces.has(x));
    const legal=c.legal!==false;
    const verified=c.verified===true;
    return {id:c.id??null,stateFit,doneFit,legal,verified,fit:stateFit&&doneFit&&legal&&verified};
  });

  const fits=tested.filter(x=>x.fit);
  return {
    functionGapO:{
      hole:{stateProvides:[...requiredInputs],doneRequires:[...requiredOutputs]},
      tested,fits,
      state:fits.length?'function-fit-found':'cast-more-functions',
      rule:'DESCRIBE THE HOLE FIRST; THEN FIND THE FUNCTION THAT FITS'
    }
  };
}
