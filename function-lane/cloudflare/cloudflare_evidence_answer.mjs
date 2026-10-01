function textOf(x){
  if(typeof x === "string") return x;
  if(typeof x?.response === "string") return x.response;
  if(typeof x?.result?.response === "string") return x.result.response;
  if(typeof x?.choices?.[0]?.message?.content === "string") return x.choices[0].message.content;
  if(typeof x?.result?.choices?.[0]?.message?.content === "string") return x.result.choices[0].message.content;
  return "";
}

function clipEvidence(evidence){
  return (Array.isArray(evidence)?evidence:[]).slice(0,8).map((e,i)=>({
    id:i+1,
    title:String(e?.title??""),
    url:String(e?.url??""),
    text:String(e?.text??"").slice(0,1800)
  }));
}

async function runText(ai,prompt,max_tokens=700){
  const raw=await ai.run("@cf/meta/llama-3.2-3b-instruct",{
    prompt,
    max_tokens,
    temperature:0
  });
  return textOf(raw).trim();
}

function routeEndpoints(q){
  const m=String(q).match(/\bfrom\s+(.+?)\s+to\s+(.+?)(?=\s+(?:in|during|for|on|at)\b|[?.!,;:]|$)/i);
  if(!m) return null;
  return [m[1].trim(),m[2].trim()];
}

function words(s){
  return [...new Set(
    String(s??"").toLowerCase()
      .replace(/[^a-z0-9\s-]/g," ")
      .split(/\s+/)
      .filter(x=>x.length>=4)
  )];
}

function deterministicPrefilter(question,ev){
  const q=String(question??"");
  const qwords=words(q);
  const eps=routeEndpoints(q);
  const routeTerms=["walk","walking","route","path","trail","towpath","canal","pedestrian","hike","hiking"];

  return ev.map(e=>{
    const blob=(e.title+" "+e.text).toLowerCase();
    let score=0;

    for(const w of qwords){
      if(blob.includes(w)) score+=1;
    }

    if(eps){
      const a=words(eps[0]);
      const b=words(eps[1]);
      const hitA=a.some(w=>blob.includes(w));
      const hitB=b.some(w=>blob.includes(w));
      const hitRoute=routeTerms.some(w=>blob.includes(w));
      if(hitA) score+=4;
      if(hitB) score+=4;
      if(hitRoute) score+=4;
      if(!(hitA && hitB && hitRoute)) score-=6;
    }

    return {...e,score};
  }).sort((a,b)=>b.score-a.score);
}

function parseYesNo(raw){
  const t=String(raw??"").trim().toUpperCase();
  if(/^YES\b/.test(t)) return true;
  if(/^NO\b/.test(t)) return false;
  return null;
}

function parseClaims(raw,label){
  const out={direct_answer:"",claims:[],rejected:[],uncertainty:""};

  for(const rawLine of String(raw??"").split(/\r?\n/)){
    const line=rawLine.trim();
    if(!line) continue;

    let m=line.match(/^DIRECT\s*:\s*(.+)$/i);
    if(m){ out.direct_answer=m[1].trim(); continue; }

    m=line.match(new RegExp("^"+label+"\\s*:\\s*(.*?)\\s*\\|\\|\\s*SOURCES?\\s*:\\s*(.+)$","i"));
    if(m){
      const ids=[...new Set(m[2].split(/[^0-9]+/).map(Number).filter(Number.isFinite))];
      out.claims.push({text:m[1].trim(),source_ids:ids});
      continue;
    }

    m=line.match(/^REJECTED\s*:\s*(.*?)\s*\|\|\s*REASON\s*:\s*(.+)$/i);
    if(m){ out.rejected.push({text:m[1].trim(),reason:m[2].trim()}); continue; }

    m=line.match(/^UNCERTAINTY\s*:\s*(.+)$/i);
    if(m){ out.uncertainty=m[1].trim(); continue; }
  }
  return out;
}

