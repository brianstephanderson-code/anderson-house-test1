#!/usr/bin/env python3
import hashlib, json, os, sys
from urllib import request, error

BASE="http://127.0.0.1:8787"

def http(method,path,data=None):
    body=None if data is None else json.dumps(data).encode("utf-8")
    req=request.Request(BASE+path,data=body,method=method)
    if body is not None:
        req.add_header("Content-Type","application/json")
    try:
        with request.urlopen(req,timeout=20) as r:
            return r.status, r.headers.get_content_type(), r.read()
    except error.HTTPError as e:
        return e.code, e.headers.get_content_type(), e.read()

def j(method,path,data=None):
    code,ctype,raw=http(method,path,data)
    try:
        payload=json.loads(raw.decode("utf-8"))
    except Exception:
        payload={"raw":raw[:200].decode("utf-8","replace")}
    return code,payload

result={"base":BASE}

code,payload=j("POST","/ping",{})
result["ping"]={"code":code,"payload":payload}
if code!=200 or not payload.get("ok"):
    print(json.dumps(result,indent=2))
    sys.exit(2)

code,payload=j("GET","/status")
result["status_before"]={"code":code,"payload":payload}

code,payload=j("POST","/capture",{"request_id":"real-phone-replay-parked"})
result["parked_capture"]={"code":code,"payload":payload}
if code!=409 or payload.get("error")!="parked_mode":
    print(json.dumps(result,indent=2))
    sys.exit(3)

code,payload=j("POST","/mode",{"mode":"active"})
result["activate"]={"code":code,"payload":payload}
if code!=200 or not payload.get("ok"):
    print(json.dumps(result,indent=2))
    sys.exit(4)

code,payload=j("POST","/capture",{"request_id":"real-phone-replay-001","reason":"look_at_this","context":{"job_id":"vision-band-real-phone-e2e"}})
result["capture"]={"code":code,"payload":payload}
if code!=200 or not payload.get("ok") or payload.get("mime")!="image/jpeg":
    print(json.dumps(result,indent=2))
    sys.exit(5)

path=payload.get("image_path")
if not path:
    print(json.dumps(result,indent=2))
    sys.exit(6)

code,ctype,raw=http("GET",path)
result["fetch"]={"code":code,"content_type":ctype,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
if code!=200 or ctype!="image/jpeg" or len(raw)<1000:
    print(json.dumps(result,indent=2))
    sys.exit(7)

code,payload=j("GET","/status")
result["status_after_capture"]={"code":code,"payload":payload}
if not payload.get("last_capture_ms"):
    print(json.dumps(result,indent=2))
    sys.exit(8)

code,payload=j("POST","/mode",{"mode":"parked"})
result["park"]={"code":code,"payload":payload}
if code!=200 or not payload.get("ok"):
    print(json.dumps(result,indent=2))
    sys.exit(9)

code,payload=j("POST","/capture",{"request_id":"real-phone-replay-after-park"})
result["post_park_capture"]={"code":code,"payload":payload}
if code!=409 or payload.get("error")!="parked_mode":
    print(json.dumps(result,indent=2))
    sys.exit(10)

result["overall"]="VISION_PHONE_REAL_ENDPOINT_REPLAY_GREEN"
print(json.dumps(result,indent=2))
