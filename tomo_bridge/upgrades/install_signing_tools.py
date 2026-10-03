#!/usr/bin/env python3
import shutil, subprocess, sys, time

need=[]
if not shutil.which("keytool"):
    need.append("openjdk-17")
if not shutil.which("openssl"):
    need.append("openssl")

if not need:
    print("SIGNING_TOOLS_ALREADY_PRESENT")
    raise SystemExit(0)

# Wait for any other Termux apt/dpkg work to finish.
deadline=time.time()+300
while time.time()<deadline:
    r=subprocess.run(["sh","-lc","pgrep -x apt >/dev/null || pgrep -x apt-get >/dev/null || pgrep -x dpkg >/dev/null"],
                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if r.returncode!=0:
        break
    time.sleep(5)

cmd=["pkg","install","-y",*need]
for attempt in range(3):
    r=subprocess.run(cmd,text=True,capture_output=True,timeout=900)
    out=(r.stdout or "")+(r.stderr or "")
    if r.returncode==0:
        print("INSTALL_RETURN=0")
        print("KEYTOOL="+("YES" if shutil.which("keytool") else "NO"))
        print("OPENSSL="+("YES" if shutil.which("openssl") else "NO"))
        raise SystemExit(0)
    if "Could not get lock" not in out and "Unable to lock" not in out:
        print("INSTALL_RETURN="+str(r.returncode))
        print(out[-5000:])
        raise SystemExit(r.returncode)
    time.sleep(15)

print("INSTALL_RETURN="+str(r.returncode))
print(out[-5000:])
raise SystemExit(r.returncode)
