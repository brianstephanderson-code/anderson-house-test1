function textOf(x){
  if(typeof x==="string") return x;
  if(typeof x?.response==="string") return x.response;
  if(typeof x?.result?.response==="string") return x.result.response;
  if(typeof x?.choices?.[0]?.message?.content==="string") return x.choices[0].message.content;
  if(typeof x?.result?.choices?.[0]?.message?.content==="string") return x.result.choices[0].message.content;
  return "";
}
function parseJsonLoose(s){
  const t=String(s??"").trim().replace(/^```(?:json)?s*/i,"").replace(/s*```$/,"");
  try{return JSON.parse(t);}catch{}
  const a=t.indexOf("{"),b=t.lastIndexOf("}");
  if(a>=0&&b>a){try{return JSON.parse(t.slice(a,b+1));}catch{}}
  return {};
}
export async function cloudflareAiCastsV20(question,ai){
  const q=String(question??"").trim();
  if(!q) return {ok:false,function:"CLOUDFLARE_AI_CASTS_V20",error:"EMPTY_QUESTION"};
  if(!ai?.run) return {ok:false,function:"CLOUDFLARE_AI_CASTS_V20",error:"AI_BINDING_MISSING"};
  const prompt=[
    "You are the search-planning brain for The 3 Amigos.",
    "Do NOT answer the question.",
    "Return ONLY JSON with keys: interpreted_need, hard_constraints, unknown, casts, missing.",
    "casts must be 4 to 6 materially different web-search queries.",
    "Preserve every hard boundary in the user's question.",
    "Expand ONLY the unknown/soft wording.",
    "Do not invent side tasks such as weather unless the user asked for weather.",
    "For route questions, every cast must preserve BOTH endpoints and the requested travel mode.",
    "Prefer direct route terms such as route, walking route, path, trail, towpath, canal path when appropriate.",
    "Include one practitioner/end-user/community cast when useful.",
    "Do not invent URLs or sources.",
    "Question: "+q
  ].join("\n");
  const raw=await ai.run("@cf/meta/llama-3.2-3b-instruct",{prompt,max_tokens:700,temperature:0});
  const rawText=textOf(raw);
  let p=parseJsonLoose(rawText);
  if(!Array.isArray(p?.casts) || p.casts.length===0) p=parseLabeledText(rawText);
  const casts=(Array.isArray(p?.casts)?p.casts:[]).map(x=>String(x??"").trim()).filter(Boolean).slice(0,6);
  return {
    ok:casts.length>0,
    function:"CLOUDFLARE_AI_CASTS_V20",
    model:"@cf/meta/llama-3.2-3b-instruct",
    question:q,
    interpreted_need:String(p?.interpreted_need??"").trim(),
    hard_constraints:Array.isArray(p?.hard_constraints)?p.hard_constraints:[],
    unknown:String(p?.unknown??"").trim(),
    casts,
    missing:Array.isArray(p?.missing)?p.missing:[],
    ...(casts.length?{}:{debug_text_preview:rawText.slice(0,1200)})
  };
}
