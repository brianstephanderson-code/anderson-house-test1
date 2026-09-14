#!/usr/bin/env python3
import hashlib, json, os, socket, sqlite3, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path.home() / "anderson-house-phys"
ROOT.mkdir(parents=True, exist_ok=True)
DB = ROOT / "controller.db"
PRODUCTS = ROOT / "products"
PRODUCTS.mkdir(exist_ok=True)
PORT = 8765
RAW = "https://raw.githubusercontent.com/brianstephanderson-code/anderson-house-test1/main/parcels/AH-PHYS-001.json"
LEASE_SECONDS = 120


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def now():
    return int(time.time())


def load_manifest():
    req = urllib.request.Request(RAW, headers={"User-Agent": "Anderson-House-Moto"})
    with urllib.request.urlopen(req, timeout=20) as r:
        m = json.loads(r.read().decode())
    m["manifest_hash"] = hashlib.sha256(canonical(m)).hexdigest()
    return m


manifest = load_manifest()
conn = sqlite3.connect(DB, check_same_thread=False, isolation_level=None)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=FULL")
conn.execute("""
CREATE TABLE IF NOT EXISTS parcel (
 parcel_id TEXT PRIMARY KEY,
 manifest_json TEXT NOT NULL,
 manifest_hash TEXT NOT NULL,
 state TEXT NOT NULL,
 claim_gen INTEGER NOT NULL DEFAULT 0,
 control_gen INTEGER NOT NULL DEFAULT 1,
 worker TEXT,
 lease_until INTEGER,
 output_hash TEXT,
 output_path TEXT
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS requests (
 request_id TEXT PRIMARY KEY,
 response_json TEXT NOT NULL
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS events (
 seq INTEGER PRIMARY KEY AUTOINCREMENT,
 ts INTEGER NOT NULL,
 parcel_id TEXT NOT NULL,
 event TEXT NOT NULL,
 detail TEXT
)
""")

row = conn.execute("SELECT manifest_hash,state FROM parcel WHERE parcel_id=?", (manifest["parcel_id"],)).fetchone()
if row is None:
    conn.execute("BEGIN IMMEDIATE")
    conn.execute("INSERT INTO parcel(parcel_id,manifest_json,manifest_hash,state) VALUES(?,?,?,?)",
                 (manifest["parcel_id"], json.dumps(manifest, sort_keys=True), manifest["manifest_hash"], "READY"))
    conn.execute("INSERT INTO events(ts,parcel_id,event,detail) VALUES(?,?,?,?)",
                 (now(), manifest["parcel_id"], "MANIFESTED", manifest["manifest_hash"]))
    conn.execute("COMMIT")
