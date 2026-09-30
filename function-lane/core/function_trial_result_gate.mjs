// FUNCTION TRIAL RESULT GATE
// Inspect equal-parcel trials against the required DONE contract.
// This gate qualifies functions; it does not choose a favorite or hide failures.

export function functionTrialResultGate({results=[]}={}) {
  const qualified=[];
  const failed=[];
  const incomplete=[];

  for (const r of results) {
    if (!r.functionId || r.doneSatisfied===undefined || r.evidenceIntegrity===undefined || r.contextPreserved===undefined) {
      incomplete.push(r); continue;
    }
    const clean = r.doneSatisfied===true && r.evidenceIntegrity===true && r.contextPreserved===true && (r.errors??[]).length===0;
    if (clean) qualified.push(r);
    else failed.push(r);
  }

  return {
    functionTrialResult:{
      qualified,failed,incomplete,
      state:qualified.length ? 'qualified-functions-found' : 'recast-function-search',
      selection:null,
      rule:'QUALIFY AGAINST DONE; PRESERVE EVERY FAILURE; DO NOT TURN MEASUREMENT INTO FAVORITISM'
    }
  };
}
