#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil, py_compile, time

home = Path.home()
repo = home / "anderson-house-mailbox"
dd = home / "storage/downloads/three_amigos_dd"
bridge = dd / "tomo_bridge"

src = repo / "tomo_bridge/upgrades/v16_ai_search_first.py"
dst = bridge / "ai_search_first.py"

if not src.exists():
    raise SystemExit("FAIL: V16 source missing")
if not bridge.exists():
    raise SystemExit("FAIL: bridge folder missing")

if dst.exists():
    stamp = time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(dst, bridge / f"ai_search_first.pre_v16_{stamp}.py")

shutil.copy2(src, dst)
py_compile.compile(str(dst), doraise=True)

launcher = dd / "amigos_ai_answer.sh"
launcher.write_text("""#!/data/data/com.termux/files/usr/bin/bash
cd ~/storage/downloads/three_amigos_dd || exit 1
python tomo_bridge/ai_search_first.py "$@"
""")
launcher.chmod(0o755)

print("==============================================")
print(" V16 AI SEARCH BRAIN INSTALLED")
print("==============================================")
print("[GREEN] Gemini 2.5 Flash")
print("[GREEN] Google Search grounding")
print("[GREEN] answer + search queries + sources")
print("[GREEN] local free-safety cap = 400/day")
print("[GREEN] old Amigos search remains untouched")
print()
print("NEXT GATE:")
print("Set GEMINI_API_KEY, then run one live test.")
print("==============================================")
