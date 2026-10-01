#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil, py_compile, time

home=Path.home()
repo=home/"anderson-house-mailbox"
dd=home/"storage/downloads/three_amigos_dd"
bridge=dd/"tomo_bridge"

src=repo/"tomo_bridge/upgrades/v17_free_search_ai_answer.py"
dst=bridge/"free_search_ai_answer.py"

if not src.exists(): raise SystemExit("FAIL: V17 source missing")
if not bridge.exists(): raise SystemExit("FAIL: bridge folder missing")

if dst.exists():
    stamp=time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(dst,bridge/f"free_search_ai_answer.pre_v17_{stamp}.py")

shutil.copy2(src,dst)
py_compile.compile(str(dst),doraise=True)

launcher=dd/"amigos_answer.sh"
launcher.write_text("""#!/data/data/com.termux/files/usr/bin/bash
cd ~/storage/downloads/three_amigos_dd || exit 1
python tomo_bridge/free_search_ai_answer.py "$@"
""")

print("==============================================")
print(" V17 FREE SEARCH -> AI ANSWER INSTALLED")
print("==============================================")
print("[GREEN] Existing Amigos free search does the web work")
print("[GREEN] Gemini 3.5 Flash-Lite is the answer brain")
print("[GREEN] No Gemini Google-Search grounding tool used")
print("[GREEN] Sources handed to Gemini explicitly")
print("[GREEN] Old search remains available as fallback")
print()
print("RUN WITH:")
print('bash amigos_answer.sh "your question"')
print("==============================================")
