#!/data/data/com.termux/files/usr/bin/python
# V11 Universal Geography Gate for 3 Amigos
import re
from urllib.parse import urlparse

# Country aliases -> ISO alpha-2 / ccTLD.
# The resolver is intentionally conservative: a country-code domain is supporting
# evidence, not enough by itself when page text conflicts or location is ambiguous.
COUNTRIES = {
"afghanistan":"af","albania":"al","algeria":"dz","andorra":"ad","angola":"ao","argentina":"ar",
"armenia":"am","australia":"au","austria":"at","azerbaijan":"az","bahamas":"bs","bahrain":"bh",
"bangladesh":"bd","barbados":"bb","belarus":"by","belgium":"be","belize":"bz","benin":"bj",
"bhutan":"bt","bolivia":"bo","bosnia and herzegovina":"ba","botswana":"bw","brazil":"br",
"brunei":"bn","bulgaria":"bg","burkina faso":"bf","burundi":"bi","cambodia":"kh","cameroon":"cm",
"canada":"ca","cape verde":"cv","chile":"cl","china":"cn","colombia":"co","costa rica":"cr",
"croatia":"hr","cuba":"cu","cyprus":"cy","czech republic":"cz","czechia":"cz","denmark":"dk",
"djibouti":"dj","dominica":"dm","dominican republic":"do","ecuador":"ec","egypt":"eg",
"el salvador":"sv","estonia":"ee","ethiopia":"et","fiji":"fj","finland":"fi","france":"fr",
"gabon":"ga","gambia":"gm","georgia":"ge","germany":"de","ghana":"gh","greece":"gr",
"grenada":"gd","guatemala":"gt","guinea":"gn","guyana":"gy","haiti":"ht","honduras":"hn",
"hungary":"hu","iceland":"is","india":"in","indonesia":"id","iran":"ir","iraq":"iq","ireland":"ie",
"israel":"il","italy":"it","jamaica":"jm","japan":"jp","jordan":"jo","kazakhstan":"kz",
"kenya":"ke","kuwait":"kw","kyrgyzstan":"kg","laos":"la","latvia":"lv","lebanon":"lb",
"lesotho":"ls","liberia":"lr","libya":"ly","liechtenstein":"li","lithuania":"lt","luxembourg":"lu",
"madagascar":"mg","malawi":"mw","malaysia":"my","maldives":"mv","mali":"ml","malta":"mt",
"mauritania":"mr","mauritius":"mu","mexico":"mx","moldova":"md","monaco":"mc","mongolia":"mn",
"montenegro":"me","morocco":"ma","mozambique":"mz","myanmar":"mm","namibia":"na","nepal":"np",
"netherlands":"nl","new zealand":"nz","nicaragua":"ni","niger":"ne","nigeria":"ng",
"north korea":"kp","north macedonia":"mk","norway":"no","oman":"om","pakistan":"pk","panama":"pa",
"papua new guinea":"pg","paraguay":"py","peru":"pe","philippines":"ph","poland":"pl","portugal":"pt",
"qatar":"qa","romania":"ro","russia":"ru","rwanda":"rw","saudi arabia":"sa","senegal":"sn",
"serbia":"rs","singapore":"sg","slovakia":"sk","slovenia":"si","somalia":"so","south africa":"za",
"south korea":"kr","spain":"es","sri lanka":"lk","sudan":"sd","suriname":"sr","sweden":"se",
"switzerland":"ch","syria":"sy","taiwan":"tw","tajikistan":"tj","tanzania":"tz","thailand":"th",
"togo":"tg","tonga":"to","trinidad and tobago":"tt","tunisia":"tn","turkey":"tr","türkiye":"tr",
"turkmenistan":"tm","uganda":"ug","ukraine":"ua","united arab emirates":"ae","uae":"ae",
"united kingdom":"uk","uk":"uk","united states":"us","united states of america":"us","usa":"us",
"uruguay":"uy","uzbekistan":"uz","vanuatu":"vu","venezuela":"ve","vietnam":"vn","yemen":"ye",
"zambia":"zm","zimbabwe":"zw"
}

REGION_HINTS = {
"western australia": ("australia","au"),
"new south wales": ("australia","au"),
"queensland": ("australia","au"),
"victoria": ("australia","au"),
"south australia": ("australia","au"),
"tasmania": ("australia","au"),
"northern territory": ("australia","au"),
"australian capital territory": ("australia","au"),
"florida": ("united states","us"),
"california": ("united states","us"),
"texas": ("united states","us"),
"washington state": ("united states","us"),
"scotland": ("united kingdom","uk"),
"england": ("united kingdom","uk"),
"wales": ("united kingdom","uk"),
"northern ireland": ("united kingdom","uk"),
}