elif row[0] != manifest["manifest_hash"]:
    raise SystemExit("STOP: manifest changed under same Parcel ID")


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def answer(handler, code, obj):
    data = json.dumps(obj, sort_keys=True).encode()
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/claim"):
            worker = "S20"
            conn.execute("BEGIN IMMEDIATE")
            r = conn.execute("SELECT manifest_json,state,claim_gen,control_gen,worker,lease_until FROM parcel WHERE parcel_id=?",
                             (manifest["parcel_id"],)).fetchone()
            mj, state, cg, ctrl, owner, lease = r
            t = now()
            if state == "DONE":
                conn.execute("COMMIT")
                return answer(self, 200, {"status":"DONE"})
            if state == "CLAIMED" and owner == worker and lease and lease >= t:
                conn.execute("COMMIT")
                return answer(self, 200, {"status":"CLAIMED","claim_gen":cg,"control_gen":ctrl,"manifest":json.loads(mj)})
            if state == "CLAIMED" and lease and lease >= t and owner != worker:
                conn.execute("COMMIT")
                return answer(self, 409, {"status":"BUSY"})
            cg += 1
            conn.execute("UPDATE parcel SET state='CLAIMED',claim_gen=?,worker=?,lease_until=? WHERE parcel_id=?",
                         (cg, worker, t + LEASE_SECONDS, manifest["parcel_id"]))
            conn.execute("INSERT INTO events(ts,parcel_id,event,detail) VALUES(?,?,?,?)",
                         (t, manifest["parcel_id"], "CLAIMED", f"worker={worker};claim={cg};control={ctrl}"))
            conn.execute("COMMIT")
            return answer(self, 200, {"status":"CLAIMED","claim_gen":cg,"control_gen":ctrl,"manifest":json.loads(mj)})

        if self.path.startswith("/status"):
            r = conn.execute("SELECT state,claim_gen,control_gen,worker,output_hash,output_path FROM parcel WHERE parcel_id=?",
                             (manifest["parcel_id"],)).fetchone()
            return answer(self, 200, {"parcel_id":manifest["parcel_id"],"state":r[0],"claim_gen":r[1],"control_gen":r[2],"worker":r[3],"output_hash":r[4],"output_path":r[5]})
        answer(self, 404, {"error":"not found"})

    def do_POST(self):
        if self.path != "/stage":
            return answer(self, 404, {"error":"not found"})
        n = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(n).decode())
        reqid = body.get("request_id")
        if not reqid:
            return answer(self, 400, {"error":"missing request_id"})

        conn.execute("BEGIN IMMEDIATE")
        old = conn.execute("SELECT response_json FROM requests WHERE request_id=?", (reqid,)).fetchone()
        if old:
            conn.execute("COMMIT")
            return answer(self, 200, json.loads(old[0]))

        r = conn.execute("SELECT state,claim_gen,control_gen,worker,manifest_json FROM parcel WHERE parcel_id=?",
                         (body.get("parcel_id"),)).fetchone()
        if not r:
            conn.execute("ROLLBACK")
            return answer(self, 404, {"error":"unknown parcel"})
        state,cg,ctrl,worker,mj = r
        if state == "DONE":
            resp = {"status":"DONE_ALREADY"}
        elif body.get("claim_gen") != cg or body.get("control_gen") != ctrl or worker != "S20":
            resp = {"status":"REJECTED_STALE_CLAIM","current_claim":cg,"current_control":ctrl}
        else:
            m = json.loads(mj)
            output = body.get("output", "")
            out_hash = hashlib.sha256(output.encode()).hexdigest()
            tmp = PRODUCTS / f"{m['parcel_id']}.{cg}.candidate.tmp"
            final = PRODUCTS / f"{m['parcel_id']}.{out_hash}.txt"
            tmp.write_text(output)
            with tmp.open("rb") as f:
                os.fsync(f.fileno())
            os.replace(tmp, final)
            if output != m["expected_output"]:
                conn.execute("UPDATE parcel SET state='QUARANTINED',output_hash=?,output_path=? WHERE parcel_id=?",
                             (out_hash, str(final), m["parcel_id"]))
                conn.execute("INSERT INTO events(ts,parcel_id,event,detail) VALUES(?,?,?,?)",
                             (now(),m["parcel_id"],"QUARANTINED",f"verification failed;hash={out_hash}"))
                resp = {"status":"QUARANTINED","reason":"verification failed","output_hash":out_hash}
            else:
                conn.execute("UPDATE parcel SET state='DONE',output_hash=?,output_path=?,lease_until=NULL WHERE parcel_id=?",
                             (out_hash, str(final), m["parcel_id"]))
                conn.execute("INSERT INTO events(ts,parcel_id,event,detail) VALUES(?,?,?,?)",
                             (now(),m["parcel_id"],"VERIFIED",out_hash))
                conn.execute("INSERT INTO events(ts,parcel_id,event,detail) VALUES(?,?,?,?)",
                             (now(),m["parcel_id"],"COMMITTED",str(final)))
                conn.execute("INSERT INTO events(ts,parcel_id,event,detail) VALUES(?,?,?,?)",
                             (now(),m["parcel_id"],"DONE",out_hash))
                resp = {"status":"DONE","parcel_id":m["parcel_id"],"output":output,"output_hash":out_hash}
        conn.execute("INSERT INTO requests(request_id,response_json) VALUES(?,?)", (reqid,json.dumps(resp,sort_keys=True)))
        conn.execute("COMMIT")
        answer(self, 200, resp)


print("ANDERSON HOUSE — MOTO CONTROLLER")
print(f"Parcel: {manifest['parcel_id']}")
print(f"Manifest hash: {manifest['manifest_hash']}")
print(f"S20 address: http://{local_ip()}:{PORT}")
print("Waiting for the bee...")
ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
