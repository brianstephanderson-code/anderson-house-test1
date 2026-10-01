#!/data/data/com.termux/files/usr/bin/python
from pathlib import Path
import shutil,py_compile,time

home=Path.home()
repo=home/"anderson-house-mailbox"
dd=home/"storage/downloads/three_amigos_dd"
bridge=dd/"tomo_bridge"
src=repo/"tomo_bridge/upgrades/v18_cloudflare_answer.py"
dst=bridge/"cloudflare_answer.py"

if not src.exists(): raise SystemExit("FAIL: V18 source missing")
if dst.exists():
    stamp=time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(dst,bridge/f"cloudflare_answer.pre_v18_{stamp}.py")
shutil.copy2(src,dst)
py_compile.compile(str(dst),doraise=True)

launcher=dd/"amigos_answer_cf.sh"
launcher.write_text("""#!/data/data/com.termux/files/usr/bin/bash
cd ~/storage/downloads/three_amigos_dd || exit 1
python tomo_bridge/cloudflare_answer.py "$@"
""")

print("==============================================")
print(" V18 FREE SEARCH -> CLOUDFLARE AI INSTALLED")
print("==============================================")
print("[GREEN] no Gemini billing")
print("[GREEN] Amigos free search retained")
print("[GREEN] Cloudflare Workers AI answer brain")
print('RUN: bash amigos_answer_cf.sh "your question"')
print("==============================================")
