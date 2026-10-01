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
  const a=t.indexOf("{"), b=t.lastIndexOf("}");
  if(a>=0&&b>a){ try{return JSON.parse(t.slice(a,b+1));}catch{} }
  return {};
}

function clipEvidence(evidence){
  return (Array.isArray(evidence)?evidence:[]).slice(0,8).map((e,i)=>({
    id:i+1,
    title:String(e?.title??""),
    url:String(e?.url??""),
    text:String(e?.text??"").slice(0,3200)
  }));
}

async function runJson(ai,prompt,max_tokens=900){
  const raw=await ai.run("@cf/meta/llama-3.2-3b-instruct",{
    prompt,
    max_tokens,
    temperature:0,
    response_format:{type:"json_object"}
  });
  const rawText=textOf(raw);
  return {rawText, parsed:parseJsonLoose(rawText)};
}

export async function cloudflareEvidenceAnswer(question,evidence,ai){
  const q=String(question??"").trim();
  const ev=clipEvidence(evidence);
  if(!q) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"EMPTY_QUESTION"};
  if(!ai?.run) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"AI_BINDING_MISSING"};
  if(!ev.length) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"NO_EVIDENCE"};

  // 1) Relevance gate: keep only evidence that directly helps answer THIS question.
  const relPrompt=[
    "You are an evidence relevance gate.",
    "Do not answer the question.",
    "Return ONLY JSON: {keep:[ids], reject:[{id,reason}], missing:[strings]}.",
    "Keep a source only if its supplied text directly helps answer the exact user question.",
    "Reject sources that merely mention one place/word but do not address the requested relationship or unknown.",
    "For route questions, a useful source should discuss the route, path, canal, trail, walking connection, or another directly relevant way between the endpoints.",
    "Do not infer facts not present in the text.",
    "",
    "QUESTION:",
    q,
    "",
    "EVIDENCE:",
    JSON.stringify(ev)
  ].join("\n");

  const rel=await runJson(ai,relPrompt,700);
  let keep=Array.isArray(rel.parsed?.keep)?rel.parsed.keep.map(Number).filter(Number.isFinite):[];
  keep=[...new Set(keep)].filter(id=>ev.some(e=>e.id===id));
  const kept=ev.filter(e=>keep.includes(e.id));

  if(!kept.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_QUESTION_FIT_EVIDENCE",
      relevance:{keep:[],reject:rel.parsed?.reject??[],missing:rel.parsed?.missing??[]},
      debug_relevance_raw:rel.rawText.slice(0,2000)
    };
  }

  // 2) Draft: structured claims only, every claim must cite supplied evidence IDs.
  const draftPrompt=[
    "You are an evidence-bound answer writer.",
    "Return ONLY JSON with this schema:",
    '{"direct_answer":"...","claims":[{"text":"...","source_ids":[1,2]}],"uncertainty":"...","sources_used":[1,2]}',
    "Use ONLY the supplied evidence text.",
    "Every factual claim must have one or more source_ids that directly support it.",
    "Do not use model memory to fill gaps.",
    "Do not invent route names, distances, weather, suitability, dates, or source details.",
    "Do not include meta-commentary about following instructions.",
    "Answer the exact question first; keep it concise but useful.",
    "",
    "QUESTION:",
    q,
    "",
    "APPROVED EVIDENCE:",
    JSON.stringify(kept)
  ].join("\n");

  const draft=await runJson(ai,draftPrompt,1000);
  const draftClaims=Array.isArray(draft.parsed?.claims)?draft.parsed.claims:[];

  // 3) Claim verifier: independent second AI pass deletes unsupported claims.
  const verifyPrompt=[
    "You are a strict claim verifier.",
    "Return ONLY JSON: {verified:[{text,source_ids}], rejected:[{text,reason}], direct_answer:'...', uncertainty:'...'}",
    "Verify each claim against the supplied evidence text.",
    "A claim passes only if the cited source_ids directly support that claim.",
    "If a claim is partly supported, rewrite it down to the supported portion.",
    "Never add new facts.",
    "The final direct_answer must be composed only from verified claims.",
    "",
    "QUESTION:",
    q,
    "",
    "EVIDENCE:",
    JSON.stringify(kept),
    "",
    "DRAFT:",
    JSON.stringify({
      direct_answer:String(draft.parsed?.direct_answer??""),
      claims:draftClaims,
      uncertainty:String(draft.parsed?.uncertainty??"")
    })
  ].join("\n");

  const ver=await runJson(ai,verifyPrompt,1000);
  const verified=Array.isArray(ver.parsed?.verified)?ver.parsed.verified:[];
  const cleanVerified=verified.map(c=>({
    text:String(c?.text??"").trim(),
    source_ids:(Array.isArray(c?.source_ids)?c.source_ids:[]).map(Number).filter(id=>kept.some(e=>e.id===id))
  })).filter(c=>c.text&&c.source_ids.length);

  if(!cleanVerified.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_VERIFIED_CLAIMS",
      relevance:{keep,missing:rel.parsed?.missing??[]},
      rejected_claims:ver.parsed?.rejected??[],
      debug_draft_raw:draft.rawText.slice(0,2000),
      debug_verify_raw:ver.rawText.slice(0,2000)
    };
  }

  const used=[...new Set(cleanVerified.flatMap(c=>c.source_ids))];
  const sources=kept.filter(e=>used.includes(e.id)).map(e=>({id:e.id,title:e.title,url:e.url}));

  return {
    ok:true,
    function:"CLOUDFLARE_EVIDENCE_ANSWER",
    model:"@cf/meta/llama-3.2-3b-instruct",
    question:q,
    relevance:{
      keep,
      rejected:rel.parsed?.reject??[],
      missing:rel.parsed?.missing??[]
    },
    direct_answer:String(ver.parsed?.direct_answer??"").trim(),
    claims:cleanVerified,
    uncertainty:String(ver.parsed?.uncertainty??"").trim(),
    rejected_claims:ver.parsed?.rejected??[],
    sources
  };
}
