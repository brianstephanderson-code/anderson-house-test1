const MONTHS=new Set("january february march april may june july august september october november december".split(" "));

function clean(v=""){ return String(v??"").replace(/\s+/g," ").replace(/^[,.;:!?\s]+|[,.;:!?\s]+$/g,"").trim(); }
function uniq(xs=[]){
  const out=[]; const seen=new Set();
  for(const x of xs){ const v=clean(x); const k=v.toLowerCase(); if(!v||seen.has(k)) continue; seen.add(k); out.push(v); }
  return out;
}
function words(text=""){
  return String(text??"").toLowerCase().replace(/[’']/g,"'").match(/[a-z0-9]+(?:-[a-z0-9]+)?/g)||[];
}
function firstMatch(raw, patterns=[]){
  for(const re of patterns){
    const m=raw.match(re);
    if(m?.[1]) return clean(m[1]);
  }
  return null;
}

export function interpretSearchInput(text=""){
  const raw=String(text??"").trim();
  if(!raw) return {ok:false,function:"SEARCH_FUNCTION_INTERPRETER",error:"EMPTY_INPUT"};

  const ws=words(raw);
  const time=uniq(ws.filter(x=>MONTHS.has(x)));

  const distanceMatch=raw.match(/\b(?:within|under|less than|no more than|up to)?\s*(\d+(?:\.\d+)?)\s*(km|kilometers?|kilometres?|miles?)\b/i);
  const boundary=distanceMatch ? {
    type:"distance",
    operator:"<=",
    value:Number(distanceMatch[1]),
    unit:distanceMatch[2].toLowerCase()
  } : null;

  const origin=firstMatch(raw,[
    /\b(?:within|under|less than|no more than|up to)\s+\d+(?:\.\d+)?\s*(?:km|kilometers?|kilometres?|miles?)\s+(?:of|from)\s+([A-Za-z.-]+(?:\s+[A-Za-z.-]+){0,2}?)(?=\s+(?:on|at|near|around|with|using|what|which|where|when|how)\b|[,.!?]|$)/i,
    /\b(?:in|near|around|from)\s+([A-Za-z.-]+(?:\s+[A-Za-z.-]+){0,2}?)(?=\s+(?:on|at|within|under|with|using|what|which|where|when|how|for)\b|[,.!?]|$)/i
  ]);

  const target=firstMatch(raw,[
    /\bfor\s+([A-Za-z][A-Za-z0-9 -]{1,40}?)(?=\s+(?:within|near|around|in|from|on|at|during|using|with|what|which|where|when|how)\b|[,.!?]|$)/i,
    /\b(?:fish(?:ing)?|catch(?:ing)?)\s+([A-Za-z][A-Za-z0-9 -]{1,40}?)(?=\s+(?:within|near|around|in|from|on|at|during|using|with|what|which|where|when|how)\b|[,.!?]|$)/i
  ]);

  const environmentTerms=[
    ["beach",/\b(?:on|from|off|at)?\s*(?:the\s+)?beach\b/i],
    ["shore",/\bshore(?:line)?\b/i],
    ["surf",/\bsurf\b/i],
    ["rock",/\brock(?:s|y)?\b/i],
    ["boat",/\bboat\b/i],
    ["river",/\briver\b/i],
    ["estuary",/\bestuary\b/i]
  ];
  const environment=environmentTerms.filter(([,re])=>re.test(raw)).map(([name])=>name);

  const action=/\bfish(?:ing)?\b/i.test(raw) ? "fishing"
    : /\bcatch(?:ing)?\b/i.test(raw) ? "catching"
    : /\bsearch(?:ing)?\b/i.test(raw) ? "searching"
    : "find information";

  let what=null;
  if(/\bbest\s+bait\b/i.test(raw)) what="best bait";
  else {
    const m=raw.match(/\bwhat\s+(?:is|are)\s+(?:the\s+)?(.+?)[?!.]*$/i);
    if(m?.[1]) what=clean(m[1]);
  }

  return {
    ok:true,
    function:"SEARCH_FUNCTION_INTERPRETER",
    raw,
    roles:{
      action,
      target,
      time,
      origin,
      boundary,
      environment,
      what,
      desired_done:what ? `verified answer for ${what}` : "verified answer"
    }
  };
}