export async function cloudflareEvidenceAnswer(question,evidence,ai){
  const q=String(question??"").trim();
  const ev=clipEvidence(evidence);

  if(!q) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"EMPTY_QUESTION"};
  if(!ai?.run) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"AI_BINDING_MISSING"};
  if(!ev.length) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"NO_EVIDENCE"};

  // PASS 1A — deterministic prefilter. This prevents obvious junk from reaching the AI.
  const ranked=deterministicPrefilter(q,ev);
  const shortlist=ranked.filter(x=>x.score>0).slice(0,4);

  if(!shortlist.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_PREFILTER_MATCH",
      prefilter:ranked.map(x=>({id:x.id,title:x.title,score:x.score}))
    };
  }

  // PASS 1B — tiny one-source-at-a-time AI relevance check.
  const kept=[];
  const rejected=[];

  for(const e of shortlist){
    const prompt=[
      "Question: "+q,
      "",
      "Candidate source:",
      "TITLE: "+e.title,
      "URL: "+e.url,
      "TEXT: "+e.text,
      "",
      "Does this source text directly help answer the exact question?",
      "For a route question it must materially discuss the walking/path/trail/towpath/canal connection or route between the endpoints.",
      "Answer exactly one line:",
      "YES",
      "or",
      "NO"
    ].join("\n");

    let raw="";
    try{ raw=await runText(ai,prompt,40); }
    catch(err){ rejected.push({id:e.id,reason:"AI relevance call failed"}); continue; }

    const yn=parseYesNo(raw);
    if(yn===true) kept.push(e);
    else rejected.push({id:e.id,reason:"not directly question-fit"});
  }

  if(!kept.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_QUESTION_FIT_EVIDENCE",
      prefilter:ranked.map(x=>({id:x.id,title:x.title,score:x.score})),
      relevance:{keep:[],reject:rejected,missing:["direct source about the requested relationship"]}
    };
  }

  // PASS 2 — concise evidence-bound draft over only the kept sources.
  const draftPrompt=[
    "You are the evidence-bound answer writer for The 3 Amigos.",
    "Use ONLY these line formats:",
    "DIRECT: short direct answer",
    "CLAIM: supported factual claim || SOURCES: 1,2",
    "UNCERTAINTY: short uncertainty or NONE",
    "",
    "Rules:",
    "- Use only the supplied evidence text.",
    "- Every CLAIM must cite one or more source IDs that directly support it.",
    "- Do not use model memory to fill gaps.",
    "- Do not invent route names, distances, weather, suitability, dates, or source details.",
    "- Do not repeat the evidence text.",
    "- Do not output JSON.",
    "",
    "QUESTION:",
    q,
    "",
    "EVIDENCE:",
    JSON.stringify(kept.map(e=>({id:e.id,title:e.title,url:e.url,text:e.text})))
  ].join("\n");

  let draftRaw="";
  try{ draftRaw=await runText(ai,draftPrompt,500); }
  catch(err){
    return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"DRAFT_AI_FAILED",detail:String(err)};
  }

  const draft=parseClaims(draftRaw,"CLAIM");
  const draftClaims=draft.claims
    .map(c=>({
      text:c.text,
      source_ids:c.source_ids.filter(id=>kept.some(e=>e.id===id))
    }))
    .filter(c=>c.text && c.source_ids.length);

  if(!draftClaims.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_DRAFT_CLAIMS",
      relevance:{keep:kept.map(e=>e.id),reject:rejected,missing:[]},
      debug_draft_raw:draftRaw.slice(0,1600)
    };
  }

  // PASS 3 — strict verification.
  const verifyPrompt=[
    "Verify these claims against the supplied evidence.",
    "Use ONLY these line formats:",
    "DIRECT: final supported direct answer",
    "VERIFIED: supported claim || SOURCES: 1,2",
    "REJECTED: unsupported claim || REASON: reason",
    "UNCERTAINTY: short uncertainty or NONE",
    "",
    "Rules:",
    "- VERIFIED only when cited source IDs directly support the claim.",
    "- If partly supported, shorten to the supported part.",
    "- Never add new facts.",
    "- Do not output JSON.",
    "",
    "QUESTION:",
    q,
    "",
    "EVIDENCE:",
    JSON.stringify(kept.map(e=>({id:e.id,title:e.title,url:e.url,text:e.text}))),
    "",
    "DRAFT CLAIMS:",
    JSON.stringify(draftClaims)
  ].join("\n");

  let verifyRaw="";
  try{ verifyRaw=await runText(ai,verifyPrompt,500); }
  catch(err){
    return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"VERIFY_AI_FAILED",detail:String(err)};
  }

  const ver=parseClaims(verifyRaw,"VERIFIED");
  const verified=ver.claims
    .map(c=>({
      text:c.text,
      source_ids:c.source_ids.filter(id=>kept.some(e=>e.id===id))
    }))
    .filter(c=>c.text && c.source_ids.length);

  if(!verified.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_VERIFIED_CLAIMS",
      relevance:{keep:kept.map(e=>e.id),reject:rejected,missing:[]},
      rejected_claims:ver.rejected,
      debug_draft_raw:draftRaw.slice(0,1200),
      debug_verify_raw:verifyRaw.slice(0,1200)
    };
  }

  const used=[...new Set(verified.flatMap(c=>c.source_ids))];
  const sources=kept.filter(e=>used.includes(e.id)).map(e=>({id:e.id,title:e.title,url:e.url}));

  return {
    ok:true,
    function:"CLOUDFLARE_EVIDENCE_ANSWER",
    model:"@cf/meta/llama-3.2-3b-instruct",
    question:q,
    relevance:{
      keep:kept.map(e=>e.id),
      rejected,
      prefilter:ranked.map(x=>({id:x.id,title:x.title,score:x.score}))
    },
    direct_answer:ver.direct_answer || draft.direct_answer,
    claims:verified,
    uncertainty:(ver.uncertainty && ver.uncertainty!=="NONE") ? ver.uncertainty : "",
    rejected_claims:ver.rejected,
    sources
  };
}
