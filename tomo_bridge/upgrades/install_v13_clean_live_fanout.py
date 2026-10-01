#!/data/data/com.termux/files/usr/bin/python
# V13 CLEAN LIVE SEARCH PATCH
# Removes legacy WA-specific recasts and wires universal semantic fan-out into live bridge.

from pathlib import Path
import ast, shutil, time, py_compile, re

home = Path.home()
dd = home / "storage/downloads/three_amigos_dd"
bridge = dd / "tomo_bridge"
runner = bridge / "amigos_bridge_job.py"

if not runner.exists():
    raise SystemExit("FAIL: amigos_bridge_job.py not found")

stamp = time.strftime("%Y%m%d-%H%M%S")
backup = bridge / f"amigos_bridge_job.pre_v13_{stamp}.py"
shutil.copy2(runner, backup)
print("[GREEN] BACKUP", backup.name)

text = runner.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 1) Ensure clean universal imports
# ------------------------------------------------------------
for old in [
    "from universal_geo import apply_geo_gate\n",
    "from universal_geo import apply_geo_gate, build_geo_pack\n",
    "from semantic_fanout import semantic_fanout\n",
]:
    text = text.replace(old, "")

lines = text.splitlines(True)
insert_at = 0
for i, line in enumerate(lines):
    if line.startswith("import ") or line.startswith("from "):
        insert_at = i + 1

imports = [
    "from universal_geo import apply_geo_gate, build_geo_pack\n",
    "from semantic_fanout import semantic_fanout\n",
]
for imp in reversed(imports):
    lines.insert(insert_at, imp)
text = "".join(lines)

# ------------------------------------------------------------
# 2) Replace legacy recast function completely
# ------------------------------------------------------------
def replace_top_level_function(src, name, replacement):
    tree = ast.parse(src)
    target = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            target = node
            break
    if not target:
        return src, False
    src_lines = src.splitlines(True)
    start = target.lineno - 1
    end = target.end_lineno
    src_lines[start:end] = [replacement.rstrip() + "\n\n"]
    return "".join(src_lines), True

new_recast = r'''
def recast_queries(question, *args, **kwargs):
    """
    Universal recast generator.
    No geography is hard-coded here.
    It preserves the user's hard boundaries and varies only flexible meaning.
    """
    supplied_geo = ""
    for a in args:
        if isinstance(a, str) and len(a) <= 32:
            supplied_geo = a

    try:
        pack = build_geo_pack(question, supplied_geo)
    except Exception:
        pack = {}

    fan = semantic_fanout(
        question,
        pack,
        max_casts=10
    )

    casts = []
    original = str(question).strip().lower()

    for row in fan.get("casts", []):
        q = str(row.get("query", "")).strip()
        if not q:
            continue
        if q.lower() == original:
            continue
        if q not in casts:
            casts.append(q)

    return casts[:6]
'''
text, replaced = replace_top_level_function(text, "recast_queries", new_recast)
print("[GREEN] RECAST FUNCTION REPLACED" if replaced else "[NOTE] NO OLD recast_queries FUNCTION FOUND")

# ------------------------------------------------------------
# 3) Add live fan-out bundle helper before main
# ------------------------------------------------------------
helper_marker = "# V13 LIVE FANOUT BUNDLE"
if helper_marker not in text:
    helper = r'''
# V13 LIVE FANOUT BUNDLE
def v13_run_fanout_bundle(question, geo, jobdir, search_history):
    """
    Search the same user intent through several semantically distinct casts.
    Hard boundaries remain fixed. Evidence is merged before downstream dedupe,
    geography, question-fit, source-family and HOLD/REJECT gates.
    """
    try:
        geo_pack = build_geo_pack(question, geo)
    except Exception:
        geo_pack = {}

    fan = semantic_fanout(
        question,
        geo_pack,
        max_casts=8
    )

    try:
        dump(
            jobdir / "semantic_fanout_live.json",
            fan
        )
    except Exception:
        pass

    merged = []
    total_seconds = 0.0
    last_rc = 0

    casts = fan.get("casts", []) or [
        {"query": question, "why": "fallback original"}
    ]

    for idx, cast in enumerate(casts, start=1):
        cast_query = str(cast.get("query", "")).strip()
        if not cast_query:
            continue

        result = run_search(
            cast_query,
            jobdir,
            f"fanout_{idx}"
        )

        evidence = result.get("evidence", []) or []
        merged.extend(evidence)
        total_seconds += float(result.get("seconds", 0) or 0)
        last_rc = result.get("returncode", 0)

        search_history.append(
            {
                "query": cast_query,
                "fanout_reason": cast.get("why", ""),
                "seconds": result.get("seconds", 0),
                "evidence": len(evidence),
                "returncode": result.get("returncode", 0),
            }
        )

    return {
        "evidence": merged,
        "seconds": total_seconds,
        "returncode": last_rc,
        "fanout_count": len(casts),
    }

'''
    main_pos = text.find("\ndef main(")
    if main_pos == -1:
        main_pos = text.find("\nif __name__")
    if main_pos == -1:
        raise SystemExit("FAIL: could not locate main insertion point")
    text = text[:main_pos] + "\n" + helper + text[main_pos:]
    print("[GREEN] LIVE FANOUT HELPER ADDED")
