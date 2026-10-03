#!/usr/bin/env python3
from pathlib import Path
import os, secrets, shutil, subprocess, sys

home=Path.home()
private=home/".tomo_private_signing"
keystore=private/"amigos-release.jks"
envfile=private/"signing.env"
alias="amigos"

private.mkdir(parents=True,exist_ok=True)
os.chmod(private,0o700)

keytool=shutil.which("keytool")
if not keytool:
    print("KEYSTORE_CREATE=NO_KEYTOOL")
    raise SystemExit(2)

if keystore.exists() and envfile.exists():
    print("KEYSTORE_CREATE=ALREADY_PRESENT")
    print("KEYSTORE_PATH="+str(keystore))
    raise SystemExit(0)

storepass=secrets.token_urlsafe(32)
keypass=secrets.token_urlsafe(32)

cmd=[
    keytool,"-genkeypair",
    "-keystore",str(keystore),
    "-storepass",storepass,
    "-keypass",keypass,
    "-alias",alias,
    "-keyalg","RSA",
    "-keysize","3072",
    "-validity","10000",
    "-dname","CN=Three Amigos Device Agent, O=Anderson House",
]
r=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
if r.returncode!=0:
    print("KEYSTORE_CREATE=FAILED")
    print((r.stderr or r.stdout or "")[-2000:])
    raise SystemExit(r.returncode)

envfile.write_text(
    "AMIGOS_KEYSTORE_PASSWORD="+storepass+"\n"+
    "AMIGOS_KEY_ALIAS="+alias+"\n"+
    "AMIGOS_KEY_PASSWORD="+keypass+"\n",
    encoding="utf-8"
)
os.chmod(keystore,0o600)
os.chmod(envfile,0o600)

fp=subprocess.run(
    [keytool,"-list","-v","-keystore",str(keystore),"-storepass",storepass,"-alias",alias],
    text=True,capture_output=True,timeout=30
)
sha256=""
for line in fp.stdout.splitlines():
    if "SHA256:" in line:
        sha256=line.strip()
        break

print("KEYSTORE_CREATE=GREEN")
print("KEYSTORE_PATH="+str(keystore))
print("SECRETS_PATH="+str(envfile))
print(sha256 or "SHA256=AVAILABLE_LOCALLY")
