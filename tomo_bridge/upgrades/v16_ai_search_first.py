#!/data/data/com.termux/files/usr/bin/python
# V16 AI SEARCH FIRST
# Google Gemini 2.5 Flash + Google Search grounding.
# Goal: let the model understand, search, reformulate, read sources, and answer.
# Guardrail: local daily cap below the documented free-tier search-grounding allowance.

import os, sys, json, time, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

MODEL = os.environ.get("AMIGOS_GEMINI_MODEL", "gemini-2.5-flash")
DAILY_CAP = int(os.environ.get("AMIGOS_AI_DAILY_CAP", "400"))
STATE = Path.home() / "storage/downloads/three_amigos_dd/tomo_bridge/v16_ai_usage.json"

SYSTEM_GUIDANCE = """You are the search-and-reasoning brain for The 3 Amigos.
Answer the user's exact question using Google Search grounding when useful.
Do not invent facts. Preserve hard boundaries in the question.
Prefer direct, practical answers first, then concise supporting detail.
Use multiple independent sources when the question benefits from it.
Include real-world/end-user or practitioner evidence when useful.
If evidence is insufficient or conflicting, say so clearly.
Do not expose hidden reasoning. Return the best supported answer and sources.
"""

def load_state():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        d = json.loads(STATE.read_text())
    except Exception:
        d = {}
    if d.get("date") != today:
        d = {"date": today, "count": 0}
    return d

def save_state(d):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(d, indent=2) + "\n")

def extract_response(obj):
    texts = []
    sources = []
    queries = []

    for cand in obj.get("candidates", []) or []:
        content = cand.get("content", {}) or {}
        for part in content.get("parts", []) or []:
            if isinstance(part, dict) and part.get("text"):
                texts.append(part["text"])

        gm = cand.get("groundingMetadata", {}) or {}
        for q in gm.get("webSearchQueries", []) or []:
            if q and q not in queries:
                queries.append(q)

        chunks = gm.get("groundingChunks", []) or []
        for ch in chunks:
            web = (ch or {}).get("web", {}) or {}
            url = web.get("uri")
            title = web.get("title") or url
            if url and all(s.get("url") != url for s in sources):
                sources.append({"title": title, "url": url})

    return {
        "answer": "\n".join(x.strip() for x in texts if x.strip()).strip(),
        "sources": sources,
        "search_queries": queries,
    }

def ask(question):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return {
            "status": "SETUP_NEEDED",
            "reason": "GEMINI_API_KEY is not set",
            "question": question,
        }

    state = load_state()
    if int(state.get("count", 0)) >= DAILY_CAP:
        return {
            "status": "FREE_CAP_STOP",
            "reason": f"Local safety cap of {DAILY_CAP} grounded requests/day reached",
            "question": question,
        }

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + MODEL
        + ":generateContent"
    )

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_GUIDANCE}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": question}]
            }
        ],
        "tools": [
            {"google_search": {}}
        ],
        "generationConfig": {
            "temperature": 0.2
        }
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
        },
        method="POST",
    )

    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            obj = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return {
            "status": "HTTP_ERROR",
            "code": e.code,
            "body": body[:4000],
            "question": question,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": repr(e),
            "question": question,
        }

    state["count"] = int(state.get("count", 0)) + 1
    save_state(state)

    out = extract_response(obj)
    out.update({
        "status": "ANSWER_READY" if out["answer"] else "NO_ANSWER",
        "question": question,
        "model": MODEL,
        "seconds": round(time.time() - started, 1),
        "usage_today": state["count"],
        "local_daily_cap": DAILY_CAP,
        "engine": "Gemini + Google Search grounding",
    })
    return out

def main():
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("Question: ").strip()
    result = ask(question)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
