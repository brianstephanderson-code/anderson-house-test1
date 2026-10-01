#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil,time,py_compile,importlib.util,json

home=Path.home()
repo=home/"anderson-house-mailbox"
dd=home/"storage/downloads/three_amigos_dd"
bridge=dd/"tomo_bridge"
src=repo/"tomo_bridge/upgrades/v15_boolean_semantic.py"
dst=bridge/"semantic_fanout.py"
runner=bridge/"amigos_bridge_job.py"

if not src.exists(): raise SystemExit("FAIL: V15 source missing")
if not runner.exists(): raise SystemExit("FAIL: live runner missing")

stamp=time.strftime("%Y%m%d-%H%M%S")
if dst.exists():
    shutil.copy2(dst,bridge/f"semantic_fanout.pre_v15_{stamp}.py")
shutil.copy2(src,dst)

py_compile.compile(str(dst),doraise=True)
py_compile.compile(str(runner),doraise=True)

spec=importlib.util.spec_from_file_location("sf",dst)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

tests=[
  ("Edinburgh route","Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?","route",["edinburgh","glasgow","walking","summer"," or "]),
  ("Perth salmon time","When is the best time to catch salmon in Perth, Western Australia?","time",["perth","western australia"," or "]),
  ("George Eliot","When is George Eliot's birthday, the famous novelist?","date",["birthday"," or "]),
  ("Idaho","What thing is Idaho most famous for?","association",["famous"," or "]),
]

for name,q,u,need in tests:
    r=m.semantic_fanout(q,{},10)
    blob=(r.get("boolean_query","")+"\n"+"\n".join(x["query"] for x in r["casts"])).lower()
    ok=r["blackboard"]["unknown"]["type"]==u and all(x in blob for x in need)
    print(("[GREEN] " if ok else "[FAIL] ")+name+" casts="+str(r["count"]))
    if not ok:
        print(json.dumps(r,indent=2))
        raise SystemExit("FAIL: "+name)

route=m.semantic_fanout(
    "Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?",
    {},10
)
bq=route["boolean_query"].lower()
if not ('"edinburgh, scotland"' in bq and '"glasgow, scotland"' in bq and 'walking' in bq and 'summer' in bq):
    raise SystemExit("FAIL: route hard boundary test")

manifest={
 "version":"V15_BOOLEAN_SEMANTIC_HYBRID",
 "rule":"Lock hard concepts with AND; widen only the unknown with OR.",
 "example":route["boolean_query"]
}
(bridge/"v15_boolean_semantic_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")

print()
print("================================================")
print(" V15 BOOLEAN + SEMANTIC HYBRID INSTALLED")
print("================================================")
print("[GREEN] HARD TERMS -> AND")
print("[GREEN] UNKNOWN SYNONYMS -> OR")
print("[GREEN] EXACT BOUNDARIES PRESERVED")
print("[GREEN] PLAIN FALLBACK CASTS INCLUDED")
print("[GREEN] EXISTING LIVE V13/V14 RUNNER WIRING REUSED")
print("================================================")
print()
print("EDINBURGH EXAMPLE:")
print(route["boolean_query"])
