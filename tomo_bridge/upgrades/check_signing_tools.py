#!/usr/bin/env python3
import shutil
print("KEYTOOL="+("YES" if shutil.which("keytool") else "NO"))
print("BASE64="+("YES" if shutil.which("base64") else "NO"))
print("OPENSSL="+("YES" if shutil.which("openssl") else "NO"))
