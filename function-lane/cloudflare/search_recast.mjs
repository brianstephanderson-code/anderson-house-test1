function uniq(xs=[]){
  const out=[]; const seen=new Set();
  for(const x of xs){
    const v=String(x??"").replace(/\s+/g," ").trim();
    const k=v.toLowerCase();
    if(!v||seen.has(k)) continue;
    seen.add(k); out.push(v);
  }
  return out;
}

export function buildSearchRecasts(state={}, priorQueries=[], maxVariants=4){
  const target=String(state.target??"").trim();
  const origin=String(state.origin??"").trim();
  const action=String(state.action??"").trim();
  const what=String(state.what??"").trim();
  const environment=Array.isArray(state.environment)?state.environment:[];
  const times=Array.isArray(state.time)?state.time:[];

  const variants=[
    {kind:"RECAST_CORE",query:uniq([target,origin,...environment,what]).join(" ")},
    {kind:"RECAST_ACTION",query:uniq([target,action,origin,...environment,what]).join(" ")},
    {kind:"RECAST_TIME",query:uniq([target,origin,...environment,...times,what]).join(" ")},
    {kind:"RECAST_PHRASE",query:uniq([target?('"'+target+'"'):"",origin,...environment,what]).join(" ")}
  ];

  if(target.toLowerCase()==="salmon" && /\bperth\b/i.test(origin)){
    variants.push({kind:"RECAST_SPECIES_HYPOTHESIS",query:uniq(['"Australian salmon"',origin,...environment,what]).join(" ")});
  }

  const prior=new Set((priorQueries||[]).map(x=>String(x).toLowerCase().replace(/\s+/g," ").trim()));
  const out=[]; const seen=new Set();
  for(const x of variants){
    const k=String(x.query??"").toLowerCase().replace(/\s+/g," ").trim();
    if(!k||prior.has(k)||seen.has(k)) continue;
    seen.add(k); out.push(x);
    if(out.length>=Math.max(1,Math.min(Number(maxVariants)||4,5))) break;
  }
  return out;
}
