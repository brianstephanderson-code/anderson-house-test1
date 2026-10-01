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
    text:String(e?.text??"").slice(0,3200)
  }));
}

async function runText(ai,prompt,max_tokens=900){
  const raw=await ai.run("@cf/meta/llama-3.2-3b-instruct",{
    prompt,
    max_tokens,
    temperature:0
  });
  return textOf(raw).trim();
}

function idsFrom(s){
  return [...new Set(
    String(s??"").split(/[^0-9]+/).map(Number).filter(Number.isFinite)
  )];
}

function parseRelevance(raw, validIds){
  const keep=[];
  const reject=[];
  const missing=[];

  for(const rawLine of String(raw??"").split(/\r?\n/)){
    const line=rawLine.trim();
    if(!line) continue;

    let m=line.match(/^KEEP\s*:\s*(.+)$/i);
    if(m){
      keep.push(...idsFrom(m[1]).filter(x=>validIds.includes(x)));
      continue;
    }

    m=line.match(/^REJECT\s*:\s*(\d+)\s*(?:\|\|\s*(.*))?$/i);
    if(m){
      reject.push({id:Number(m[1]),reason:String(m[2]??"").trim()});
      continue;
    }

    m=line.match(/^MISSING\s*:\s*(.+)$/i);
    if(m){
      missing.push(m[1].trim());
      continue;
    }
  }

  return {
    keep:[...new Set(keep)],
    reject,
    missing
  };
}

function parseClaims(raw,label){
  const out={direct_answer:"",claims:[],rejected:[],uncertainty:""};

  for(const rawLine of String(raw??"").split(/\r?\n/)){
    const line=rawLine.trim();
    if(!line) continue;

    let m=line.match(/^DIRECT\s*:\s*(.+)$/i);
    if(m){
      out.direct_answer=m[1].trim();
      continue;
    }

    m=line.match(new RegExp("^"+label+"\\s*:\\s*(.*?)\\s*\\|\\|\\s*SOURCES?\\s*:\\s*(.+)$","i"));
    if(m){
      out.claims.push({
        text:m[1].trim(),
        source_ids:idsFrom(m[2])
      });
      continue;
    }

    m=line.match(/^REJECTED\s*:\s*(.*?)\s*\|\|\s*REASON\s*:\s*(.+)$/i);
    if(m){
      out.rejected.push({text:m[1].trim(),reason:m[2].trim()});
      continue;
    }

    m=line.match(/^UNCERTAINTY\s*:\s*(.+)$/i);
    if(m){
      out.uncertainty=m[1].trim();
      continue;
    }
  }

  return out;
}

