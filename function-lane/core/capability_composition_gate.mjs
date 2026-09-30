// CAPABILITY COMPOSITION GATE
// One bee does not need every skill if several proven bees can compose the required atomic transformation.
// Build a temporary team only when their proven capabilities cover the whole requirement without gaps.

export function capabilityCompositionGate({job={},bees=[]}={}) {
  const required=[...(job.requires??[])];
  const active=bees.filter(b=>b.available!==false);
  const coverage={};
  for (const req of required) coverage[req]=active.filter(b=>(b.capabilities??[]).includes(req)).map(b=>b.id);
  const missing=required.filter(req=>coverage[req].length===0);
  const team=[...new Set(required.flatMap(req=>coverage[req].slice(0,1)))];

  return {
    capabilityComposition:{
      jobId:job.id??null,required,coverage,missing,team,
      state:missing.length?'open-capability-o-gate':'composable-team-found',
      handoffContract:'preserve-state-evidence-context-between-capabilities',
      rule:'IF NO SINGLE BEE FITS, COMPOSE PROVEN SKILLS; DO NOT INVENT A SUPER-BEE'
    }
  };
}
