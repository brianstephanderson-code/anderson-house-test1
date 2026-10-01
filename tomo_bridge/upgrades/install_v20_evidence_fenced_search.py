#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil,py_compile,time

home=Path.home()
repo=home/"anderson-house-mailbox"
dd=home/"storage/downloads/three_amigos_dd"
bridge=dd/"tomo_bridge"
src=repo/"tomo_bridge/upgrades/v20_evidence_fenced_search.py"
dst=bridge/"evidence_fenced_search.py"

if not src.exists(): raise SystemExit("FAIL: V20 source missing")
if dst.exists():
    stamp=time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(dst,bridge/f"evidence_fenced_search.pre_v20_{stamp}.py")

shutil.copy2(src,dst)
py_compile.compile(str(dst),doraise=True)

launcher=dd/"amigos_best_answer.sh"
launcher.write_text("""#!/data/data/com.termux/files/usr/bin/bash
cd ~/storage/downloads/three_amigos_dd || exit 1
python tomo_bridge/evidence_fenced_search.py "$@"
""")

print("================================================")
print(" V20 BEST-EFFORT EVIDENCE-FENCED SEARCH INSTALLED")
print("================================================")
print("[GREEN] AI understands question")
print("[GREEN] hard boundaries preserved in casts")
print("[GREEN] free web search")
print("[GREEN] readable source harvest")
print("[GREEN] AI relevance gate")
print("[GREEN] evidence-only answer draft")
print("[GREEN] second AI claim verification")
print("[GREEN] unsupported claims deleted")
print("[GREEN] no Gemini billing")
print("[GREEN] old machinery retained as fallback")
print()
print('RUN: bash amigos_best_answer.sh "your question"')
print("================================================")
