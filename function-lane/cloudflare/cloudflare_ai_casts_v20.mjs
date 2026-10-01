function textOf(x){
  if(typeof x === "string") return x;
  if(typeof x?.response === "string") return x.response;
  if(typeof x?.result?.response === "string") return x.result.response;
  if(typeof x?.choices?.[0]?.message?.content === "string") return x.choices[0].message.content;
  if(typeof x?.result?.choices?.[0]?.message?.content === "string") return x.result.choices[0].message.content;
  return "";
}

function parseJsonLoose(s){
  const t = String(s ?? "").trim()
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/, "");
  try { return JSON.parse(t); } catch {}
  const a=t.indexOf("{"), b=t.lastIndexOf("}");
  if(a>=0 && b>a){
    try { return JSON.parse(t.slice(a,b+1)); } catch {}
  }
  return {};
}

function parsePartialJsonPlanner(s){
  const t=String(s ?? "");
  const out={interpreted_need:"",hard_constraints:[],unknown:"",casts:[],missing:[]};

  const grabString=(key)=>{
    const m=t.match(new RegExp('"'+key+'"\\s*:\\s*"([^"]*)"',"i"));
    return m ? m[1].trim() : "";
  };

  const grabArray=(key)=>{
    const start=t.search(new RegExp('"'+key+'"\\s*:\\s*\\[',"i"));
    if(start<0) return [];
    const tail=t.slice(start);
    const colon=tail.indexOf("[");
    if(colon<0) return [];
    const body=tail.slice(colon+1);
    const end=body.indexOf("]");
    const chunk=end>=0 ? body.slice(0,end) : body;
    const vals=[];
    const re=/"((?:\\.|[^"\\])*)"/g;
    let m;
    while((m=re.exec(chunk))){
      try{ vals.push(JSON.parse('"'+m[1]+'"')); }
      catch{ vals.push(m[1]); }
    }
    return vals.map(x=>String(x).trim()).filter(Boolean);
  };

  out.interpreted_need=grabString("interpreted_need");
  out.unknown=grabString("unknown");
  out.hard_constraints=grabArray("hard_constraints");
  out.casts=grabArray("casts");
  out.missing=grabArray("missing");
  return out;
}

function parseLabeledText(s){
  const out={
    interpreted_need:"",
    hard_constraints:[],
    unknown:"",
    casts:[],
    missing:[]
  };
  const lines=String(s ?? "").split(/\r?\n/);
  let mode="";

  for(const raw of lines){
    const line=raw.trim();
    if(!line) continue;

    const m=line.match(/^([a-z_ ]+)\s*:\s*(.*)$/i);
    if(m){
      const key=m[1].trim().toLowerCase().replace(/\s+/g,"_");
      const val=m[2].trim();

      if(key==="interpreted_need"){
        out.interpreted_need=val;
        mode="interpreted_need";
        continue;
      }
      if(key==="hard_constraints"){ mode="hard_constraints"; continue; }
      if(key==="unknown"){
        out.unknown=val;
        mode="unknown";
        continue;
      }
      if(key==="casts"){ mode="casts"; continue; }
      if(key==="missing"){ mode="missing"; continue; }
    }

    const b=line.match(/^[-*•]\s*(.+)$/);
    if(!b) continue;

    const v=b[1].replace(/^["']|["']$/g,"").trim();
    if(!v) continue;

    if(mode==="hard_constraints") out.hard_constraints.push(v);
    else if(mode==="casts") out.casts.push(v);
    else if(mode==="missing") out.missing.push(v);
    else if(mode==="unknown") out.unknown += (out.unknown ? " | " : "") + v;
  }

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
    "Return ONLY JSON with keys: interpreted_need, hard_constraints, unknown, casts, missing.",
    "unknown means the thing the user is trying to discover, not secondary details such as distance or duration.",
    "casts must contain EXACTLY 5 materially different web-search queries.",
    "Keep every field short. Do not repeat equivalent casts. Do not add commentary.",
    "Preserve every hard boundary in the user's question.",
    "Expand ONLY the unknown/soft wording.",
    "Do not invent side tasks such as weather unless the user asked for weather.",
    "For route questions, every cast must preserve BOTH endpoints and the requested travel mode.",
    "Prefer direct route terms such as route, walking route, path, trail, towpath, canal path when appropriate.",
    "Include one practitioner/end-user/community cast when useful.",
    "Do not invent URLs or sources.",
    "Question: "+q
  ].join("\n");

  const raw=await ai.run("@cf/meta/llama-3.2-3b-instruct",{
    prompt,
    max_tokens:500,
    temperature:0,
    response_format:{type:"json_object"}
  });

  const rawText=textOf(raw);

  let p=parseJsonLoose(rawText);
  if(!Array.isArray(p?.casts) || p.casts.length===0){
    p=parsePartialJsonPlanner(rawText);
  }
  if(!Array.isArray(p?.casts) || p.casts.length===0){
    p=parseLabeledText(rawText);
  }

  const casts=(Array.isArray(p?.casts) ? p.casts : [])
    .map(x=>String(x ?? "").trim())
    .filter(Boolean)
    .slice(0,6);

  return {
    ok:casts.length>0,
    function:"CLOUDFLARE_AI_CASTS_V20",
    model:"@cf/meta/llama-3.2-3b-instruct",
    question:q,
    interpreted_need:String(p?.interpreted_need ?? "").trim(),
    hard_constraints:Array.isArray(p?.hard_constraints) ? p.hard_constraints : [],
    unknown:String(p?.unknown ?? "").trim(),
    casts,
    missing:Array.isArray(p?.missing) ? p.missing : [],
    ...(casts.length ? {} : {debug_text_preview:rawText.slice(0,1200)})
  };
}
