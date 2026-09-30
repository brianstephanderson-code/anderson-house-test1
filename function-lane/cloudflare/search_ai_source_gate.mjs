import { readTextLinks } from "./read_text_links.mjs";

function clean(v=""){ return String(v??"").replace(/\s+/g," ").trim(); }

function evidenceWindow(text="",terms=[],radius=220){
  const s=clean(text);
  if(!s) return "";
  const lower=s.toLowerCase();
  for(const term of terms){
    const t=String(term??"").toLowerCase().trim();
    if(!t) continue;
    const i=lower.indexOf(t);
    if(i>=0){
      const start=Math.max(0,i-radius);
      const end=Math.min(s.length,i+t.length+radius);
      return s.slice(start,end).trim();
    }
  }
  return s.slice(0,Math.min(450,s.length)).trim();
}

export async function aiSourceGate(parcel={},{
  maxSources=3,
  maxChars=6000,
  evidenceTerms=[],
  reader=readTextLinks
}={}){
  const sources=Array.isArray(parcel.sources)?parcel.sources:[];
  const urls=[];
  const seen=new Set();
  for(const item of sources){
    const url=typeof item==="string"?item:String(item?.url??"");
    if(!/^https?:\/\//i.test(url)||seen.has(url)) continue;
    seen.add(url); urls.push(url);
    if(urls.length>=Math.max(1,Math.min(Number(maxSources)||3,5))) break;
  }

  const evidence=await Promise.all(urls.map(async url=>{
    try{
      const r=await reader(url,{maxChars,maxLinks:10});
      return {
        url,
        ok:!!r.ok,
        provenance:r.provenance??null,
        chars:Number(r.chars??0),
        evidence:evidenceWindow(r.text,evidenceTerms),
        source_links:Array.isArray(r.links)?r.links.slice(0,5):[]
      };
    }catch(e){
      return {url,ok:false,error:String(e),provenance:null,chars:0,evidence:"",source_links:[]};
    }
  }));

  return {
    ok:evidence.some(x=>x.ok&&x.evidence),
    function:"AI_SOURCE_GATE",
    policy:"AI_WORDS_ARE_LEADS_SOURCE_IS_EVIDENCE",
    ai_answer_discarded:true,
    ai_answer_present:Boolean(clean(parcel.answer)),
    source_count:urls.length,
    evidence
  };
}
