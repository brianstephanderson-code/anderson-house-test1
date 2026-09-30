// Lightweight public-web text reader for Anderson House.
// Fetches HTML only, removes obvious non-reading elements, and returns bounded clean text.
function allowed(u) {
  if (!/^https?:$/.test(u.protocol)) return false;
  const h=u.hostname.toLowerCase();
  if (h==="localhost" || h.endsWith(".local") || h==="0.0.0.0" || h==="127.0.0.1" || h==="::1") return false;
  if (/^(10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.)/.test(h)) return false;
  return true;
}
class Collector {
  constructor(max){this.max=max;this.parts=[];this.n=0;}
  text(t){if(this.n>=this.max)return;const s=t.text.replace(/\s+/g," ");if(!s.trim())return;const x=s.slice(0,this.max-this.n);this.parts.push(x);this.n+=x.length;}
}
class Remove { element(e){e.remove();} }
export async function fetchText(rawUrl, maxChars=60000) {
  let u; try{u=new URL(String(rawUrl??""));}catch{return {ok:false,function:"FETCH_TEXT",error:"BAD_URL"};}
  if(!allowed(u)) return {ok:false,function:"FETCH_TEXT",error:"URL_NOT_ALLOWED"};
  const cap=Math.max(1000,Math.min(Number(maxChars)||60000,100000));
  const r=await fetch(u.toString(),{redirect:"follow",headers:{"accept":"text/html,text/plain;q=0.9","user-agent":"AndersonHouse-Reader/1.0"}});
  if(!r.ok) return {ok:false,function:"FETCH_TEXT",url:u.toString(),error:"HTTP_"+r.status};
  const ct=(r.headers.get("content-type")||"").toLowerCase();
  if(ct.includes("text/plain")){
    const text=(await r.text()).slice(0,cap).replace(/\s+/g," ").trim();
    return {ok:true,function:"FETCH_TEXT",url:r.url||u.toString(),content_type:ct,chars:text.length,text,provenance:r.url||u.toString()};
  }
  if(!ct.includes("text/html")) return {ok:false,function:"FETCH_TEXT",url:r.url||u.toString(),error:"UNSUPPORTED_CONTENT_TYPE",content_type:ct};
  const col=new Collector(cap);
  const cleaned=new HTMLRewriter()
    .on("script",new Remove()).on("style",new Remove()).on("noscript",new Remove())
    .on("svg",new Remove()).on("img",new Remove()).on("nav",new Remove())
    .on("footer",new Remove()).on("form",new Remove()).on("aside",new Remove())
    .on("body",col).transform(r);
  await cleaned.arrayBuffer();
  const text=col.parts.join(" ").replace(/\s+/g," ").trim();
  return {ok:true,function:"FETCH_TEXT",url:r.url||u.toString(),content_type:ct,chars:text.length,text,provenance:r.url||u.toString()};
}
