#!/data/data/com.termux/files/usr/bin/python
# V15 BOOLEAN + SEMANTIC HYBRID FAN-OUT
# Rule: lock hard concepts with AND; widen the unknown with OR.

import re

UNKNOWN_FAMILIES = {
    "route": ["route","path","trail","footpath","towpath","walking route","pedestrian route","long-distance walk"],
    "time": ["best time","best season","peak season","best month","timing","seasonal window","peak period"],
    "date": ["date","birthday","date of birth","born on"],
    "bait": ["bait","natural bait","bait choice","most effective bait","successful bait","preferred bait"],
    "cause": ["cause","reason","root cause","culprit","source"],
    "method": ["method","way","approach","procedure","technique"],
    "choice": ["best option","best choice","top choice","most suitable option"],
    "association": ["best known for","most famous for","iconic for","commonly associated with"],
    "example": ["real-world example","case study","end-user example","operator report","practical example"],
    "function": ["function","purpose","job","role","what it does"],
    "thing": ["answer","result","solution","option"],
}

def clean(s):
    return re.sub(r"\s+"," ",str(s or "")).strip()

def quote_if_needed(s):
    s=clean(s)
    if not s:
        return ""
    if " " in s or "," in s:
        return '"' + s.replace('"','') + '"'
    return s

def unique(seq):
    out=[]
    seen=set()
    for x in seq:
        x=clean(x)
        if not x:
            continue
        k=x.lower()
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out

def extract_route(question):
    q=clean(question)
    m=re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)(?=\s+(?:in|during|for|on|at)\b|[?.!,;:]|$)",
        q,re.I
    )
    if not m:
        return None,None
    return clean(m.group(1)),clean(m.group(2))

def infer_unknown(question):
    low=clean(question).lower()

    if re.search(r"\bis there (?:a|any) way\b",low):
        return "route","way"

    if re.match(r"^when\b",low):
        if "birthday" in low or "born" in low:
            return "date","date"
        return "time","time"

    if re.match(r"^why\b",low):
        return "cause","cause"

    if re.match(r"^how\b",low):
        return "method","method"

    if "most famous for" in low or "best known for" in low:
        return "association","association"

    if "real-life example" in low or "real life example" in low or "real-world example" in low:
        return "example","example"

    if "function of" in low:
        return "function","function"

    m=re.search(r"\b(?:best|ideal|optimal|earliest|cheapest|fastest|closest|nearest)\s+([a-z][a-z'-]*)",low)
    if m:
        noun=m.group(1)
        if noun in ("time","season","month","period","window"):
            return "time",noun
        if noun in ("bait","lure"):
            return "bait",noun
        if noun in ("route","way","path"):
            return "route",noun
        return "choice",noun

    return "thing","answer"

def build_state(question,geo_pack=None):
    q=clean(question)
    geo_pack=geo_pack or {}
    unknown_type,unknown_word=infer_unknown(q)
    frm,to=extract_route(q)

    locations=[]
    if frm: locations.append(frm)
    if to: locations.append(to)
    for x in geo_pack.get("target_terms",[]) or []:
        locations.append(x)
    locations=unique(locations)

    low=q.lower()
    modes=[]
    for m in ["walk","walking","hike","hiking","drive","driving","flight","fly","train","bus","ferry","cycle","cycling"]:
        if re.search(r"\b"+re.escape(m)+r"\b",low):
            modes.append(m)
    modes=unique(modes)

    times=[]
    for t in ["today","tomorrow","tonight","now","summer","winter","spring","autumn","fall",
              "january","february","march","april","may","june","july","august","september","october","november","december"]:
        if re.search(r"\b"+re.escape(t)+r"\b",low):
            times.append(t)
    times=unique(times)

    return {
        "question":q,
        "unknown":{"type":unknown_type,"word":unknown_word,"family":UNKNOWN_FAMILIES.get(unknown_type,UNKNOWN_FAMILIES["thing"])},
        "hard":{
            "from":frm,
            "to":to,
            "locations":locations,
            "modes":modes,
            "times":times,
        },
        "rule":"AND the hard concepts; OR the unknown's semantic family."
    }

def hard_terms(state):
    h=state["hard"]
    terms=[]

    # For route questions, endpoints are the critical hard boundary.
    if h.get("from"):
        terms.append(h["from"])
    if h.get("to"):
        terms.append(h["to"])

    endpoint_blob=(" ".join([h.get("from") or "",h.get("to") or ""])).lower()

    for x in h.get("locations",[]):
        if x.lower() not in endpoint_blob:
            terms.append(x)

    # Canonicalize walking as the mode term when any walk variant is present.
    if any(x in h.get("modes",[]) for x in ["walk","walking","hike","hiking"]):
        terms.append("walking")
    else:
        terms += h.get("modes",[])

    terms += h.get("times",[])
    return unique(terms)

def boolean_query(state,family=None):
    hard=[quote_if_needed(x) for x in hard_terms(state) if x]
    fam=family or state["unknown"]["family"]
    ors=[quote_if_needed(x) for x in unique(fam) if x]

    if ors:
        unknown_clause="("+" OR ".join(ors)+")"
    else:
        unknown_clause=""

    parts=hard + ([unknown_clause] if unknown_clause else [])
    return " AND ".join(parts)

def compile_casts(state,max_casts=10):
    casts=[]

    def add(q,why):
        q=clean(q)
        if not q:
            return
        if q.lower() not in [x["query"].lower() for x in casts]:
            casts.append({"query":q,"why":why})

    add(state["question"],"original question")

    fam=state["unknown"]["family"]

    # Main hybrid cast: hard boundaries locked with AND, vocabulary widened with OR.
    add(boolean_query(state,fam),"boolean backbone + semantic OR family")

    # Smaller OR families improve compatibility with engines that simplify long Boolean strings.
    chunks=[fam[i:i+3] for i in range(0,len(fam),3)]
    for chunk in chunks:
        if len(casts)>=max_casts:
            break
        add(boolean_query(state,chunk),"compact Boolean semantic chunk")

    # Exact-boundary plain-language fallback variants.
    h=" ".join(hard_terms(state))
    for alt in fam:
        if len(casts)>=max_casts:
            break
        add(clean(h+" "+alt),"plain fallback preserving hard boundaries")

    return casts[:max_casts]

def semantic_fanout(question,geo_pack=None,max_casts=10):
    state=build_state(question,geo_pack or {})
    casts=compile_casts(state,max_casts)
    return {
        "question":state["question"],
        "blackboard":state,
        "hard_constraints":state["hard"],
        "flexible_terms":[state["unknown"]["word"]],
        "boolean_query":boolean_query(state),
        "casts":casts,
        "count":len(casts),
    }

if __name__=="__main__":
    import json,sys
    q=" ".join(sys.argv[1:]) if len(sys.argv)>1 else "Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?"
    print(json.dumps(semantic_fanout(q,{},10),indent=2))
