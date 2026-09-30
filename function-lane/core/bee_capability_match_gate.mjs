// BEE CAPABILITY / MATCH GATE
// Jobs belong to functions, not named workers. Any free bee that satisfies the atomic job requirements may take it.

export function beeCapabilityMatchGate({job={},bees=[]}={}) {
  const required=new Set(job.requires??[]);
  const eligible=bees.filter(bee=>{
    if (!bee.id || bee.state!=='free') return false;
    const has=new Set(bee.capabilities??[]);
    return [...required].every(x=>has.has(x));
  });

  const ranked=[...eligible].sort((a,b)=>(a.load??0)-(b.load??0));
  return {
    beeCapabilityMatch:{
      jobId:job.id??null,
      eligible:ranked.map(x=>x.id),
      selected:ranked[0]?.id??null,
      state:ranked.length?'matched':'no-capable-free-bee',
      rule:'ROUTE THE FUNCTION TO ANY FREE CAPABLE BEE; DO NOT BIND THE FUNCTION TO A WORKER'
    }
  };
}
