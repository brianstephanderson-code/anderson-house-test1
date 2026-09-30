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
  const subject=String(state.subject??"").trim();
  const place=Array.isArray(state.locations)&&state.locations.length?String(state.locations[0]).trim():"";
  const content=Array.isArray(state.content)?state.content.map(x=>String(x).toLowerCase()):[];
  const hasAustralia=content.includes("australia");
  const focus=content.includes("bait") ? "bait" : content.includes("best") ? "best" : "";
  const region=hasAustralia ? "Australia" : "";

  const variants=[
    {kind:"RECAST_SIMPLE",query:uniq([subject,place,region,focus]).join(" ")},
    {kind:"RECAST_FISHING",query:uniq([subject,"fishing",place,region,focus]).join(" ")},
    {kind:"RECAST_PHRASE",query:uniq([subject?('"'+subject+'"'):"",place,region,focus]).join(" ")}
  ];

  if(subject.toLowerCase()==="salmon" && hasAustralia){
    variants.push(
      {kind:"RECAST_GEO_SPECIES_HYPOTHESIS",query:uniq(['"Australian salmon"',place,"bait"]).join(" ")},
      {kind:"RECAST_GEO_SPECIES_HYPOTHESIS",query:'"Australian salmon" "Western Australia" bait'}
    );
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
