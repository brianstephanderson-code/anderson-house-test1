function textOf(x){
  if(typeof x === "string") return x;
  if(typeof x?.response === "string") return x.response;
  if(typeof x?.result?.response === "string") return x.result.response;
  if(typeof x?.choices?.[0]?.message?.content === "string") return x.choices[0].message.content;
  if(typeof x?.result?.choices?.[0]?.message?.content === "string") return x.result.choices[0].message.content;
  return "";
}

function parsePlannerText(raw){
  const out={
    interpreted_need:"",
    hard_constraints:[],
    unknown:"",
    casts:[],
    missing:[]
  };

  const lines=String(raw ?? "").split(/\r?\n/);

  for(const rawLine of lines){
    const line=rawLine.trim();
    if(!line) continue;

    let m=line.match(/^NEED\s*:\s*(.+)$/i);
    if(m){ out.interpreted_need=m[1].trim(); continue; }

    m=line.match(/^UNKNOWN\s*:\s*(.+)$/i);
    if(m){ out.unknown=m[1].trim(); continue; }

    m=line.match(/^HARD\s*:\s*(.+)$/i);
    if(m){
      const v=m[1].trim();
      if(v) out.hard_constraints.push(v);
      continue;
    }

    m=line.match(/^CAST\s*:\s*(.+)$/i);
    if(m){
      const v=m[1].trim().replace(/^["']|["']$/g,"");
      if(v) out.casts.push(v);
      continue;
    }

    m=line.match(/^MISSING\s*:\s*(.+)$/i);
    if(m){
      const v=m[1].trim();
      if(v) out.missing.push(v);
      continue;
    }
  }

  // Last-resort fallback: if the model ignores labels but returns quoted queries,
  // recover plausible search casts without requiring valid JSON.
  if(out.casts.length===0){
    const q=[];
    const re=/"([^"\n]{12,220})"/g;
    let m;
    while((m=re.exec(String(raw ?? "")))){
      const v=m[1].trim();
      if(/edinburgh|glasgow|walk|route|path|trail|towpath|canal/i.test(v)) q.push(v);
    }
    out.casts=[...new Set(q)].slice(0,5);
  }

  out.casts=[...new Set(out.casts)].slice(0,5);
  out.hard_constraints=[...new Set(out.hard_constraints)].slice(0,8);
  out.missing=[...new Set(out.missing)].slice(0,8);
  return out;
}

export async function cloudflareAiCastsV20(question, ai){
  const q=String(question ?? "").trim();

  if(!q){
    return {ok:false,function:"CLOUDFLARE_AI_CASTS_V20",error:"EMPTY_QUESTION"};
  }
  if(!ai?.run){
    return {ok:false,function:"CLOUDFLARE_AI_CASTS_V20",error:"AI_BINDING_MISSING"};
  }

  const prompt=[
    "You are the search-planning brain for The 3 Amigos.",
    "Do NOT answer the question.",
    "Return ONLY the following plain-text line format:",
    "NEED: <short description of what is being sought>",
    "UNKNOWN: <the thing to discover>",
    "HARD: <one hard constraint>",
    "HARD: <another hard constraint>",
    "CAST: <search query 1>",
    "CAST: <search query 2>",
    "CAST: <search query 3>",
    "CAST: <search query 4>",
    "CAST: <search query 5>",
    "MISSING: <optional genuinely missing information>",
    "",
    "Rules:",
    "- Exactly 5 CAST lines.",
    "- Preserve every hard boundary in every cast.",
    "- Expand only the unknown/soft wording.",
    "- Do not invent side tasks such as weather unless the user asked for weather.",
    "- For route questions, every CAST must preserve BOTH endpoints and the travel mode.",
    "- Prefer materially different route words such as route, walking route, path, trail, towpath, canal path when appropriate.",
    "- Include one practitioner/end-user/community style cast when useful.",
    "- Do not output JSON.",
    "- Do not output commentary.",
    "",
    "Question: "+q
  ].join("\n");

  let rawText="";
  try{
    const raw=await ai.run("@cf/meta/llama-3.2-3b-instruct",{
      prompt,
      max_tokens:500,
      temperature:0
    });
    rawText=textOf(raw);
  }catch(err){
    return {
      ok:false,
      function:"CLOUDFLARE_AI_CASTS_V20",
      error:"AI_RUN_FAILED",
      detail:String(err)
    };
  }

  const p=parsePlannerText(rawText);

  return {
    ok:p.casts.length>0,
    function:"CLOUDFLARE_AI_CASTS_V20",
    model:"@cf/meta/llama-3.2-3b-instruct",
    question:q,
    interpreted_need:p.interpreted_need,
    hard_constraints:p.hard_constraints,
    unknown:p.unknown,
    casts:p.casts,
    missing:p.missing,
    ...(p.casts.length ? {} : {debug_text_preview:rawText.slice(0,1600)})
  };
}
