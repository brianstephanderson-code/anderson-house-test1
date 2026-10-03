#!/usr/bin/env python3
from pathlib import Path
import os, secrets, shutil, subprocess, sys

home=Path.home()
private=home/".tomo_signing"
private.mkdir(parents=True,exist_ok=True)
os.chmod(private,0o700)

keystore=private/"amigos-signing.p12"
password_file=private/"password.txt"
alias_file=private/"alias.txt"
alias="amigos-device-agent"

if keystore.exists() and password_file.exists() and alias_file.exists():
    print("SIGNING_KEY_ALREADY_EXISTS")
    print("PRIVATE_DIR="+str(private))
    raise SystemExit(0)

keytool=shutil.which("keytool")
if not keytool:
    print("SIGNING_KEY_TOOL_MISSING")
    raise SystemExit(2)

password=secrets.token_urlsafe(32)
cmd=[
    keytool,
    "-genkeypair",
    "-storetype","PKCS12",
    "-keystore",str(keystore),
    "-storepass",password,
    "-keypass",password,
    "-alias",alias,
    "-keyalg","RSA",
    "-keysize","3072",
    "-validity","10000",
    "-dname","CN=Three Amigos Device Agent, O=Anderson House",
]
r=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
if r.returncode!=0:
    try: keystore.unlink()
    except FileNotFoundError: pass
    print("SIGNING_KEY_CREATE_FAILED")
    print((r.stderr or "")[-1000:])
    raise SystemExit(r.returncode)

password_file.write_text(password+"\n",encoding="utf-8")
alias_file.write_text(alias+"\n",encoding="utf-8")
for p in (keystore,password_file,alias_file):
    os.chmod(p,0o600)

print("SIGNING_KEY_CREATED")
print("PRIVATE_DIR="+str(private))
print("KEYSTORE_PRESENT=YES")
print("PASSWORD_PRINTED=NO")