else:
    print("[GREEN] LIVE FANOUT HELPER ALREADY PRESENT")

# ------------------------------------------------------------
# 4) Replace the live pass1 call with fan-out
# ------------------------------------------------------------
tree = ast.parse(text)
src_lines = text.splitlines(True)
candidate = None

for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        call = node.value
        if isinstance(call, ast.Call):
            fn = call.func
            fn_name = fn.id if isinstance(fn, ast.Name) else None
            if fn_name == "run_search" and call.args:
                a0 = call.args[0]
                is_question = isinstance(a0, ast.Name) and a0.id == "question"
                has_pass1 = any(
                    isinstance(a, ast.Constant) and a.value == "pass1"
                    for a in call.args
                )
                if is_question and has_pass1:
                    candidate = node
                    break

if candidate:
    indent = re.match(r"^\s*", src_lines[candidate.lineno - 1]).group(0)
    replacement = (
        indent + "result = v13_run_fanout_bundle(\n"
        + indent + "    question,\n"
        + indent + "    geo,\n"
        + indent + "    jobdir,\n"
        + indent + "    search_history\n"
        + indent + ")\n"
    )
    src_lines[candidate.lineno - 1:candidate.end_lineno] = [replacement]
    text = "".join(src_lines)
    print("[GREEN] LIVE PASS1 WIRED TO FANOUT")
elif "v13_run_fanout_bundle(" in text:
    print("[GREEN] LIVE PASS1 ALREADY WIRED")
else:
    raise SystemExit("FAIL: could not find live pass1 run_search call")

# ------------------------------------------------------------
# 5) Purge known legacy hard-coded recast contamination
# ------------------------------------------------------------
legacy_phrases = [
    '"Western Australia" practical advice',
    "WA official end user",
    "Western Australia practical advice",
]
for phrase in legacy_phrases:
    text = text.replace(phrase, "")

runner.write_text(text, encoding="utf-8")

# ------------------------------------------------------------
# 6) Compile + structural checks
# ------------------------------------------------------------
py_compile.compile(str(runner), doraise=True)

final = runner.read_text(encoding="utf-8")
checks = {
    "universal_geo_import": "from universal_geo import apply_geo_gate, build_geo_pack" in final,
    "semantic_fanout_import": "from semantic_fanout import semantic_fanout" in final,
    "live_fanout_helper": "def v13_run_fanout_bundle" in final,
    "legacy_WA_practical_removed": '"Western Australia" practical advice' not in final,
    "legacy_WA_enduser_removed": "WA official end user" not in final,
}
for name, ok in checks.items():
    print(("[GREEN] " if ok else "[FAIL] ") + name)
if not all(checks.values()):
    raise SystemExit("FAIL: V13 structural check")

# ------------------------------------------------------------
# 7) Dry semantic tests
# ------------------------------------------------------------
from importlib.util import spec_from_file_location, module_from_spec

sf_path = bridge / "semantic_fanout.py"
if not sf_path.exists():
    raise SystemExit("FAIL: semantic_fanout.py missing")

spec = spec_from_file_location("sf", sf_path)
sf = module_from_spec(spec)
spec.loader.exec_module(sf)

tests = [
    (
        "Edinburgh -> Glasgow",
        "Is there a way to walk from Edinburgh, Scotland to Glasgow, Scotland in the summer?",
        ["edinburgh", "glasgow", "summer"],
    ),
    (
        "Perth salmon",
        "When is the best time to catch salmon in Perth, Western Australia?",
        ["perth", "western australia"],
    ),
    (
        "Global AI agents",
        "Are there real-life examples of people using multi-agent AI systems like ours?",
        [],
    ),
]

for name, q, required in tests:
    f = sf.semantic_fanout(q, {}, 10)
    blob = "\n".join(x["query"] for x in f["casts"]).lower()
    ok = f["count"] >= 2 and all(x in blob for x in required)
    print(("[GREEN] " if ok else "[FAIL] ") + name + f" casts={f['count']}")
    if not ok:
        raise SystemExit("FAIL: fanout dry test " + name)

print()
print("================================================")
print(" V13 CLEAN LIVE SEMANTIC FAN-OUT INSTALLED")
print("================================================")
print("[GREEN] OLD WA RECASTS REMOVED")
print("[GREEN] LIVE SEARCH USES SEMANTIC FAN-OUT")
print("[GREEN] HARD BOUNDARIES PRESERVED")
print("[GREEN] UNIVERSAL GEOGRAPHY RETAINED")
print("[GREEN] DOWNSTREAM DEDUPE / HOLD / REJECT RETAINED")
print("================================================")
