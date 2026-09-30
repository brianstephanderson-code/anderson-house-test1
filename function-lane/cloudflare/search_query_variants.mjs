const STOP = new Set([
  "i","me","my","we","our","you","your","a","an","the","and","or","but","if","then",
  "to","of","in","on","at","for","from","with","about","into","through","over","under",
  "want","would","like","go","going","get","find","tell","know","what","which","who",
  "where","when","why","how","is","are","was","were","be","been","being","do","does",
  "did","have","has","had","can","could","should","please","dont","don't","within","out"
]);

function words(text="") {
  return String(text)
    .replace(/[’]/g,"'")
    .replace(/[^\p{L}\p{N}'-]+/gu," ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
}

export function compactSearchQuery(question="") {
  const original=words(question);
  const kept=[];
  for(const token of original) {
    const low=token.toLowerCase();
    if(STOP.has(low)) continue;
    if(/^\d+$/.test(low)) { kept.push(token); continue; }
    if(low.length<2) continue;
    kept.push(token);
  }
  return kept.join(" ").replace(/\s+/g," ").trim();
}

export function searchQueryVariants(question="", limit=4) {
  const q=String(question??"").trim();
  if(!q) return [];

  const compact=compactSearchQuery(q);
  const variants=[];
  const push=v=>{
    const s=String(v??"").replace(/\s+/g," ").trim();
    if(s && !variants.some(x=>x.toLowerCase()===s.toLowerCase())) variants.push(s);
  };

  // Search-engine language first: entities, place, date/season, object, desired answer.
  push(compact);

  // Preserve useful numerical constraints in one cast, but also cast without them
  // because engines often rank the topical answer better before geography is verified later.
  const noDistance=compact
    .replace(/\b\d+\s*(?:km|kilometers?|kilometres?|miles?)\b/gi," ")
    .replace(/\s+/g," ").trim();
  push(noDistance);

  // Small lexical recast for "best" questions; nouns remain untouched.
  push(noDistance.replace(/\bbest\b/gi,"recommended"));

  // Original is last, retained as a provenance/debug cast rather than the primary search language.
  push(q);

  return variants.slice(0,Math.max(1,Math.min(Number(limit)||4,6)));
}
