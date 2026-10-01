#!/data/data/com.termux/files/usr/bin/python
# V12 Semantic Fan-Out for the 3 Amigos
# Goal: widen search language while preserving hard boundaries.

import re
from itertools import product

MAX_CASTS = 12

SYN = {
    "best": ["best", "optimal", "ideal", "peak", "prime", "most productive", "highest chance"],
    "time": ["time", "season", "month", "period", "window", "timing", "peak"],
    "catch": ["catch", "caught", "land", "landed", "hook", "hooked", "target", "encounter"],
    "walk": ["walk", "walking route", "long-distance walk", "footpath", "hiking route", "trail", "pedestrian route"],
    "way": ["route", "way", "path", "connection", "itinerary"],
    "examples": ["examples", "real-world examples", "case studies", "reports", "user experiences"],
    "people": ["people", "users", "operators", "practitioners", "builders"],
    "experience": ["experience", "experiences", "reports", "feedback", "lessons learned"],
    "famous": ["famous", "best known", "most associated with", "iconic", "well known for"],
    "flight": ["flight", "air itinerary", "air route", "departure"],
    "earliest": ["earliest", "soonest", "next available", "first available"],
    "hotel": ["hotel", "accommodation", "lodging", "place to stay"],
}

MODE_WORDS = {
    "walk","walking","hike","hiking","flight","fly","drive","driving","train","bus","ferry","boat"
}

TIME_PATTERNS = [
    r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b",
    r"\b(?:spring|summer|autumn|fall|winter)\b",
    r"\b(?:today|tomorrow|tonight|now|this week|next week|this month|next month)\b",
    r"\bwithin\s+\d+\s*(?:km|kms|kilometres|kilometers|miles|mi)\b",
]

def clean(s):
    return re.sub(r"\s+"," ",str(s or "")).strip()

def tokenize(q):
    return re.findall(r"[A-Za-z][A-Za-z'-]*", clean(q).lower())

def extract_hard_constraints(question, geo_pack=None):
    q=clean(question)
    low=q.lower()
    hard={"locations":[],"time":[],"numbers":[],"mode":[]}

    if geo_pack:
        for x in geo_pack.get("target_terms",[]) or []:
            if x and x not in hard["locations"]:
                hard["locations"].append(x)

    # Capitalized multi-word place-like phrases after common prepositions.
    for m in re.finditer(r"\b(?:in|from|to|near|around|within)\s+([A-Z][A-Za-z .'-]{1,70}?)(?=\s+(?:in|from|to|near|around|within|for|during|on|at|this|next|with|and|or)\b|[?.!,;:]|$)", q):
        p=clean(m.group(1))
        if p and p not in hard["locations"]:
            hard["locations"].append(p)

    for pat in TIME_PATTERNS:
        for m in re.finditer(pat, low, re.I):
            v=clean(m.group(0))
            if v not in hard["time"]:
                hard["time"].append(v)

    for m in re.finditer(r"\b\d+(?:\.\d+)?\s*(?:km|kms|kilometres|kilometers|miles|mi|hours?|days?|weeks?)\b",low):
        v=clean(m.group(0))
        if v not in hard["numbers"]:
            hard["numbers"].append(v)

    for w in tokenize(q):
        if w in MODE_WORDS and w not in hard["mode"]:
            hard["mode"].append(w)

    return hard

def important_flexible_terms(question, hard):
    toks=tokenize(question)
    hard_text=" ".join(sum((v for v in hard.values()),[])).lower()
    out=[]
    for t in toks:
        if len(t)<3: continue
        if t in {"the","and","for","with","from","into","there","what","when","where","which","who","how","does","can","could","would","should","this","that","are","was","were","is","a","an","of","in","to","on","at"}:
            continue
        if t in hard_text:
            continue
        if t not in out:
            out.append(t)
    return out[:8]

def meaning_family(term):
    t=term.lower()
    if t in SYN:
        return SYN[t]
    if t.endswith("ing") and t[:-3] in SYN:
        return SYN[t[:-3]]
    if t.endswith("ed") and t[:-2] in SYN:
        return SYN[t[:-2]]
    return [term]

def semantic_fanout(question, geo_pack=None, max_casts=MAX_CASTS):
    q=clean(question)
    hard=extract_hard_constraints(q, geo_pack or {})
    flex=important_flexible_terms(q, hard)

    # Keep original constraints as an immutable suffix.
    fixed=[]
    for group in ("locations","time","numbers","mode"):
        for x in hard[group]:
            if x and x.lower() not in [z.lower() for z in fixed]:
                fixed.append(x)
    fixed_suffix=" ".join(fixed)

    casts=[]
    def add(s, why):
        s=clean(s)
        if not s: return
        key=s.lower()
        if key not in [x["query"].lower() for x in casts]:
            casts.append({"query":s,"why":why})

    add(q,"original question")

    # WHAT-first compact cast: flexible concepts first, hard constraints after.
    if flex:
        add(" ".join(flex)+" "+fixed_suffix,"WHAT-first compact cast")

    # Expand one important concept at a time; never explode all combinations.
    for term in flex:
        fam=meaning_family(term)
        if len(fam)<=1:
            continue
        for alt in fam[1:4]:
            words=[]
            replaced=False
            for tok in flex:
                if tok==term and not replaced:
                    words.append(alt); replaced=True
                else:
                    words.append(tok)
            add(" ".join(words)+" "+fixed_suffix,f"semantic expansion of '{term}'")
            if len(casts)>=max_casts:
                break
        if len(casts)>=max_casts:
            break

    # Evidence-lane fan-out only after semantic casts.
    base=(" ".join(flex)+" "+fixed_suffix).strip() or q
    for suffix,why in [
        (" real-world examples","real-world evidence lane"),
        (" practitioner operator supplier experience","practitioner/provider lane"),
        (" end-user experience forum trip report","end-user lane"),
    ]:
        if len(casts)>=max_casts: break
        add(base+suffix,why)

    return {
        "question":q,
        "hard_constraints":hard,
        "flexible_terms":flex,
        "casts":casts[:max_casts],
        "count":min(len(casts),max_casts),
    }

if __name__=="__main__":
    import json,sys
    question=" ".join(sys.argv[1:]) if len(sys.argv)>1 else "Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?"
    print(json.dumps(semantic_fanout(question),indent=2))
