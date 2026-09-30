// Common Search Department socket.
// Small functions only: normalize, deduplicate, fan-out, return-as-ready.

export function normalizeResult(item = {}, sourceDoor = "UNKNOWN") {
  return {
    title: String(item.title ?? item.name ?? "").trim(),
    url: String(item.url ?? item.id ?? item.link ?? "").trim(),
    snippet: String(item.snippet ?? item.description ?? item.summary ?? "").trim(),
    source_door: String(item.source_door ?? sourceDoor),
    provenance: item.provenance ?? null
  };
}

export function normalizeResults(items = [], sourceDoor = "UNKNOWN") {
  return Array.isArray(items) ? items.map(x => normalizeResult(x, sourceDoor)).filter(x => x.url) : [];
}

export function deduplicateResults(items = []) {
  const byUrl = new Map();
  for (const x of items) {
    if (!x?.url) continue;
    let key;
    try {
      const u = new URL(x.url);
      u.hash = "";
      ["utm_source","utm_medium","utm_campaign","utm_term","utm_content"].forEach(k => u.searchParams.delete(k));
      key = u.toString().replace(/\/$/, "");
    } catch { key = String(x.url).replace(/\/$/, ""); }
    if (!byUrl.has(key)) byUrl.set(key, {...x, source_doors:[x.source_door].filter(Boolean)});
    else {
      const old=byUrl.get(key);
      old.source_doors=[...new Set([...(old.source_doors||[]),x.source_door].filter(Boolean))];
      if (!old.snippet && x.snippet) old.snippet=x.snippet;
      if (!old.title && x.title) old.title=x.title;
    }
  }
  return [...byUrl.values()];
}

export async function fanOutReturnAsReady({parentTicket, jobs, onReturn}) {
  const started=Date.now();
  let received=0;
  const work=(jobs||[]).map(async (job,i) => {
    const childTicket=job.child_ticket ?? `${parentTicket}-${String(i+1).padStart(2,"0")}`;
    const t=Date.now();
    try {
      const value=await job.run();
      const parcel={type:"CHILD_RETURN",parent_ticket:parentTicket,child_ticket:childTicket,elapsed_ms:Date.now()-t,ok:true,value};
      received++; await onReturn(parcel); return parcel;
    } catch (e) {
      const parcel={type:"CHILD_RETURN",parent_ticket:parentTicket,child_ticket:childTicket,elapsed_ms:Date.now()-t,ok:false,error:String(e?.message??e)};
      received++; await onReturn(parcel); return parcel;
    }
  });
  await Promise.allSettled(work);
  const complete={type:"PARENT_COMPLETE",parent_ticket:parentTicket,expected:work.length,received,elapsed_ms:Date.now()-started};
  await onReturn(complete);
  return complete;
}
