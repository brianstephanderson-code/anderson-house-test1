// Borged text-browser pattern: readable text + useful links.
// Independent from FETCH_TEXT so either function can evolve separately.

class Remove { element(e){ e.remove(); } }
class TextCollector {
  constructor(max){this.max=max;this.parts=[];this.n=0;}
  text(t){if(this.n>=this.max)return;const s=t.text.replace(/\s+/g," ");if(!s.trim())return;const x=s.slice(0,this.max-this.n);this.parts.push(x);this.n+=x.length;}
}
class LinkCollector {
  constructor(base,max){this.base=base;this.max=max;this.links=[];this.seen=new Set();}
  element(e){
    if(this.links.length>=this.max)return;
    const href=e.getAttribute("href"); if(!href)return;
    let u; try{u=new URL(href,this.base);}catch{return;}
    if(!/^https?:$/.test(u.protocol))return;
    u.hash=""; const key=u.toString();
    if(this.seen.has(key))return; this.seen.add(key);
    this.links.push({url:key,text:""});
  }
}
function publicUrl(u){
  if(!/^https?:$/.test(u.protocol))return false;
  const h=u.hostname.toLowerCase();
  if(h==="localhost"||h.endsWith(".local")||h==="0.0.0.0"||h==="127.0.0.1"||h==="::1")return false;
  if(/^(10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.)/.test(h))return false;
  return true;
}
export async function readTextLinks(rawUrl,{maxChars=60000,maxLinks=100}={}){
  let u; try{u=new URL(String(rawUrl??""));}catch{return {ok:false,function:"READ_TEXT_LINKS",error:"BAD_URL"};}
  if(!publicUrl(u))return {ok:false,function:"READ_TEXT_LINKS",error:"URL_NOT_ALLOWED"};
  const r=await fetch(u.toString(),{redirect:"follow",headers:{accept:"text/html","user-agent":"AndersonHouse-Reader/1.0"}});
  if(!r.ok)return {ok:false,function:"READ_TEXT_LINKS",error:"HTTP_"+r.status,url:u.toString()};
  const ct=(r.headers.get("content-type")||"").toLowerCase();
  if(!ct.includes("text/html"))return {ok:false,function:"READ_TEXT_LINKS",error:"UNSUPPORTED_CONTENT_TYPE",content_type:ct,url:r.url};
  const text=new TextCollector(Math.max(1000,Math.min(+maxChars||60000,100000)));
  const links=new LinkCollector(r.url||u.toString(),Math.max(1,Math.min(+maxLinks||100,500)));
  const out=new HTMLRewriter()
    .on("script",new Remove()).on("style",new Remove()).on("noscript",new Remove())
    .on("svg",new Remove()).on("img",new Remove()).on("form",new Remove())
    .on("body",text).on("a[href]",links).transform(r);
  await out.arrayBuffer();
  const readable=text.parts.join(" ").replace(/\s+/g," ").trim();
  return {ok:true,function:"READ_TEXT_LINKS",url:r.url||u.toString(),chars:readable.length,text:readable,links:links.links,link_count:links.links.length,provenance:r.url||u.toString()};
}
