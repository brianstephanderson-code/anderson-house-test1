#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path

TEXT_EXTS = {".txt", ".md", ".html", ".htm", ".csv", ".json", ".xml", ".log", ".sh", ".py"}
MAX_BYTES = 12 * 1024 * 1024

def main():
    ap = argparse.ArgumentParser(description="Read-only local file search for Three Amigos")
    ap.add_argument("--query", required=True)
    ap.add_argument("--root", default="~")
    ap.add_argument("--name-any", nargs="*", default=[])
    ap.add_argument("--context", type=int, default=3)
    ap.add_argument("--max-matches", type=int, default=100)
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    query = args.query.casefold()
    name_any = [x.casefold() for x in args.name_any]
    hits = []
    files_checked = 0

    for base, dirs, files in os.walk(root):
        # Do not follow symlinks outside the selected tree.
        dirs[:] = [d for d in dirs if not (Path(base) / d).is_symlink()]
        for fn in files:
            p = Path(base) / fn
            if name_any and not any(term in fn.casefold() for term in name_any):
                continue
            try:
                if p.is_symlink() or p.suffix.casefold() not in TEXT_EXTS:
                    continue
                if p.stat().st_size > MAX_BYTES:
                    continue
                files_checked += 1
                lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue

            for i, line in enumerate(lines):
                if query not in line.casefold():
                    continue
                lo = max(0, i - args.context)
                hi = min(len(lines), i + args.context + 1)
                hits.append({
                    "file": str(p),
                    "line": i + 1,
                    "context": lines[lo:hi],
                })
                if len(hits) >= args.max_matches:
                    break
            if len(hits) >= args.max_matches:
                break
        if len(hits) >= args.max_matches:
            break

    print(json.dumps({
        "root": str(root),
        "query": args.query,
        "name_any": args.name_any,
        "files_checked": files_checked,
        "matches": len(hits),
        "hits": hits,
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
