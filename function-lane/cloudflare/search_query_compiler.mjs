const MONTHS=new Set("january february march april may june july august september october november december".split(" "));
const STOP=new Set(`
a an and are as at be because been but by can could did do does for from get go going had has have how i i'd i'll i'm if in into is it its like me my of on or our please should so some than that the their them then there they this to under up want was we were what when where which who why will with within would you your don out
`.trim().split(/\s+/));

function words(text="") {
  return String(text).toLowerCase().replace(/[’']/g,"'").match(/[a-z0-9]+(?:-[a-z0-9]+)?/g)||[];
}

function uniq(xs=[]) {
  const out=[]; const seen=new Set();
  for(const x of xs){ const k=String(x).toLowerCase(); if(!k||seen.has(k)) continue; seen.add(k); out.push(x); }
  return out;
}

export function extractSearchState(text="") {
  const raw=String(text??"").trim();
  const ws=words(raw);
  const months=uniq(ws.filter(x=>MONTHS.has(x)));
  const numbers=[];
  const distanceRe=/\b(\d+(?:\.\d+)?)\s*(km|kilometers?|kilometres?|miles?)\b/gi;
  let m; while((m=distanceRe.exec(raw))) numbers.push(`${m[1]} ${m[2]}`);
  const locationMatches=[];
  const locRe=/\b(?:in|near|around|from)\s+([A-Z][A-Za-z.-]+(?:\s+[A-Z][A-Za-z.-]+){0,3})/g;
  while((m=locRe.exec(raw))) locationMatches.push(m[1].replace(/[,.!?]+$/,""));
  const subjectMatch=raw.match(/\b(?:for|about|catch|find|search(?:ing)? for)\s+([A-Za-z][A-Za-z0-9 -]{1,50}?)(?=[,.!?]|\s+(?:in|near|around|within|under|during|on|at|what|which|who|where|when|how)\b|$)/i);
  const subject=subjectMatch?subjectMatch[1].trim():null;
  const content=uniq(ws.filter(x=>x.length>2&&!STOP.has(x)));
  return {
    raw,
    subject,
    locations:uniq(locationMatches),
    times:months,
    constraints:uniq(numbers),
    content
  };
}

export function compileSearchQueries(text="", maxVariants=4) {
  const state=extractSearchState(text);
  if(!state.raw) return {ok:false,function:"SEARCH_QUERY_COMPILER",error:"EMPTY_QUERY",state,queries:[]};
  const core=state.content.slice(0,14);
  const compact=core.join(" ");
  const focus=[];
  if(state.subject) focus.push(`"${state.subject}"`);
  focus.push(...state.locations,...state.times,...state.constraints);
  const tail=core.filter(x=>!focus.join(" ").toLowerCase().includes(x.toLowerCase())).slice(0,8);
  const focused=uniq([...focus,...tail]).join(" ").trim();
  const booleanTerms=uniq([
    state.subject? `"${state.subject}"`:null,
    ...state.locations,
    ...state.times,
    ...state.constraints,
    ...tail.slice(0,5)
  ].filter(Boolean));
  const boolean=booleanTerms.join(" AND ");
  const exactPhrases=[...state.locations,state.subject].filter(Boolean).map(x=>`"${x}"`);
  const phrasePlus=uniq([...exactPhrases,...state.times,...tail.slice(0,6)]).join(" ").trim();

  const candidates=[
    {kind:"COMPACT_KEYWORDS",query:compact},
    {kind:"FOCUSED_PHRASE",query:focused},
    {kind:"BOOLEAN_AND",query:boolean},
    {kind:"PHRASE_PLUS_KEYWORDS",query:phrasePlus},
    {kind:"ORIGINAL_FALLBACK",query:state.raw}
  ].filter(x=>x.query);

  const seen=new Set(); const queries=[];
  for(const x of candidates){
    const k=x.query.toLowerCase().replace(/\s+/g," ").trim();
    if(!k||seen.has(k)) continue;
    seen.add(k); queries.push(x);
    if(queries.length>=Math.max(1,Math.min(Number(maxVariants)||4,5))) break;
  }
  return {ok:true,function:"SEARCH_QUERY_COMPILER",state,queries};
}
