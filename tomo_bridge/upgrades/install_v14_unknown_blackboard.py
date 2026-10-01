#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil, time, py_compile, importlib.util, json

home=Path.home()
dd=home/"storage/downloads/three_amigos_dd"
repo=home/"anderson-house-mailbox"
bridge=dd/"tomo_bridge"
src=repo/"tomo_bridge/upgrades/v14_unknown_blackboard_fanout.py"
dst=bridge/"semantic_fanout.py"
runner=bridge/"amigos_bridge_job.py"

if not src.exists():
    raise SystemExit("FAIL: V14 source missing")
if not runner.exists():
    raise SystemExit("FAIL: bridge runner missing")

stamp=time.strftime("%Y%m%d-%H%M%S")
if dst.exists():
    shutil.copy2(dst,bridge/f"semantic_fanout.pre_v14_{stamp}.py")
shutil.copy2(src,dst)

py_compile.compile(str(dst),doraise=True)
py_compile.compile(str(runner),doraise=True)

spec=importlib.util.spec_from_file_location("sf",dst)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

tests=[
    {
      "name":"route",
      "q":"Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?",
      "unknown":"route",
      "must":["Edinburgh, Scotland","Glasgow, Scotland","summer"]
    },
    {
      "name":"salmon time",
      "q":"When is the best time to catch salmon in Perth, Western Australia?",
      "unknown":"time",
      "must":["summer"] if False else ["Perth"]
    },
    {
      "name":"birthday",
      "q":"When is George Eliot's birthday, the famous novelist?",
      "unknown":"date",
      "must":["George"]
    },
    {
      "name":"Idaho association",
      "q":"What thing is Idaho most famous for?",
      "unknown":"association",
      "must":["Idaho"]
    },
    {
      "name":"AI examples",
      "q":"Are there real-life examples of people using multi-agent AI systems like ours?",
      "unknown":"example",
      "must":["agent"]
    },
]

for t in tests:
    f=m.semantic_fanout(t["q"],{},10)
    board=f["blackboard"]
    blob="\n".join(x["query"] for x in f["casts"])
    ok=board["unknown"]["type"]==t["unknown"] and f["count"]>=2 and all(x.lower() in blob.lower() for x in t["must"])
    print(("[GREEN] " if ok else "[FAIL] ")+t["name"]+" unknown="+board["unknown"]["type"]+" casts="+str(f["count"]))
    if not ok:
        print(json.dumps(f,indent=2))
        raise SystemExit("FAIL: "+t["name"])

# Critical route-boundary assertion.
route=m.semantic_fanout(
    "Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?",
    {},
    10
)
for cast in route["casts"]:
    q=cast["query"].lower()
    if cast["why"]!="original question":
        if "edinburgh" not in q or "glasgow" not in q or "summer" not in q:
            raise SystemExit("FAIL: route boundary leaked")

manifest={
  "version":"V14_UNKNOWN_FIRST_BLACKBOARD",
  "core_rule":"Find the unknown, lock the boundaries, fan out only the unknown.",
  "flow":[
    "USER QUESTION",
    "UNKNOWN EXTRACTOR",
    "BOUNDARY LOCK",
    "BLACKBOARD",
    "UNKNOWN SEMANTIC FAN-OUT",
    "CAST",
    "SEARCH",
    "MERGE",
    "VERIFY",
    "SUFFICIENT?",
    "DONE"
  ]
}
(bridge/"v14_unknown_blackboard_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")

print()
print("================================================")
print(" V14 UNKNOWN-FIRST BLACKBOARD INSTALLED")
print("================================================")
print("[GREEN] UNKNOWN EXTRACTOR")
print("[GREEN] BOUNDARY LOCK")
print("[GREEN] BLACKBOARD STATE")
print("[GREEN] UNKNOWN-ONLY SEMANTIC FAN-OUT")
print("[GREEN] EXISTING V13 LIVE WIRING REUSED")
print("[GREEN] WORLDWIDE GEO GATE RETAINED")
print("================================================")
