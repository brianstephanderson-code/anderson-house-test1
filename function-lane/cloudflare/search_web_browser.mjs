import puppeteer from "@cloudflare/puppeteer";

function htmlText(v=""){
  return String(v??"").replace(/<[^>]+>/g," ").replace(/&amp;/g,"&").replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/s+/g," ").trim();
}

export async function searchDuckDuckGoBrowser(query,limit=10,browserBinding=null){
  const q=String(query??"").trim();
  if(!q) return {ok:false,provider:"DUCKDUCKGO_BROWSER",error:"EMPTY_QUERY",results:[]};
  if(!browserBinding) return {ok:false,provider:"DUCKDUCKGO_BROWSER",error:"NO_BROWSER_BINDING",results:[]};

  const n=Math.max(1,Math.min(Number(limit)||10,20));
  let browser;
  try {
    browser=await puppeteer.launch(browserBinding);
    const page=await browser.newPage();
    const url="https://html.duckduckgo.com/html/?q="+encodeURIComponent(q);
    await page.goto(url,{waitUntil:"domcontentloaded",timeout:20000});
    const rows=await page.$$eval("a.result__a",(nodes,max)=>nodes.slice(0,max).map(a=>({
      title:(a.textContent||"").trim(),
      href:a.getAttribute("href")||""
    })),n);
    const results=[];
    const seen=new Set();
    for(const row of rows||[]){
      let href=String(row.href||"");
      try {
        const u=new URL(href,"https://html.duckduckgo.com");
        const target=u.searchParams.get("uddg");
        if(target) href=decodeURIComponent(target);
      } catch {}
      if(!/^https?:\/\//.test(href)||seen.has(href)) continue;
      seen.add(href);
      results.push({
        title:htmlText(row.title),
        url:href,
        snippet:"",
        source_door:"DUCKDUCKGO_BROWSER",
        provenance:"https://html.duckduckgo.com/html/"
      });
    }
    return {ok:results.length>0,provider:"DUCKDUCKGO_BROWSER",results,error:results.length?null:"NO_RESULTS"};
  } catch(e) {
    return {ok:false,provider:"DUCKDUCKGO_BROWSER",error:String(e?.message??e),results:[]};
  } finally {
    try { if(browser) await browser.close(); } catch {}
  }
}
