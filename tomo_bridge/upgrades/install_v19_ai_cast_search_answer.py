#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil,py_compile,time

home=Path.home()
repo=home/"anderson-house-mailbox"
dd=home/"storage/downloads/three_amigos_dd"
bridge=dd/"tomo_bridge"

src=repo/"tomo_bridge/upgrades/v19_ai_cast_search_answer.py"
dst=bridge/"ai_cast_search_answer.py"

if not src.exists(): raise SystemExit("FAIL: V19 source missing")
if dst.exists():
    stamp=time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(dst,bridge/f"ai_cast_search_answer.pre_v19_{stamp}.py")

shutil.copy2(src,dst)
py_compile.compile(str(dst),doraise=True)

launcher=dd/"amigos_ai_search_answer.sh"
launcher.write_text("""#!/data/data/com.termux/files/usr/bin/bash
cd ~/storage/downloads/three_amigos_dd || exit 1
python tomo_bridge/ai_cast_search_answer.py "$@"
""")

print("==============================================")
print(" V19 AI CAST -> SEARCH -> AI ANSWER INSTALLED")
print("==============================================")
print("[GREEN] curl transport")
print("[GREEN] Cloudflare AI interprets the question")
print("[GREEN] Cloudflare AI generates search casts")
print("[GREEN] free web search harvests sources")
print("[GREEN] source text is fetched")
print("[GREEN] Cloudflare AI writes answer from evidence")
print("[GREEN] no Gemini billing")
print()
print('RUN: bash amigos_ai_search_answer.sh "your question"')
print("==============================================")
