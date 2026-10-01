#!/data/data/com.termux/files/usr/bin/python
# V14 UNKNOWN-FIRST BLACKBOARD FAN-OUT
# One job: identify the unknown, lock boundaries, widen only the unknown,
# then compile clean search casts.

import re
from pathlib import Path

STOP = {
    "the","a","an","is","are","was","were","be","been","being","do","does","did",
    "can","could","would","should","will","may","might","of","for","to","from","in",
    "on","at","by","with","and","or","this","that","these","those","there","here",
    "i","we","you","they","he","she","it","my","our","your","their","what","when",
    "where","which","who","why","how"
}

UNKNOWN_FAMILIES = {
    "route": [
        "route","walking route","path","trail","footpath","towpath",
        "pedestrian route","long-distance walk","walking itinerary"
    ],
    "time": [
        "best time","best season","peak season","best month","timing",
        "seasonal window","peak period","when most successful"
    ],
    "date": [
        "date","date of birth","birthday","born on"
    ],
    "bait": [
        "bait","best bait","natural bait","bait choice","most effective bait",
        "successful bait","preferred bait"
    ],
    "cause": [
        "cause","reason","root cause","culprit","source of the problem"
    ],
    "method": [
        "method","way","approach","procedure","technique"
    ],
    "choice": [
        "best option","best choice","top choice","most suitable option"
    ],
    "association": [
        "best known for","most famous for","strongest association",
        "iconic for","commonly associated with"
    ],
    "example": [
        "real-world example","case study","end-user example","operator report",
        "practical example","documented example"
    ],
    "function": [
        "function","purpose","job","role","what it does"
    ],
    "thing": [
        "answer","result","solution","option","example"
    ],
}

OPTIMIZERS = {
    "best","earliest","latest","cheapest","fastest","closest","nearest","longest",
    "shortest","most","least","highest","lowest","optimal","ideal","maximum","minimum"
}

MODE_WORDS = {
    "walk","walking","hike","hiking","drive","driving","fly","flight","train",
    "bus","ferry","boat","cycle","cycling","bike","biking"
}

TIME_WORDS = [
    "today","tomorrow","tonight","now","summer","winter","spring","autumn","fall",
    "january","february","march","april","may","june","july","august","september",
    "october","november","december"
]

def clean(s):
    return re.sub(r"\s+"," ",str(s or "")).strip()

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

def extract_route_bounds(q):
    # "from Edinburgh, Scotland to Glasgow, Scotland in the summer"
    m=re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)(?=\s+(?:in|during|for|on|at)\b|[?.!,;:]|$)",
        q, re.I
    )
    if not m:
        return None, None
    return clean(m.group(1)), clean(m.group(2))

def extract_time(q):
    low=q.lower()
    vals=[]
    for w in TIME_WORDS:
        if re.search(r"\b"+re.escape(w)+r"\b",low):
            vals.append(w)
    for m in re.finditer(r"\bwithin\s+\d+\s*(?:km|kms|kilometres|kilometers|miles|mi|hours?|days?|weeks?)\b",low):
        vals.append(clean(m.group(0)))
    return unique(vals)

def extract_mode(q):
    low=q.lower()
    vals=[]
    for w in MODE_WORDS:
        if re.search(r"\b"+re.escape(w)+r"\b",low):
            vals.append(w)
    return unique(vals)

def extract_optimizer(q):
    toks=re.findall(r"[A-Za-z'-]+",q.lower())
    return unique([t for t in toks if t in OPTIMIZERS])

def infer_unknown(q):
    low=q.lower().strip()

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

    if re.search(r"\bfunction of\b",low):
        return "function","function"

    # "best bait", "best time", "best hotel", etc.
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

    if re.match(r"^what\b",low):
        return "thing","answer"

    if re.match(r"^which\b",low):
        return "choice","choice"

    if re.match(r"^where\b",low):
        return "thing","place"

    if re.match(r"^who\b",low):
        return "thing","person"

    return "thing","answer"

def infer_subject_terms(q, unknown_word, hard_strings):
    toks=re.findall(r"[A-Za-z][A-Za-z'-]*",q.lower())
    hard_blob=" ".join(hard_strings).lower()
    vals=[]
    for t in toks:
        if t in STOP or t in OPTIMIZERS or t in MODE_WORDS or t in TIME_WORDS:
            continue
        if t == unknown_word.lower():
            continue
        if t in hard_blob:
            continue
        if len(t)<3:
            continue
        vals.append(t)
    return unique(vals)[:7]

