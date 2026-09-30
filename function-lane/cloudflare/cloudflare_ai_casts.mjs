function textOf(x){
  if(typeof x==="string") return x;
  if(typeof x?.response==="string") return x.response;
  if(typeof x?.result?.response==="string") return x.result.response;
  if(typeof x?.choices?.[0]?.message?.content==="string") return x.choices[0].message.content;
  if(typeof x?.result?.choices?.[0]?.message?.content==="string") return x.result.choices[0].message.content;
  return "";
}


function parseLabeledText(t){
  const text=String(t??"");
  const lines=text.split(/\r?\n/);
  const casts=[], missing=[];
  let mode="";
  let interpreted="";
  for(const line of lines){
    const x=line.trim();
    if(/^interpreted need\s*:/i.test(x)){ mode="need"; continue; }
    if(/^casts\s*:/i.test(x)){ mode="casts"; continue; }
    if(/^missing\s*:/i.test(x)){ mode="missing"; continue; }
    const m=x.match(/^[-*•]\s*(.+)$/);
    if(!m) continue;
    const v=m[1].replace(/^["']|["']$/g,"").trim();
    if(!v) continue;
    if(mode==="casts") casts.push(v);
    else if(mode==="missing") missing.push(v);
    else if(mode==="need") interpreted+=(interpreted?" ":"")+v;
  }
  return {interpreted_need:interpreted,casts,missing};
}

function parseJsonLoose(s){
  const t=String(s??"").trim().replace(/^\`\`\`(?:json)?\s*/i,"").replace(/\s*\`\`\`$/,"");
  try{return JSON.parse(t);}catch{}
  const a=t.indexOf("{"), b=t.lastIndexOf("}");
  if(a>=0&&b>a){ try{return JSON.parse(t.slice(a,b+1));}catch{} }
  return {};
}

export async function cloudflareAiCasts(question, ai){
  const q=String(question??"").trim();
  if(!q) return {ok:false,function:"CLOUDFLARE_AI_CASTS",error:"EMPTY_QUESTION"};
  if(!ai?.run) return {ok:false,function:"CLOUDFLARE_AI_CASTS",error:"AI_BINDING_MISSING"};

  const prompt=[
    "You are the search-planning brain for Anderson House.",
    "Do NOT answer the question.",
    "Return only JSON with keys: interpreted_need, casts, missing.",
    "casts must be an array of 3 to 5 materially different web-search queries.",
    "Include at least one end-user/operator/community-oriented cast when relevant.",
    "Do not invent sources or URLs.",
    "Question: "+q
  ].join("\n");

  const raw=await ai.run("@cf/meta/llama-3.2-3b-instruct",{
    prompt,
    max_tokens:500,
    temperature:0
  });

  const rawText=textOf(raw);
  let parsed=parseJsonLoose(rawText);
  if(!Array.isArray(parsed?.casts) || parsed.casts.length===0) parsed=parseLabeledText(rawText);
  const casts=(Array.isArray(parsed?.casts)?parsed.casts:[])
    .map(x=>String(x??"").trim()).filter(Boolean).slice(0,5);

  return {
    ok:casts.length>0,
    function:"CLOUDFLARE_AI_CASTS",
    policy:"AI_PLANS_SEARCH_DETERMINISTIC_PLUMBING_PROVES_SOURCES",
    model:"@cf/meta/llama-3.2-3b-instruct",
    question:q,
    interpreted_need:String(parsed?.interpreted_need??"").trim(),
    casts,
    missing:Array.isArray(parsed?.missing)?parsed.missing.map(x=>String(x)):[],
    ai_answer_is_evidence:false,
    ...(casts.length?{}:{debug_text_preview:rawText.slice(0,1200),debug_keys:Object.keys(raw??{})})
  };
}
