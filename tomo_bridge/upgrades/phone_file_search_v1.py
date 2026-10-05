#!/usr/bin/env python3
"""Three Amigos read-only phone file search.

Purpose: search Termux-owned files from the remote Tomo bridge without UI automation.
Safe by design: read-only, bounded results, bounded file size, no shell execution.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HOME = Path.home().resolve()
TEXT_EXTENSIONS = {
    ".txt", ".md", ".html", ".htm", ".csv", ".json", ".xml", ".log",
    ".sh", ".py", ".kt", ".java", ".yaml", ".yml"
}
SKIP_DIR_NAMES = {
    ".git", "__pycache__", ".cache", "node_modules", ".gradle", ".npm", ".pnpm-store"
}
MAX_FILE_BYTES = 12 * 1024 * 1024
MAX_MATCHES = 200
MAX_FILES = 20000


def safe_root(raw: str) -> Path:
    aliases = {
        "home": HOME,
        "~": HOME,
        "termux-home": HOME,
    }
    p = aliases.get(raw, Path(raw).expanduser())
    p = p.resolve()
    # Remote file search is deliberately limited to Termux home.
    if not (p == HOME or HOME in p.parents):
        raise ValueError("root outside Termux home")
    if not p.exists() or not p.is_dir():
        raise ValueError("root does not exist or is not a directory")
    return p


def iter_files(root: Path):
    seen = 0
    stack = [root]
    while stack and seen < MAX_FILES:
        current = stack.pop()
        try:
            children = list(current.iterdir())
        except (PermissionError, OSError):
            continue
        for child in children:
            try:
                if child.is_symlink():
                    continue
                if child.is_dir():
                    if child.name not in SKIP_DIR_NAMES:
                        stack.append(child)
                    continue
                if child.is_file():
                    seen += 1
                    yield child
                    if seen >= MAX_FILES:
                        return
            except OSError:
                continue


def search(root: Path, query: str) -> dict:
    q = query.casefold()
    matches = []
    files_checked = 0
    text_files_checked = 0

    for path in iter_files(root):
        files_checked += 1
        rel = str(path.relative_to(root))

        if q in path.name.casefold():
            matches.append({
                "kind": "name",
                "path": rel,
            })
            if len(matches) >= MAX_MATCHES:
                break

        try:
            size = path.stat().st_size
        except OSError:
            continue
        if path.suffix.casefold() not in TEXT_EXTENSIONS or size > MAX_FILE_BYTES:
            continue

        text_files_checked += 1
        try:
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                for lineno, line in enumerate(fh, 1):
                    if q in line.casefold():
                        excerpt = " ".join(line.strip().split())[:700]
                        matches.append({
                            "kind": "text",
                            "path": rel,
                            "line": lineno,
                            "excerpt": excerpt,
                        })
                        if len(matches) >= MAX_MATCHES:
                            break
        except (PermissionError, OSError):
            continue

        if len(matches) >= MAX_MATCHES:
            break

    return {
        "ok": True,
        "query": query,
        "root": str(root),
        "files_checked": files_checked,
        "text_files_checked": text_files_checked,
        "matches": matches,
        "truncated": len(matches) >= MAX_MATCHES,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--root", default="home")
    args = ap.parse_args()

    query = args.query.strip()
    if not query:
        raise SystemExit("query must not be empty")
    if len(query) > 200:
        raise SystemExit("query too long")

    result = search(safe_root(args.root), query)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
