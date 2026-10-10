"""Staging-only Moto command guard. Never invokes a shell or writes to production."""
import json
import re

ALLOWED_ACTIONS = frozenset({"repo_status"})
ID_PATTERN = re.compile(r"^temperature-bee-[a-zA-Z0-9_-]{1,64}$")


def validate_command(raw):
    cmd = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(cmd, dict) or set(cmd) != {"id", "action"}:
        raise ValueError("unexpected command fields")
    if not isinstance(cmd["id"], str) or not ID_PATTERN.fullmatch(cmd["id"]):
        raise ValueError("invalid command id")
    if cmd["action"] not in ALLOWED_ACTIONS:
        raise ValueError("action not allowed in staging")
    return cmd


def execute_probe(raw, repo_status_provider):
    """Only permitted operation is a read-only status callback."""
    cmd = validate_command(raw)
    return {"id": cmd["id"], "action": "repo_status",
            "ok": True, "status": repo_status_provider(),
            "lane": "temperature-bee-staging"}


if __name__ == "__main__":
    import sys
    # Validation-only CLI: no phone actions or git writes.
    print(json.dumps(validate_command(sys.stdin.read()), sort_keys=True))
