#!/data/data/com.termux/files/usr/bin/python
# Activates V12 after baseline has been recorded.
from pathlib import Path
import shutil, time, py_compile

home=Path.home()
dd=home/"storage/downloads/three_amigos_dd"
bridge=dd/"tomo_bridge"
runner=bridge/"amigos_bridge_job.py"
module=bridge/"semantic_fanout.py"

if not runner.exists() or not module.exists():
    raise SystemExit("FAIL: stage V12 first")

stamp=time.strftime("%Y%m%d-%H%M%S")
shutil.copy2(runner, bridge/f"amigos_bridge_job.pre_v12_activate_{stamp}.py")
text=runner.read_text(encoding="utf-8")
imp="from semantic_fanout import semantic_fanout\n"
if imp not in text:
    lines=text.splitlines(True); pos=0
    for i,line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "): pos=i+1
    lines.insert(pos,imp); text="".join(lines)

# Replace first search pass only. Existing recast/verification logic remains.
old='''    result = run_search(
        question,
        jobdir,
        "pass1"
    )

    search_history.append(
        {
            "query":
                question,
'''
new='''    try:
        gp = build_geo_pack(question, geo) if "build_geo_pack" in globals() else {}
    except Exception:
        gp = {}

    fanout = semantic_fanout(
        question,
        gp,
        10
    )

    dump(
        jobdir / "semantic_fanout.json",
        fanout
    )

    result = None
    fanout_evidence = []

    for cast_index, cast in enumerate(
        fanout.get("casts", []),
        start=1
    ):
        cast_query = cast["query"]

        cast_result = run_search(
            cast_query,
            jobdir,
            f"fanout_{cast_index}"
        )

        search_history.append(
            {
                "query": cast_query,
                "fanout_reason": cast.get("why"),
                "seconds": cast_result.get("seconds", 0),
                "evidence": len(cast_result.get("evidence", [])),
                "returncode": cast_result.get("returncode", 0),
            }
        )

        fanout_evidence.extend(
            cast_result.get("evidence", [])
        )

        if result is None:
            result = cast_result

    if result is None:
        result = {
            "evidence": [],
            "seconds": 0,
            "returncode": 0,
        }

    result["evidence"] = fanout_evidence

    search_history.append(
        {
            "query":
                question,
'''
if old not in text:
    raise SystemExit("FAIL: could not locate V12 activation patch target")

text=text.replace(old,new,1)
runner.write_text(text,encoding="utf-8")
py_compile.compile(str(runner),doraise=True)
print("[GREEN] V12 SEMANTIC FAN-OUT ACTIVATED")
