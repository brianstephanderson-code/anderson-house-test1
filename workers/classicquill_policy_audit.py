#!/usr/bin/env python3
import base64, json, re, subprocess, hashlib, sys
from collections import Counter, defaultdict

REPO="brianstephanderson-code/anderson-house-test1"
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def clean(value):
    return "" if value is None else str(value).strip()

def gh_json(*args):
    p=subprocess.run(["gh",*args],text=True,capture_output=True,check=True)
    return json.loads(p.stdout)

tree=gh_json("api",f"repos/{REPO}/git/trees/main?recursive=1")["tree"]
policy_paths=[x for x in tree if x.get("type")=="blob" and x["path"].startswith("hive/") and x["path"].endswith(".md")]

docs={}
for item in policy_paths:
    blob=gh_json("api",f"repos/{REPO}/git/blobs/{item['sha']}")
    text=base64.b64decode(blob["content"]).decode("utf-8","replace")
    docs[item["path"]]=text

rule_re=re.compile(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL)\b",re.I)
todo_re=re.compile(r"\b(TODO|UNKNOWN|TBD|FIXME|\?\?\?)\b",re.I)
heading_re=re.compile(r"^#{1,6}\s+(.+)$",re.M)

rules=[]
todos=[]
headings=defaultdict(list)
for path,text in docs.items():
    for n,line in enumerate(text.splitlines(),1):
        s=clean(line)
        if rule_re.search(s):
            rules.append((path,n,s))
        if todo_re.search(s):
            todos.append((path,n,s))
    for h in heading_re.findall(text):
        headings[clean(h).lower()].append(path)

dupes={h:paths for h,paths in headings.items() if len(set(paths))>1}

# light contradiction candidates: same normalized subject line appearing with both positive and negative force words
norm_groups=defaultdict(list)
for path,n,s in rules:
    norm=re.sub(r"\b(MUST|NEVER|ONLY|REQUIRED|ALWAYS|DO NOT|SHALL|NOT)\b","",s,flags=re.I)
    norm=clean(re.sub(r"[^a-z0-9]+"," ",norm.lower()))
    if norm:
        norm_groups[norm].append((path,n,s))
conflicts=[]
for norm,items in norm_groups.items():
    joined=" ".join(x[2].lower() for x in items)
    if len(items)>1 and ("never" in joined or "do not" in joined or " not " in f" {joined} ") and ("must" in joined or "always" in joined or "required" in joined or "shall" in joined):
        conflicts.append(items)

job_files=[x["path"] for x in tree if x.get("type")=="blob" and x["path"].startswith("jobs/") and x["path"].endswith(".job")]
result_files=[x["path"] for x in tree if x.get("type")=="blob" and x["path"].startswith("results/") and x["path"].endswith(".result")]
job_ids={p.split("/")[-1][:-4] for p in job_files}
result_ids={p.split("/")[-1][:-7] for p in result_files}
orphan_jobs=sorted(job_ids-result_ids)
orphan_results=sorted(result_ids-job_ids)

out=[]
out.append("# CLASSICQUILL Anderson House Policy Audit")
out.append("")
out.append(f"Policy files scanned: {len(docs)}")
out.append(f"Hard-rule lines found: {len(rules)}")
out.append(f"TODO/UNKNOWN markers found: {len(todos)}")
out.append(f"Repeated headings across files: {len(dupes)}")
out.append(f"Potential rule conflicts: {len(conflicts)}")
out.append(f"Jobs without results: {len(orphan_jobs)}")
out.append(f"Results without jobs: {len(orphan_results)}")
out.append("")

out.append("## Policy files")
for p in sorted(docs): out.append(f"- {p}")
out.append("")

out.append("## Hard rules")
for path,n,s in rules[:250]:
    out.append(f"- {path}:{n} — {s[:220]}")
if len(rules)>250: out.append(f"- ... {len(rules)-250} more omitted")
out.append("")

out.append("## TODO / UNKNOWN gaps")
if todos:
    for path,n,s in todos[:150]: out.append(f"- {path}:{n} — {s[:220]}")
else:
    out.append("- None found")
out.append("")

out.append("## Repeated headings")
if dupes:
    for h,paths in sorted(dupes.items()):
        out.append(f"- {h}: {', '.join(sorted(set(paths)))}")
else:
    out.append("- None found")
out.append("")

out.append("## Potential rule conflicts")
if conflicts:
    for group in conflicts[:50]:
        out.append("- Candidate:")
        for path,n,s in group: out.append(f"  - {path}:{n} — {s[:220]}")
else:
    out.append("- None detected by conservative text heuristic")
out.append("")

out.append("## Mailbox gaps")
out.append("Jobs without results:")
if orphan_jobs:
    for x in orphan_jobs[:100]: out.append(f"- {x}")
else:
    out.append("- None")
out.append("")
out.append("Results without jobs:")
if orphan_results:
    for x in orphan_results[:100]: out.append(f"- {x}")
else:
    out.append("- None")

report="\n".join(out)
print(report)
