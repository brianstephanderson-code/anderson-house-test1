#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil, py_compile, time, importlib.util

home=Path.home()
dd=home/"storage/downloads/three_amigos_dd"
repo=home/"anderson-house-mailbox"
bridge=dd/"tomo_bridge"
runner=bridge/"amigos_bridge_job.py"
src=repo/"tomo_bridge/upgrades/v12_semantic_fanout.py"
dst=bridge/"semantic_fanout.py"

if not runner.exists(): raise SystemExit("FAIL: bridge runner missing")
if not src.exists(): raise SystemExit("FAIL: V12 semantic fan-out module missing")

stamp=time.strftime("%Y%m%d-%H%M%S")
shutil.copy2(runner, bridge/f"amigos_bridge_job.pre_v12_{stamp}.py")
shutil.copy2(src,dst)
py_compile.compile(str(dst),doraise=True)

spec=importlib.util.spec_from_file_location("sf",dst)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

# Dry tests: constraints must survive and fan-out must widen.
cases=[
("Edinburgh Glasgow","Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?",["Edinburgh","Glasgow","summer"]),
("Perth salmon","When is the best time to catch salmon in Perth, Western Australia?",["Perth","Western Australia"]),
("Global agents","Are there real-life examples of people using multi-agent AI systems like ours?",[]),
]
for name,q,need in cases:
    r=m.semantic_fanout(q,{},12)
    blob="\n".join(x["query"] for x in r["casts"]).lower()
    ok=r["count"]>=2 and all(x.lower() in blob for x in need)
    print(("[GREEN] " if ok else "[FAIL] ")+name+" fan-out="+str(r["count"]))
    if not ok: raise SystemExit("FAIL: "+name)

print("[GREEN] V12 MODULE STAGED")
print("[NOTE] Runner integration intentionally NOT activated yet.")
print("[NOTE] Keep baseline experiment clean; activate after baseline result is recorded.")
