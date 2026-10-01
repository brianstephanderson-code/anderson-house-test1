#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil, py_compile, importlib.util, json, time

home=Path.home()
dd=home/"storage/downloads/three_amigos_dd"
repo=home/"anderson-house-mailbox"
bridge=dd/"tomo_bridge"
runner=bridge/"amigos_bridge_job.py"
module_src=repo/"tomo_bridge/upgrades/v11_universal_geo.py"
module_dst=bridge/"universal_geo.py"

if not runner.exists(): raise SystemExit("FAIL: bridge runner missing")
if not module_src.exists(): raise SystemExit("FAIL: V11 module missing from repo")

stamp=time.strftime("%Y%m%d-%H%M%S")
shutil.copy2(runner, bridge/f"amigos_bridge_job.pre_v11_{stamp}.py")
shutil.copy2(module_src,module_dst)

text=runner.read_text(encoding="utf-8")
imp="from universal_geo import apply_geo_gate\n"
if imp not in text:
    # insert after ordinary imports
    pos=0
    lines=text.splitlines(True)
    for i,line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            pos=i+1
    lines.insert(pos,imp)
    text="".join(lines)

old1='''    all_evidence = dedupe_evidence(
        all_evidence
    )

    board = run_dd(
        all_evidence,
        geo,
        jobdir,
        "pass1"
    )
'''
new1='''    all_evidence = dedupe_evidence(
        all_evidence
    )

    geo_gate = apply_geo_gate(
        question,
        geo,
        all_evidence
    )

    evidence_for_dd = (
        geo_gate["accepted"]
        if geo_gate["enabled"]
        else all_evidence
    )

    dump(
        jobdir / "geo_gate_pass1.json",
        geo_gate
    )

    board = run_dd(
        evidence_for_dd,
        geo if geo_gate["enabled"] else "",
        jobdir,
        "pass1"
    )
'''
if old1 in text:
    text=text.replace(old1,new1,1)
elif 'geo_gate = apply_geo_gate(' not in text:
    raise SystemExit("FAIL: pass1 patch target not found")

old2='''            all_evidence = dedupe_evidence(
                all_evidence
            )

            board = run_dd(
                all_evidence,
                geo,
                jobdir,
                f"pass{index}"
            )
'''
new2='''            all_evidence = dedupe_evidence(
                all_evidence
            )

            geo_gate = apply_geo_gate(
                question,
                geo,
                all_evidence
            )

            evidence_for_dd = (
                geo_gate["accepted"]
                if geo_gate["enabled"]
                else all_evidence
            )

            dump(
                jobdir / f"geo_gate_pass{index}.json",
                geo_gate
            )

            board = run_dd(
                evidence_for_dd,
                geo if geo_gate["enabled"] else "",
                jobdir,
                f"pass{index}"
            )
'''
if old2 in text:
    text=text.replace(old2,new2,1)

needle='''        "geography":
            geo,
'''
replacement='''        "geography":
            geo,

        "geography_gate": {
            "enabled": geo_gate.get("enabled", False),
            "pack": geo_gate.get("pack", {}),
            "accepted": len(geo_gate.get("accepted", [])),
            "held": len(geo_gate.get("held", [])),
            "rejected": len(geo_gate.get("rejected", [])),
        },
'''
if needle in text and '"geography_gate": {' not in text:
    text=text.replace(needle,replacement,1)

runner.write_text(text,encoding="utf-8")
py_compile.compile(str(module_dst),doraise=True)
py_compile.compile(str(runner),doraise=True)

spec=importlib.util.spec_from_file_location("ug",module_dst)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
tests=[
 ("WA gov AU", m.classify_source(m.build_geo_pack("salmon in Western Australia","WA"),"https://www.wa.gov.au/x","Western Australia salmon")["state"]=="ACCEPT"),
 ("Washington reject", m.classify_source(m.build_geo_pack("salmon in Western Australia","WA"),"https://wdfw.wa.gov/fishing","Washington State salmon")["state"]=="REJECT"),
 ("Athens Greece", m.build_geo_pack("I want to stay in Athens, Greece for a week","")["country_code"]=="gr"),
 ("Greece ccTLD", m.classify_source(m.build_geo_pack("I want to stay in Athens, Greece for a week",""),"https://example.gr/hotel","Athens hotel")["state"]=="ACCEPT"),
 ("Global off", m.build_geo_pack("Has anybody on the internet solved this?","")["enabled"] is False),
]
for name,ok in tests:
    print(("[GREEN] " if ok else "[FAIL] ")+name)
if not all(ok for _,ok in tests):
    raise SystemExit("FAIL: V11 tests")

manifest={
 "version":"V11_UNIVERSAL_GEO",
 "rules":[
  "Location gate activates only when the question contains a place requirement.",
  "Country ccTLDs are used as supporting geography evidence.",
  "Explicit target place text is strong evidence.",
  "Generic/global internet questions keep geography gate off.",
  "Ambiguous or unproven geography is HOLD.",
  "Explicit conflicting country evidence is REJECT.",
  "Western Australia vs Washington State false-friend is explicitly blocked."
 ]
}
(bridge/"v11_geo_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("[GREEN] V11 UNIVERSAL GEO INSTALLED")