export async function cloudflareEvidenceAnswer(question,evidence,ai){
  const q=String(question??"").trim();
  const ev=clipEvidence(evidence);

  if(!q) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"EMPTY_QUESTION"};
  if(!ai?.run) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"AI_BINDING_MISSING"};
  if(!ev.length) return {ok:false,function:"CLOUDFLARE_EVIDENCE_ANSWER",error:"NO_EVIDENCE"};

  const validIds=ev.map(e=>e.id);

  // PASS 1 — QUESTION-FIT RELEVANCE
  const relPrompt=[
    "You are the evidence relevance gate for The 3 Amigos.",
    "Do NOT answer the user's question.",
    "Use ONLY these line formats:",
    "KEEP: 1,2",
    "REJECT: 3 || reason",
    "MISSING: short missing evidence description",
    "",
    "Rules:",
    "- KEEP only sources whose supplied text directly helps answer the exact question.",
    "- Reject sources that merely mention one endpoint or a generic travel topic.",
    "- For a route question, KEEP sources that discuss a walking route, path, trail, towpath, canal path, or direct walking connection between the endpoints.",
    "- Do not infer facts absent from the supplied text.",
    "- Do not output JSON.",
    "- Do not add commentary.",
    "",
    "QUESTION:",
    q,
    "",
    "EVIDENCE:",
    JSON.stringify(ev)
  ].join("\n");

  let relRaw="";
  try{
    relRaw=await runText(ai,relPrompt,650);
  }catch(err){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"RELEVANCE_AI_FAILED",
      detail:String(err)
    };
  }

  const rel=parseRelevance(relRaw,validIds);
  const kept=ev.filter(e=>rel.keep.includes(e.id));

  if(!kept.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_QUESTION_FIT_EVIDENCE",
      relevance:rel,
      debug_relevance_raw:relRaw.slice(0,2200)
    };
  }

  // PASS 2 — EVIDENCE-BOUND DRAFT
  const draftPrompt=[
    "You are the evidence-bound answer writer for The 3 Amigos.",
    "Use ONLY these line formats:",
    "DIRECT: short direct answer",
    "CLAIM: supported factual claim || SOURCES: 1,2",
    "CLAIM: another supported factual claim || SOURCES: 2",
    "UNCERTAINTY: short uncertainty or NONE",
    "",
    "Rules:",
    "- Use only the supplied evidence text.",
    "- Every CLAIM must cite one or more evidence IDs that directly support it.",
    "- Do not use model memory to fill gaps.",
    "- Do not invent route names, distances, weather, suitability, dates, or source details.",
    "- Keep the answer useful and concise.",
    "- Do not output JSON.",
    "- Do not add meta-commentary.",
    "",
    "QUESTION:",
    q,
    "",
    "APPROVED EVIDENCE:",
    JSON.stringify(kept)
  ].join("\n");

  let draftRaw="";
  try{
    draftRaw=await runText(ai,draftPrompt,850);
  }catch(err){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"DRAFT_AI_FAILED",
      detail:String(err),
      relevance:rel
    };
  }

  const draft=parseClaims(draftRaw,"CLAIM");
  const draftClaims=draft.claims
    .map(c=>({
      text:c.text,
      source_ids:[...new Set(c.source_ids)].filter(id=>kept.some(e=>e.id===id))
    }))
    .filter(c=>c.text && c.source_ids.length);

  if(!draftClaims.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_DRAFT_CLAIMS",
      relevance:rel,
      debug_draft_raw:draftRaw.slice(0,2200)
    };
  }

  // PASS 3 — STRICT CLAIM VERIFICATION
  const verifyPrompt=[
    "You are the strict claim verifier for The 3 Amigos.",
    "Use ONLY these line formats:",
    "DIRECT: final supported direct answer",
    "VERIFIED: supported claim || SOURCES: 1,2",
    "REJECTED: unsupported claim || REASON: reason",
    "UNCERTAINTY: short uncertainty or NONE",
    "",
    "Rules:",
    "- Check every draft claim against the supplied evidence.",
    "- VERIFIED only if the cited source IDs directly support the claim.",
    "- If only part of a claim is supported, rewrite it down to the supported part.",
    "- Never add new facts.",
    "- The DIRECT line must be based only on VERIFIED claims.",
    "- Do not output JSON.",
    "- Do not add commentary.",
    "",
    "QUESTION:",
    q,
    "",
    "EVIDENCE:",
    JSON.stringify(kept),
    "",
    "DRAFT CLAIMS:",
    JSON.stringify(draftClaims)
  ].join("\n");

  let verifyRaw="";
  try{
    verifyRaw=await runText(ai,verifyPrompt,850);
  }catch(err){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"VERIFY_AI_FAILED",
      detail:String(err),
      relevance:rel,
      debug_draft_raw:draftRaw.slice(0,2200)
    };
  }

  const ver=parseClaims(verifyRaw,"VERIFIED");
  const cleanVerified=ver.claims
    .map(c=>({
      text:c.text,
      source_ids:[...new Set(c.source_ids)].filter(id=>kept.some(e=>e.id===id))
    }))
    .filter(c=>c.text && c.source_ids.length);

  if(!cleanVerified.length){
    return {
      ok:false,
      function:"CLOUDFLARE_EVIDENCE_ANSWER",
      error:"NO_VERIFIED_CLAIMS",
      relevance:rel,
      rejected_claims:ver.rejected,
      debug_draft_raw:draftRaw.slice(0,2200),
      debug_verify_raw:verifyRaw.slice(0,2200)
    };
  }

  const used=[...new Set(cleanVerified.flatMap(c=>c.source_ids))];
  const sources=kept
    .filter(e=>used.includes(e.id))
    .map(e=>({id:e.id,title:e.title,url:e.url}));

  return {
    ok:true,
    function:"CLOUDFLARE_EVIDENCE_ANSWER",
    model:"@cf/meta/llama-3.2-3b-instruct",
    question:q,
    relevance:rel,
    direct_answer:ver.direct_answer || draft.direct_answer,
    claims:cleanVerified,
    uncertainty:(ver.uncertainty && ver.uncertainty!=="NONE") ? ver.uncertainty : "",
    rejected_claims:ver.rejected,
    sources
  };
}
