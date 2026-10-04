#!/usr/bin/env python3
import json, os, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST="127.0.0.1"
PORT=8765
DIR=Path.home()/".tomo_private_events"
LOG=DIR/"events.jsonl"\nNAV_STATE=DIR/"navigation_state.json"
MAX_LOG_BYTES=5*1024*1024

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path!="/event":
            self.send_error(404); return
        try:
            n=int(self.headers.get("Content-Length","0"))
            if n<=0 or n>65536:
                self.send_error(400); return
            event=json.loads(self.rfile.read(n).decode("utf-8"))
            source=str(event.get("source",""))[:32]
            package=str(event.get("packageName",""))[:256]
            if source not in {"accessibility","notification","navigation","location"} or not package:
                raise ValueError("invalid source/package")
            DIR.mkdir(parents=True,exist_ok=True)
            try: os.chmod(DIR,0o700)
            except OSError: pass
            rec={
                "receivedMs":int(time.time()*1000),
                "source":source,
                "packageName":package,
                "title":event.get("title"),
                "text":event.get("text"),
                "whenMs":event.get("whenMs"),
            }
            if source in {"navigation","location"}:
                state={}
                if NAV_STATE.exists():
                    try: state=json.loads(NAV_STATE.read_text(encoding="utf-8"))
                    except Exception: state={}
                state[source]=rec
                tmp=NAV_STATE.with_suffix(".tmp")
                tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                try: os.chmod(tmp,0o600)
                except OSError: pass
                tmp.replace(NAV_STATE)
                try: os.chmod(NAV_STATE,0o600)
                except OSError: pass

            if LOG.exists() and LOG.stat().st_size >= MAX_LOG_BYTES:
                old=DIR/"events.previous.jsonl"
                try: old.unlink()
                except FileNotFoundError: pass
                LOG.replace(old)
            with LOG.open("a",encoding="utf-8") as f:
                f.write(json.dumps(rec,ensure_ascii=False)+"\n")
            try: os.chmod(LOG,0o600)
            except OSError: pass
            body=b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            body=json.dumps({"ok":False,"error":type(e).__name__}).encode()
            self.send_response(400)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    def log_message(self, fmt, *args):
        return

if __name__=="__main__":
    DIR.mkdir(parents=True,exist_ok=True)
    try: os.chmod(DIR,0o700)
    except OSError: pass
    ThreadingHTTPServer((HOST,PORT),H).serve_forever()
