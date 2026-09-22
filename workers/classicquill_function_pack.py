#!/usr/bin/env python3
import base64, json, re, subprocess, sys
from collections import defaultdict

REPO="brianstephanderson-code/anderson-house-test1"

def gh_json(*args):
    p=subprocess.run(["gh",*args],text=True,capture_output=True,check=True)
    return json.loads(p.stdout)

def load_docs():
    tree=gh_json("api",f"repos/{REPO}/git/trees/main?recursive=1")["tree"]
    policy=[x for x in tree if x.get("type")=="blob" and x["path"].startswith("hive/") and x["path"].endswith(".md")]
    docs={}
    for item in policy:
        blob=gh_json("api",f"repos/{REPO}/git/blobs/{item['sha']}")
        docs[item["path"]]=base64.b64decode(blob["content"]).decode("utf-8","replace")
    return tree,docs

def hard_rules(docs):
    rr=re.compile(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL)\b",re.I)
    out=[]
    for path,text in docs.items():
        for n,line in enumerate(text.splitlines(),1):
            if rr.search(line): out.append((path,n,line.strip()))
    return out

def headings(docs):
    hr=re.compile(r"^#{1,6}\s+(.+)$",re.M)
    out=[]
    for path,text in docs.items():
        for h in hr.findall(text): out.append((path,h.strip()))
    return out

def unknowns(docs):
    ur=re.compile(r"\bUNKNOWN\b",re.I)
    out=[]
    for path,text in docs.items():
        for n,line in enumerate(text.splitlines(),1):
            if ur.search(line): out.append((path,n,line.strip()))
    return out

def mailbox_gaps(tree):
    jobs={x["path"].split("/")[-1][:-4] for x in tree if x.get("type")=="blob" and x["path"].startswith("jobs/") and x["path"].endswith(".job")}
    results={x["path"].split("/")[-1][:-7] for x in tree if x.get("type")=="blob" and x["path"].startswith("results/") and x["path"].endswith(".result")}
    return sorted(jobs-results), sorted(results-jobs)

def main():
    tree,docs=load_docs()
    rules=hard_rules(docs)
    heads=headings(docs)
    unk=unknowns(docs)
    oj,or_=mailbox_gaps(tree)
    print("# CLASSICQUILL FUNCTION PACK")
    print(f"HARD_RULES={len(rules)}")
    print(f"HEADINGS={len(heads)}")
    print(f"UNKNOWN_STATES={len(unk)}")
    print(f"JOBS_WITHOUT_RESULTS={len(oj)}")
    print(f"RESULTS_WITHOUT_JOBS={len(or_)}")
    print("\n## HARD RULE EXTRACTOR")
    for p,n,s in rules[:200]: print(f"- {p}:{n} — {s[:220]}")
    print("\n## HEADING REGISTRY")
    for p,h in heads[:200]: print(f"- {p} — {h[:180]}")
    print("\n## UNKNOWN STATE INDEX")
    for p,n,s in unk[:120]: print(f"- {p}:{n} — {s[:220]}")
    print("\n## MAILBOX GAP CHECKER")
    print("Jobs without results:")
    for x in oj[:100]: print(f"- {x}")
    if not oj: print("- None")
    print("Results without jobs:")
    for x in or_[:100]: print(f"- {x}")
    if not or_: print("- None")

if __name__=="__main__":
    main()