def build_blackboard(question, geo_pack=None):
    q=clean(question)
    geo_pack=geo_pack or {}

    frm,to=extract_route_bounds(q)
    locations=[]

    if frm: locations.append(frm)
    if to: locations.append(to)

    for x in geo_pack.get("target_terms",[]) or []:
        if x:
            locations.append(x)

    time_terms=extract_time(q)
    modes=extract_mode(q)
    optimizers=extract_optimizer(q)
    unknown_type,unknown_word=infer_unknown(q)

    hard_strings=unique(locations+time_terms+modes)
    subjects=infer_subject_terms(q,unknown_word,hard_strings)

    done={
        "route":"one or more practical routes satisfying all fixed boundaries",
        "time":"a supported time window satisfying all fixed boundaries",
        "date":"a verified date for the identified subject",
        "bait":"one or more supported bait choices within all fixed boundaries",
        "cause":"one or more supported causes that explain the stated problem",
        "method":"one or more practical methods satisfying all fixed boundaries",
        "choice":"a supported comparison leading to the requested choice",
        "association":"a supported strongest public association",
        "example":"several independent real-world examples",
        "function":"a clear statement of what the target does",
        "thing":"a supported answer satisfying all fixed boundaries",
    }.get(unknown_type,"a supported answer")

    return {
        "question":q,
        "unknown":{
            "type":unknown_type,
            "word":unknown_word,
            "family":UNKNOWN_FAMILIES.get(unknown_type,UNKNOWN_FAMILIES["thing"])
        },
        "boundaries":{
            "from":frm,
            "to":to,
            "locations":unique(locations),
            "time":time_terms,
            "mode":modes,
        },
        "optimizer":optimizers,
        "subject_terms":subjects,
        "done_condition":done,
        "rule":"Expand the unknown. Preserve the boundaries."
    }

def compile_casts(board,max_casts=10):
    q=board["question"]
    fam=board["unknown"]["family"]
    b=board["boundaries"]
    subjects=board["subject_terms"]
    opts=board["optimizer"]

    fixed=[]
    if b.get("from"): fixed += ["from",b["from"]]
    if b.get("to"): fixed += ["to",b["to"]]

    # Add location terms not already inside route endpoints.
    endpoint_blob=(" ".join([b.get("from") or "",b.get("to") or ""])).lower()
    for x in b.get("locations",[]):
        if x.lower() not in endpoint_blob:
            fixed.append(x)

    fixed += b.get("mode",[])
    fixed += b.get("time",[])

    subject=" ".join(unique(subjects+opts))
    fixed_text=" ".join(fixed)

    casts=[]
    def add(query,why):
        query=clean(query)
        if not query:
            return
        if query.lower() not in [x["query"].lower() for x in casts]:
            casts.append({"query":query,"why":why})

    add(q,"original question")

    # Unknown-first casts.
    for alt in fam:
        if len(casts)>=max_casts:
            break
        add(" ".join([alt,subject,fixed_text]),"unknown semantic fan-out")

    # Practical evidence lanes, still preserving the same unknown and boundaries.
    base=" ".join([fam[0],subject,fixed_text])
    for suffix,why in [
        ("real-world example","real-world evidence lane"),
        ("practitioner operator experience","practitioner lane"),
        ("end-user experience trip report forum","end-user lane"),
    ]:
        if len(casts)>=max_casts:
            break
        add(base+" "+suffix,why)

    return casts[:max_casts]

def semantic_fanout(question, geo_pack=None, max_casts=10):
    board=build_blackboard(question,geo_pack or {})
    casts=compile_casts(board,max_casts)
    return {
        "question":board["question"],
        "blackboard":board,
        "hard_constraints":board["boundaries"],
        "flexible_terms":[board["unknown"]["word"]],
        "casts":casts,
        "count":len(casts),
    }

if __name__=="__main__":
    import json,sys
    q=" ".join(sys.argv[1:]) if len(sys.argv)>1 else "Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?"
    print(json.dumps(semantic_fanout(q,{},10),indent=2))
