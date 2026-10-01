function textOf(x){
  if(typeof x==="string") return x;
  if(typeof x?.response==="string") return x.response;
  if(typeof x?.result?.response==="string") return x.result.response;
  if(typeof x?.choices?.[0]?.message?.content==="string") return x.choices[0].message.content;
  if(typeof x?.result?.choices?.[0]?.message?.content==="string") return x.result.choices[0].message.content;
  return "";
}

export async function cloudflareAiAnswer(question, evidence, ai){
  const q=String(question??"").trim();
  const ev=Array.isArray(evidence)?evidence:[];
  if(!q) return {ok:false,function:"CLOUDFLARE_AI_ANSWER",error:"EMPTY_QUESTION"};
  if(!ai?.run) return {ok:false,function:"CLOUDFLARE_AI_ANSWER",error:"AI_BINDING_MISSING"};
  if(!ev.length) return {ok:false,function:"CLOUDFLARE_AI_ANSWER",error:"NO_EVIDENCE"};

  const clipped=ev.slice(0,6).map((e,i)=>({
    n:i+1,
    title:String(e?.title??""),
    url:String(e?.url??""),
    text:String(e?.text??"").slice(0,3000)
  }));

  const prompt=[
    "You are the answer brain for The 3 Amigos.",
    "Answer the user's exact question directly and practically.",
    "Use only the supplied evidence for web-derived factual claims.",
    "Preserve hard boundaries in the user's question.",
    "Do not invent facts or source details.",
    "If evidence is insufficient, say what is missing.",
    "Cite sources inline as [1], [2], etc.",
    "Finish with a short Sources section listing source numbers and URLs.",
    "Do not expose hidden chain-of-thought.",
    "",
    "QUESTION:",
    q,
    "",
    "EVIDENCE:",
    JSON.stringify(clipped)
  ].join("\n");

  const raw=await ai.run("@cf/meta/llama-3.2-3b-instruct",{
    prompt,
    max_tokens:900,
    temperature:0.2
  });

  const answer=textOf(raw).trim();
  return {
    ok:!!answer,
    function:"CLOUDFLARE_AI_ANSWER",
    model:"@cf/meta/llama-3.2-3b-instruct",
    question:q,
    evidence_count:clipped.length,
    answer
  };
}