FALSE_PLACE_PHRASES = {
"the internet","internet","the web","web","online","github","reddit","youtube"
}

def _clean(s):
    return re.sub(r"\s+"," ",str(s or "")).strip()

def _host(url):
    try:
        h=(urlparse(str(url or "")).hostname or "").lower()
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""

def _extract_place_phrase(q):
    q=_clean(q)
    # Useful simple phrase catcher for city/region requests:
    # in Athens for a week; near Perth; around Albany; to Greece.
    m=re.search(r"\b(?:in|near|around|within|to|from)\s+([A-Z][A-Za-z .'-]{1,60}?)(?=\s+(?:for|during|on|at|this|next|with|and|or)\b|[?.!,;:]|$)",q)
    if not m:
        return None
    p=_clean(m.group(1))
    return None if p.lower() in FALSE_PLACE_PHRASES else p

def build_geo_pack(question, supplied_geo=""):
    q=_clean(question)
    low=q.lower()
    explicit_countries=[]
    for name,cc in sorted(COUNTRIES.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b"+re.escape(name)+r"\b",low):
            explicit_countries.append((name,cc))
    region=None
    region_country=None
    region_cc=None
    for name,(country,cc) in REGION_HINTS.items():
        if re.search(r"\b"+re.escape(name)+r"\b",low):
            region=name
            region_country=country
            region_cc=cc
            break
    place=_extract_place_phrase(q)
    # Specific historical shorthand: bridge geo=WA means Western Australia only
    # when question context also points to Australia/Perth/etc.
    if str(supplied_geo or "").upper()=="WA" and (
        "western australia" in low or "australia" in low or
        any(x in low for x in ("perth","albany","denmark","esperance","bunbury","fremantle","mandurah"))
    ):
        region="western australia"; region_country="australia"; region_cc="au"
    country=explicit_countries[0][0] if explicit_countries else region_country
    cc=explicit_countries[0][1] if explicit_countries else region_cc
    target_terms=[]
    for x in (place,region,country):
        if x and x.lower() not in [t.lower() for t in target_terms]:
            target_terms.append(x)
    requires=bool(explicit_countries or region or place)
    return {
        "enabled": requires,
        "place": place,
        "region": region,
        "country": country,
        "country_code": cc,
        "target_terms": target_terms,
        "supplied_geo": supplied_geo or None,
    }

def classify_source(pack,url,text):
    if not pack.get("enabled"):
        return {"state":"ACCEPT","reason":"GEO_NOT_REQUIRED"}
    host=_host(url)
    body=_clean(text).lower()
    terms=[str(x).lower() for x in pack.get("target_terms",[]) if x]
    cc=pack.get("country_code")
    # Special high-confidence false friend caught generically.
    if "western australia" in terms:
        if host=="wdfw.wa.gov" or "washington state" in body or "puget sound" in body:
            return {"state":"REJECT","reason":"WASHINGTON_NOT_WESTERN_AUSTRALIA"}
        if host.endswith(".gov") and not host.endswith(".gov.au"):
            return {"state":"REJECT","reason":"NON_AU_GOV_FOR_WESTERN_AUSTRALIA"}
    # Strong explicit target text.
    if any(t in body for t in terms if len(t)>=4):
        return {"state":"ACCEPT","reason":"TARGET_TEXT_MATCH"}
    # Exact country ccTLD supports location, but by itself is not infallible.
    if cc and (host.endswith("."+cc) or host.endswith(".gov."+cc)):
        return {"state":"ACCEPT","reason":"TARGET_COUNTRY_DOMAIN"}
    # If page explicitly names another known country and not the target, reject.
    target_country=(pack.get("country") or "").lower()
    others=[]
    for name in COUNTRIES:
        if name!=target_country and len(name)>=5 and re.search(r"\b"+re.escape(name)+r"\b",body):
            others.append(name)
    if others and target_country:
        return {"state":"REJECT","reason":"EXPLICIT_OTHER_COUNTRY","other_country":others[0]}
    # Bare abbreviations, generic .com/.org, or unresolved city names remain HOLD.
    return {"state":"HOLD","reason":"LOCATION_NOT_PROVEN"}

def apply_geo_gate(question,supplied_geo,evidence):
    pack=build_geo_pack(question,supplied_geo)
    if not pack["enabled"]:
        return {"enabled":False,"pack":pack,"accepted":list(evidence),"held":[],"rejected":[]}
    accepted=[]; held=[]; rejected=[]
    for row in evidence:
        r=classify_source(pack,row.get("url",""),row.get("claim",""))
        e=dict(row); e["geo_gate"]=r
        {"ACCEPT":accepted,"HOLD":held,"REJECT":rejected}[r["state"]].append(e)
    return {"enabled":True,"pack":pack,"accepted":accepted,"held":held,"rejected":rejected}
