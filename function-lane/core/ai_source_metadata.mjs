function clean(v=""){ return String(v??"").trim(); }

function normalizeUrl(value){
  try{
    const u=new URL(clean(value));
    if(!/^https?:$/.test(u.protocol)) return "";
    u.hash="";
    return u.toString();
  }catch{
    return "";
  }
}

function dedupeSources(items=[]){
  const out=[];
  const seen=new Set();
  for(const item of items){
    const url=normalizeUrl(item?.url ?? item?.uri ?? "");
    if(!url || seen.has(url)) continue;
    seen.add(url);
    out.push({
      url,
      title: clean(item?.title),
      source_metadata: clean(item?.source_metadata)
    });
  }
  return out;
}

export function extractGoogleSources(response={}){
  const found=[];

  for(const candidate of Array.isArray(response?.candidates)?response.candidates:[]){
    const gm=candidate?.groundingMetadata ?? candidate?.grounding_metadata ?? {};
    const chunks=gm?.groundingChunks ?? gm?.grounding_chunks ?? [];
    for(const chunk of Array.isArray(chunks)?chunks:[]){
      const web=chunk?.web ?? {};
      found.push({
        url:web?.uri ?? web?.url,
        title:web?.title,
        source_metadata:"GOOGLE_GROUNDING_CHUNK"
      });
    }
  }

  // Gemini Interactions API shape.
  for(const step of Array.isArray(response?.steps)?response.steps:[]){
    for(const block of Array.isArray(step?.content)?step.content:[]){
      for(const ann of Array.isArray(block?.annotations)?block.annotations:[]){
        if(String(ann?.type??"").toLowerCase()!=="url_citation") continue;
        found.push({
          url:ann?.url,
          title:ann?.title,
          source_metadata:"GOOGLE_URL_CITATION"
        });
      }
    }
  }

  return dedupeSources(found);
}

export function extractAwsSources(response={}){
  const found=[];
  for(const item of Array.isArray(response?.output)?response.output:[]){
    for(const block of Array.isArray(item?.content)?item.content:[]){
      for(const ann of Array.isArray(block?.annotations)?block.annotations:[]){
        if(String(ann?.type??"").toLowerCase()!=="url_citation") continue;
        found.push({
          url:ann?.url,
          title:ann?.title,
          source_metadata:"AWS_BEDROCK_URL_CITATION"
        });
      }
    }
  }
  return dedupeSources(found);
}

export function aiSourceParcel(provider, question, response={}){
  const p=clean(provider).toLowerCase();
  const sources=
    p==="google" ? extractGoogleSources(response) :
    p==="aws" ? extractAwsSources(response) :
    [];

  return {
    ok:sources.length>0,
    function:"AI_NATIVE_SOURCE_PARCEL",
    policy:"AI_WORDS_ARE_LEADS_SOURCE_LINKS_ONLY_ENTER_EVIDENCE_PIPE",
    provider:p,
    question:clean(question),
    source_count:sources.length,
    sources
  };
}
