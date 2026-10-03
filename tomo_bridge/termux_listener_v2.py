#!/usr/bin/env python3
import json, os, subprocess, time, threading, urllib.request
from pathlib import Path

REPO = Path.home() / "anderson-house-mailbox"
INBOX = REPO / "tomo_bridge" / "inbox_v2"
OUTBOX = REPO / "tomo_bridge" / "outbox_v2"
DONE = REPO / "tomo_bridge" / "archive_v2"
POLL_SECONDS = 5
WAKE_TOPIC = "ah3a-wake-v2-4f11e8c2877b4d42a7f3a9e22b16c501"
WAKE_URL = f"https://ntfy.sh/{WAKE_TOPIC}/json"

ALLOWED_ROOTS = [
    (REPO / "tomo_bridge" / "upgrades").resolve(),
    (REPO / "research").resolve(),
    (REPO / "search-universe").resolve(),
]

CODEX_TERMUX = "codex-termux"
PNPM_BIN = Path.home() / ".local" / "share" / "pnpm" / "bin"

def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=REPO, text=True, capture_output=True, check=check)

def safe_python_path(raw):
    p = (REPO / raw).resolve()
    if p.suffix != ".py":
        raise ValueError("only .py files are allowed")
    if not any(str(p).startswith(str(root) + os.sep) or p == root for root in ALLOWED_ROOTS):
        raise ValueError("path outside allow-list")
    if not p.exists():
        raise FileNotFoundError(str(p))
    return p

def safe_workdir(raw):
    if not raw:
        return REPO
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = REPO / p
    p = p.resolve()
    allowed = [REPO.resolve(), (Path.home() / "downloads").resolve()]
    if not any(str(p).startswith(str(root) + os.sep) or p == root for root in allowed):
        raise ValueError("workdir outside allow-list")
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(str(p))
    return p

def codex_env():
    env = os.environ.copy()
    env["PATH"] = str(PNPM_BIN) + os.pathsep + env.get("PATH", "")
    return env

def write_result(cmd_id, result):
    OUTBOX.mkdir(parents=True, exist_ok=True)
    path = OUTBOX / f"{cmd_id}.result.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return path

def archive_command(path):
    DONE.mkdir(parents=True, exist_ok=True)
    target = DONE / path.name
    path.replace(target)
    return target

def process(path):
    cmd = json.loads(path.read_text())
    cmd_id = cmd.get("id") or path.stem
    action = cmd.get("action")
    result = {"id": cmd_id, "action": action, "ok": False, "bridge_version": "v2"}

    try:
        if action == "git_sync":
            r = git("pull", "--ff-only", "origin", "main")
            result.update(ok=True, stdout=r.stdout, stderr=r.stderr)

        elif action == "run_repo_python":
            script = safe_python_path(cmd["path"])
            args = [str(x) for x in cmd.get("args", [])]
            r = subprocess.run(["python", str(script), *args], cwd=REPO, text=True, capture_output=True,
                               timeout=int(cmd.get("timeout", 900)))
            result.update(ok=(r.returncode == 0), returncode=r.returncode,
                          stdout=r.stdout[-20000:], stderr=r.stderr[-20000:])

        elif action == "codex_exec":
            prompt = str(cmd.get("prompt", "")).strip()
            if not prompt:
                raise ValueError("codex_exec requires a non-empty prompt")
            if len(prompt) > 20000:
                raise ValueError("prompt too long")
            workdir = safe_workdir(cmd.get("workdir"))
            allow_write = bool(cmd.get("allow_write", False))
            if not allow_write:
                prompt = ("READ-ONLY JOB. Do not create, edit, delete, move, rename, install, "
                          "or change files, apps, settings, services, network state, or system state. "
                          "Only inspect/read and report.\n\n" + prompt)
            args = [CODEX_TERMUX, "exec", "--skip-git-repo-check", "--ephemeral",
                    "-s", "danger-full-access", "-c", 'approval_policy="never"',
                    "-C", str(workdir), prompt]
            r = subprocess.run(args, cwd=workdir, text=True, capture_output=True,
                               timeout=int(cmd.get("timeout", 900)), env=codex_env())
            result.update(ok=(r.returncode == 0), returncode=r.returncode,
                          workdir=str(workdir), allow_write=allow_write,
                          stdout=r.stdout[-30000:], stderr=r.stderr[-30000:])

        elif action == "android_launch":
            package = str(cmd.get("package", "")).strip()
            component = str(cmd.get("component", "")).strip()
            if not package or not component:
                raise ValueError("android_launch requires package and component")
            if not component.startswith(package + "/"):
                raise ValueError("component must belong to package")
            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c",
                 f"am start -n {component}"],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            result.update(
                ok=(r.returncode == 0),
                returncode=r.returncode,
                package=package,
                component=component,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_text_cycle":
            package = str(cmd.get("package", "")).strip()
            text_value = str(cmd.get("text", "")).strip()
            expected_before = str(cmd.get("expected_before", "")).strip()
            expected_after = str(cmd.get("expected_after", "")).strip()
            x = int(cmd.get("x"))
            y = int(cmd.get("y"))

            if not package or not expected_before or not expected_after:
                raise ValueError("android_guarded_text_cycle requires package, expected_before, expected_after")
            if not text_value or len(text_value) > 64 or not all(ch.isalnum() or ch in "._-" for ch in text_value):
                raise ValueError("text must be 1-64 safe ASCII characters")
            if not (0 <= x <= 5000 and 0 <= y <= 5000):
                raise ValueError("tap coordinates out of range")

            tmp1 = "/sdcard/tomo_guard_before.xml"
            tmp2 = "/sdcard/tomo_guard_after.xml"
            tmp3 = "/sdcard/tomo_guard_restore.xml"
            deletes = " ".join(["input keyevent KEYCODE_DEL;" for _ in text_value])

            shell = f'''
set -e
focus="$(dumpsys window | grep mCurrentFocus | head -n 1)"
case "$focus" in *"{package}/"*) ;; *) echo ABORT_WRONG_FOREGROUND_BEFORE; exit 41;; esac

uiautomator dump {tmp1} >/dev/null
grep -F 'package="{package}"' {tmp1} >/dev/null
grep -F 'text="{expected_before}"' {tmp1} >/dev/null

input tap {x} {y}

focus="$(dumpsys window | grep mCurrentFocus | head -n 1)"
case "$focus" in *"{package}/"*) ;; *) echo ABORT_WRONG_FOREGROUND_AFTER_TAP; exit 42;; esac

input keyevent KEYCODE_MOVE_END
input text {text_value}

focus="$(dumpsys window | grep mCurrentFocus | head -n 1)"
case "$focus" in *"{package}/"*) ;; *) echo ABORT_WRONG_FOREGROUND_AFTER_TYPE; exit 43;; esac

uiautomator dump {tmp2} >/dev/null
grep -F 'package="{package}"' {tmp2} >/dev/null
grep -F 'text="{expected_after}"' {tmp2} >/dev/null
echo APPEND_VERIFIED

{deletes}

focus="$(dumpsys window | grep mCurrentFocus | head -n 1)"
case "$focus" in *"{package}/"*) ;; *) echo ABORT_WRONG_FOREGROUND_AFTER_DELETE; exit 44;; esac

uiautomator dump {tmp3} >/dev/null
grep -F 'package="{package}"' {tmp3} >/dev/null
grep -F 'text="{expected_before}"' {tmp3} >/dev/null
echo RESTORE_VERIFIED
rm -f {tmp1} {tmp2} {tmp3}
'''

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            result.update(
                ok=(r.returncode == 0),
                returncode=r.returncode,
                package=package,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_open_text_cycle":
            package = str(cmd.get("package", "")).strip()
            component = str(cmd.get("component", "")).strip()
            text_value = str(cmd.get("text", "")).strip()
            expected_before = str(cmd.get("expected_before", "")).strip()
            expected_after = str(cmd.get("expected_after", "")).strip()
            x = int(cmd.get("x"))
            y = int(cmd.get("y"))

            if not package or not component or not component.startswith(package + "/"):
                raise ValueError("android_guarded_open_text_cycle requires a valid package/component pair")
            if not expected_before or not expected_after:
                raise ValueError("expected_before and expected_after are required")
            if not text_value or len(text_value) > 64 or not all(ch.isalnum() or ch in "._-" for ch in text_value):
                raise ValueError("text must be 1-64 safe ASCII characters")
            if not (0 <= x <= 5000 and 0 <= y <= 5000):
                raise ValueError("tap coordinates out of range")

            tmp1 = "/sdcard/tomo_open_guard_before.xml"
            tmp2 = "/sdcard/tomo_open_guard_after.xml"
            tmp3 = "/sdcard/tomo_open_guard_restore.xml"
            deletes = " ".join(["input keyevent KEYCODE_DEL;" for _ in text_value])

            shell = f"""
set -e
rm -f {tmp1} {tmp2} {tmp3}
am start -n {component} >/dev/null
sleep 1

focus="$(dumpsys window | grep mCurrentFocus | head -n 1)"
case "$focus" in *"{package}/"*) ;; *) echo ABORT_WRONG_FOREGROUND_OPEN; exit 61;; esac

uiautomator dump {tmp1} >/dev/null
grep -F 'package="{package}"' {tmp1} >/dev/null
grep -F 'text="{expected_before}"' {tmp1} >/dev/null

input tap {x} {y}

focus="$(dumpsys window | grep mCurrentFocus | head -n 1)"
case "$focus" in *"{package}/"*) ;; *) echo ABORT_WRONG_FOREGROUND_AFTER_TAP; exit 62;; esac

input keyevent KEYCODE_MOVE_END
input text {text_value}

uiautomator dump {tmp2} >/dev/null
grep -F 'package="{package}"' {tmp2} >/dev/null
grep -F 'text="{expected_after}"' {tmp2} >/dev/null
echo APPEND_VERIFIED

{deletes}

uiautomator dump {tmp3} >/dev/null
grep -F 'package="{package}"' {tmp3} >/dev/null
grep -F 'text="{expected_before}"' {tmp3} >/dev/null
echo RESTORE_VERIFIED

rm -f {tmp1} {tmp2} {tmp3}
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "APPEND_VERIFIED" in proof_output and "RESTORE_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_find_edittext_cycle":
            package = str(cmd.get("package", "")).strip()
            component = str(cmd.get("component", "")).strip()
            text_value = str(cmd.get("text", "")).strip()
            expected_before = str(cmd.get("expected_before", "")).strip()
            expected_after = str(cmd.get("expected_after", "")).strip()

            if not package or not component or not component.startswith(package + "/"):
                raise ValueError("android_guarded_find_edittext_cycle requires a valid package/component pair")
            if not expected_before or not expected_after:
                raise ValueError("expected_before and expected_after are required")
            if not text_value or len(text_value) > 64 or not all(ch.isalnum() or ch in "._-" for ch in text_value):
                raise ValueError("text must be 1-64 safe ASCII characters")

            tmp1 = "/sdcard/tomo_find_before.xml"
            tmp2 = "/sdcard/tomo_find_after.xml"
            tmp3 = "/sdcard/tomo_find_restore.xml"
            deletes = " ".join(["input keyevent KEYCODE_DEL;" for _ in text_value])

            shell = f"""
set -e
rm -f {tmp1} {tmp2} {tmp3}
am start -n {component} >/dev/null
sleep 1

# Treat the visible accessibility tree as the authoritative foreground gate.
# Some Android builds report stale mCurrentFocus/mResumedActivity during app transitions.
uiautomator dump {tmp1} >/dev/null
grep -F 'package="{package}"' {tmp1} >/dev/null || {{ echo ABORT_WRONG_VISIBLE_PACKAGE_OPEN; exit 71; }}
grep -F 'text="{expected_before}"' {tmp1} >/dev/null || {{ echo ABORT_EXPECTED_TEXT_NOT_FOUND; exit 72; }}

node="$(grep -o '<node[^>]*class="android.widget.EditText"[^>]*>' {tmp1} | head -n 1)"
[ -n "$node" ] || {{ echo ABORT_NO_EDITTEXT; exit 73; }}
bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_BAD_BOUNDS; exit 74; }}
x=$(( ($1 + $3) / 2 ))
y=$(( ($2 + $4) / 2 ))

input tap "$x" "$y"
input keyevent KEYCODE_MOVE_END
input text {text_value}

uiautomator dump {tmp2} >/dev/null
grep -F 'package="{package}"' {tmp2} >/dev/null || {{ echo ABORT_WRONG_VISIBLE_PACKAGE_AFTER_TYPE; exit 75; }}
grep -F 'text="{expected_after}"' {tmp2} >/dev/null || {{ echo ABORT_EXPECTED_TYPED_TEXT_NOT_FOUND; exit 76; }}
echo APPEND_VERIFIED

{deletes}

uiautomator dump {tmp3} >/dev/null
grep -F 'package="{package}"' {tmp3} >/dev/null || {{ echo ABORT_WRONG_VISIBLE_PACKAGE_AFTER_DELETE; exit 77; }}
grep -F 'text="{expected_before}"' {tmp3} >/dev/null || {{ echo ABORT_EXPECTED_RESTORE_TEXT_NOT_FOUND; exit 78; }}
echo RESTORE_VERIFIED

rm -f {tmp1} {tmp2} {tmp3}
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "APPEND_VERIFIED" in proof_output and "RESTORE_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_find_edittext_submit":
            package = str(cmd.get("package", "")).strip()
            component = str(cmd.get("component", "")).strip()
            text_value = str(cmd.get("text", "")).strip()
            expected_before = str(cmd.get("expected_before", "")).strip()
            submit_key = str(cmd.get("submit_key", "KEYCODE_ENTER")).strip()

            if not package or not component or not component.startswith(package + "/"):
                raise ValueError("android_guarded_find_edittext_submit requires a valid package/component pair")
            if not expected_before:
                raise ValueError("expected_before is required")
            if not text_value or len(text_value) > 128 or not all(ch.isalnum() or ch in " ._-" for ch in text_value):
                raise ValueError("text must be 1-128 safe ASCII characters")
            if submit_key not in {"KEYCODE_ENTER", "KEYCODE_SEARCH"}:
                raise ValueError("unsupported submit key")

            tmp1 = "/sdcard/tomo_submit_before.xml"
            tmp2 = "/sdcard/tomo_submit_after.xml"

            shell = f"""
set -e
rm -f {tmp1} {tmp2}
am start -n {component} >/dev/null
sleep 1

uiautomator dump {tmp1} >/dev/null
grep -F 'package="{package}"' {tmp1} >/dev/null || {{ echo ABORT_WRONG_VISIBLE_PACKAGE_OPEN; exit 81; }}
grep -F 'text="{expected_before}"' {tmp1} >/dev/null || {{ echo ABORT_EXPECTED_TEXT_NOT_FOUND; exit 82; }}

node="$(grep -o '<node[^>]*class="android.widget.EditText"[^>]*>' {tmp1} | head -n 1)"
[ -n "$node" ] || {{ echo ABORT_NO_EDITTEXT; exit 83; }}
bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_BAD_BOUNDS; exit 84; }}
x=$(( ($1 + $3) / 2 ))
y=$(( ($2 + $4) / 2 ))

input tap "$x" "$y"
input keyevent KEYCODE_MOVE_END
input text "{text_value}"
input keyevent {submit_key}
sleep 2

uiautomator dump {tmp2} >/dev/null
grep -F 'package="{package}"' {tmp2} >/dev/null || {{ echo ABORT_WRONG_VISIBLE_PACKAGE_AFTER_SUBMIT; exit 85; }}
grep -F '{text_value}' {tmp2} >/dev/null || {{ echo ABORT_SUBMITTED_TEXT_NOT_VISIBLE; exit 86; }}
echo SUBMIT_VERIFIED

rm -f {tmp1} {tmp2}
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SUBMIT_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                text=text_value,
                submit_key=submit_key,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_self_draft":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if target_title != "+64 20 449 8229 (You)":
                raise ValueError("android_guarded_whatsapp_self_draft is restricted to the verified self-chat")
            if text_value != "TOMO TEST":
                raise ValueError("android_guarded_whatsapp_self_draft currently allows only TOMO TEST")

            tmp1 = "/data/local/tmp/tomo_wa_self_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_self_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_self_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
count="$(printf '%s\n' "$node" | sed '/^$/d' | wc -l)"
[ "$count" -eq 1 ] || {{ echo ABORT_SELF_CHAT_MATCH_COUNT_"$count"; exit 91; }}

bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SELF_CHAT_BAD_BOUNDS; exit 92; }}
x=$(( ($1 + $3) / 2 ))
y=$(( ($2 + $4) / 2 ))
input tap "$x" "$y"
sleep 1

uiautomator dump {tmp2} >/dev/null
title_node="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' || true)"
[ "$(printf '%s\n' "$title_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_WRONG_SELF_CHAT_TITLE; exit 93; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_ENTRY_MATCH_COUNT; exit 94; }}

bounds="$(printf '%s' "$entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_ENTRY_BAD_BOUNDS; exit 95; }}
x=$(( ($1 + $3) / 2 ))
y=$(( ($2 + $4) / 2 ))
input tap "$x" "$y"
input keyevent KEYCODE_MOVE_END
input text "{text_value}"

uiautomator dump {tmp3} >/dev/null
after="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$after" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_NOT_VERIFIED; exit 96; }}
echo DRAFT_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "DRAFT_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_draft":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if not target_title or len(target_title) > 120:
                raise ValueError("android_guarded_whatsapp_draft requires a target_title")
            if not text_value or len(text_value) > 256:
                raise ValueError("android_guarded_whatsapp_draft text must be 1-256 characters")
            if any(ord(ch) < 32 for ch in text_value):
                raise ValueError("android_guarded_whatsapp_draft text contains control characters")

            tmp1 = "/data/local/tmp/tomo_wa_generic_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_generic_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_generic_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
count="$(printf '%s\n' "$node" | sed '/^$/d' | wc -l)"
[ "$count" -eq 1 ] || {{ echo ABORT_CHAT_MATCH_COUNT_"$count"; exit 111; }}

bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_CHAT_BAD_BOUNDS; exit 112; }}
x=$(( ($1 + $3) / 2 ))
y=$(( ($2 + $4) / 2 ))
input tap "$x" "$y"
sleep 1

uiautomator dump {tmp2} >/dev/null
title_node="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' || true)"
[ "$(printf '%s\n' "$title_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_WRONG_CHAT_TITLE; exit 113; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_ENTRY_MATCH_COUNT; exit 114; }}

bounds="$(printf '%s' "$entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_ENTRY_BAD_BOUNDS; exit 115; }}
x=$(( ($1 + $3) / 2 ))
y=$(( ($2 + $4) / 2 ))
input tap "$x" "$y"
input keyevent KEYCODE_MOVE_END
input text "{text_value}"

uiautomator dump {tmp3} >/dev/null
after="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$after" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_NOT_VERIFIED; exit 116; }}
echo DRAFT_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "DRAFT_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_self_repair_draft":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            expected_before = str(cmd.get("expected_before", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if target_title != "+64 20 449 8229 (You)":
                raise ValueError("repair action is restricted to the verified self-chat")
            if expected_before != "HELLO FROM too" or text_value != "HELLO FROM TOMO":
                raise ValueError("unexpected repair payload")

            encoded_text = text_value.replace(" ", "%s")
            tmp1 = "/data/local/tmp/tomo_wa_repair_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_repair_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_repair_after.xml"
            deletes = " ".join(["input keyevent KEYCODE_DEL;" for _ in expected_before])

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
[ "$(printf '%s\n' "$node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SELF_CHAT_MATCH; exit 121; }}
bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SELF_CHAT_BAD_BOUNDS; exit 122; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 123; }}
entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{expected_before}"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_EXPECTED_BAD_DRAFT_NOT_FOUND; exit 124; }}

bounds="$(printf '%s' "$entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_ENTRY_BAD_BOUNDS; exit 125; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
input keyevent KEYCODE_MOVE_END
{deletes}
input text "{encoded_text}"

uiautomator dump {tmp3} >/dev/null
after="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$after" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_REPAIRED_DRAFT_NOT_VERIFIED; exit 126; }}
echo DRAFT_REPAIR_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "DRAFT_REPAIR_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                expected_before=expected_before,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_whatsapp_search_inspect":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            if not target_title or len(target_title) > 120:
                raise ValueError("target_title is required")

            search_text = target_title.replace(" ", "%s")
            tmp1 = "/data/local/tmp/tomo_wa_inspect_home.xml"
            tmp2 = "/data/local/tmp/tomo_wa_inspect_box.xml"
            tmp3 = "/data/local/tmp/tomo_wa_inspect_results.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

search_node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/search_bar_inner_layout"' || true)"
[ "$(printf '%s\n' "$search_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEARCH_BAR_MATCH; exit 201; }}

bounds="$(printf '%s' "$search_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEARCH_BAR_BOUNDS; exit 202; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
search_entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | head -n 1 || true)"
[ -n "$search_entry" ] || {{ echo ABORT_NO_SEARCH_EDITTEXT; exit 203; }}

bounds="$(printf '%s' "$search_entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEARCH_ENTRY_BOUNDS; exit 204; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
input text "{search_text}"
sleep 1

uiautomator dump {tmp3} >/dev/null

echo INSPECT_MATCHES_BEGIN
grep -o '<node[^>]*>' {tmp3} | grep -F 'text="{target_title}"' || true
echo INSPECT_MATCHES_END
echo INSPECT_CONTEXT_BEGIN
grep -F -C 3 'text="{target_title}"' {tmp3} || true
echo INSPECT_CONTEXT_END
echo INSPECT_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "INSPECT_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                stdout=r.stdout[-12000:],
                stderr=r.stderr[-12000:],
            )

        elif action == "android_guarded_whatsapp_scroll_send":
            package = "com.whatsapp"
            component = "com.whatsapp/.home.ui.HomeActivity"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if not target_title or len(target_title) > 120:
                raise ValueError("target_title is required")
            if not text_value or len(text_value) > 256:
                raise ValueError("text must be 1-256 characters")
            if any(ord(ch) < 32 for ch in target_title + text_value):
                raise ValueError("text contains control characters")

            tmp1 = "/data/local/tmp/tomo_wa_scroll_send_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_scroll_send_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_scroll_send_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am force-stop {package} >/dev/null 2>&1 || true
sleep 0.5
am start -n {component} >/dev/null
sleep 1

result_node=""
for pass in 1 2 3 4 5 6 7 8 9 10 11 12; do
  uiautomator dump {tmp1} >/dev/null
  result_node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
  count="$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)"
  if [ "$count" -eq 1 ]; then
    break
  fi
  input swipe 360 1280 360 650 350
  sleep 0.7
done

[ "$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_MAIN_LIST_MATCH_AFTER_FULL_SCAN; exit 241; }}

bounds="$(printf '%s' "$result_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_MAIN_LIST_BOUNDS; exit 242; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 243; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_TEXT_NOT_VERIFIED; exit 244; }}

send_node="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/send"' || true)"
[ "$(printf '%s\n' "$send_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEND_BUTTON_MATCH; exit 245; }}

bounds="$(printf '%s' "$send_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEND_BOUNDS; exit 246; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp3} >/dev/null
grep -F 'resource-id="com.whatsapp:id/entry"' {tmp3} | grep -F 'text="Message"' >/dev/null || {{ echo ABORT_ENTRY_NOT_CLEARED; exit 247; }}
grep -F 'text="{text_value}"' {tmp3} >/dev/null || {{ echo ABORT_SENT_TEXT_NOT_VISIBLE; exit 248; }}
echo SCROLL_SEND_VERIFIED
cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""
            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO, text=True, capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SCROLL_SEND_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_whatsapp_notification_summary":
            package = "com.whatsapp"
            shell = r"""
set -e
echo WHATSAPP_NOTIFICATION_SUMMARY_BEGIN

dumpsys notification --noredact 2>/dev/null | awk '
  /NotificationRecord\(/ {
    if (inrec && hit) print rec
    rec=$0 "\n"; inrec=1; hit=($0 ~ /pkg=com\.whatsapp/)
    next
  }
  inrec {
    rec=rec $0 "\n"
    if ($0 ~ /pkg=com\.whatsapp/ || $0 ~ /opPkg=com\.whatsapp/ || $0 ~ /ApplicationInfo.*com\.whatsapp/) hit=1
  }
  END { if (inrec && hit) print rec }
' | grep -E 'android\.title=|android\.text=|android\.messages=|sender=|text=|time=|type=|uri=|tickerText=' || true

echo WHATSAPP_NOTIFICATION_SUMMARY_END
echo NOTIFICATION_SUMMARY_VERIFIED
"""
            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO, text=True, capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "NOTIFICATION_SUMMARY_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                stdout=r.stdout[-12000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_whatsapp_notification_inspect":
            package = "com.whatsapp"
            shell = r"""
set -e
echo WHATSAPP_NOTIFICATIONS_BEGIN
dumpsys notification --noredact 2>/dev/null | grep -E 'com\.whatsapp|android\.(title|text|bigText|messages)|postTime=|tickerText=|extras=|NotificationRecord' || true
echo WHATSAPP_NOTIFICATIONS_END
echo NOTIFICATION_INSPECT_VERIFIED
"""
            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO, text=True, capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "NOTIFICATION_INSPECT_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                stdout=r.stdout[-16000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_whatsapp_message_snapshot":
            package = "com.whatsapp"
            component = "com.whatsapp/.home.ui.HomeActivity"
            target_title = str(cmd.get("target_title", "")).strip()
            public_key_pem = str(cmd.get("return_public_key_pem", "")).strip()

            if not target_title or len(target_title) > 120:
                raise ValueError("target_title is required")
            if any(ord(ch) < 32 for ch in target_title):
                raise ValueError("target_title contains control characters")

            safe_id = "".join(ch for ch in str(cmd_id) if ch.isalnum() or ch in "._-")[:96] or "snapshot"
            private_dir = Path.home() / ".tomo_private_snapshots"
            private_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(private_dir, 0o700)

            tmp_xml = "/data/local/tmp/tomo_wa_message_snapshot.xml"
            local_xml = private_dir / f"{safe_id}.xml"
            local_png = private_dir / f"{safe_id}.png"
            local_tar = private_dir / f"{safe_id}.tar"
            local_pub = private_dir / f"{safe_id}.pub.pem"

            # The title is shell-quoted defensively because it comes from the command.
            import shlex
            q_title = shlex.quote(target_title)
            shell = f"""
set -e
cleanup() {{ rm -f {tmp_xml}; }}
trap cleanup EXIT

am force-stop {package} >/dev/null 2>&1 || true
sleep 0.5
am start -n {component} >/dev/null
sleep 1

result_node=""
for pass in 1 2 3 4 5 6 7 8 9 10 11 12; do
  uiautomator dump {tmp_xml} >/dev/null
  result_node="$(grep -o '<node[^>]*>' {tmp_xml} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F "text=\\"{target_title}\\"" || true)"
  count="$(printf '%s\\n' "$result_node" | sed '/^$/d' | wc -l)"
  if [ "$count" -eq 1 ]; then
    break
  fi
  input swipe 360 1280 360 650 350
  sleep 0.7
done

[ "$(printf '%s\\n' "$result_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_MAIN_LIST_MATCH_AFTER_FULL_SCAN >&2; exit 271; }}

bounds="$(printf '%s' "$result_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_MAIN_LIST_BOUNDS >&2; exit 272; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp_xml} >/dev/null
grep -o '<node[^>]*>' {tmp_xml} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F "text=\\"{target_title}\\"" >/dev/null || {{ echo ABORT_WRONG_CHAT >&2; exit 273; }}

cat {tmp_xml}
cleanup
trap - EXIT
"""
            nav = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO, text=True, capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            if nav.returncode != 0:
                result.update(
                    ok=False,
                    returncode=nav.returncode,
                    package=package,
                    component=component,
                    target_title=target_title,
                    stderr=nav.stderr[-4000:],
                )
            else:
                local_xml.write_text(nav.stdout, encoding="utf-8")

                shot = subprocess.run(
                    [str(Path.home() / "bin" / "rish"), "-c", "screencap -p"],
                    cwd=REPO, capture_output=True,
                    timeout=int(cmd.get("timeout", 60)),
                )
                if shot.returncode != 0 or not shot.stdout.startswith(b"\\x89PNG\\r\\n\\x1a\\n"):
                    raise RuntimeError("screencap failed or did not return PNG data")
                local_png.write_bytes(shot.stdout)

                tar = subprocess.run(
                    ["tar", "-cf", str(local_tar), local_xml.name, local_png.name],
                    cwd=private_dir, text=True, capture_output=True,
                    timeout=30,
                )
                if tar.returncode != 0:
                    raise RuntimeError("snapshot bundle creation failed: " + tar.stderr[-1000:])

                # Never put plaintext WhatsApp evidence in the GitHub outbox.
                # With a caller-supplied RSA public key, publish only encrypted evidence.
                if public_key_pem:
                    local_pub.write_text(public_key_pem + ("\\n" if not public_key_pem.endswith("\\n") else ""), encoding="utf-8")
                    os.chmod(local_pub, 0o600)

                    keyrun = subprocess.run(
                        ["openssl", "rand", "-hex", "32"],
                        text=True, capture_output=True, timeout=15,
                    )
                    if keyrun.returncode != 0:
                        raise RuntimeError("openssl random key generation failed")
                    bundle_key = keyrun.stdout.strip()

                    enc_bundle = OUTBOX / f"{safe_id}.snapshot.tar.enc"
                    enc_key = OUTBOX / f"{safe_id}.snapshot.key.enc"
                    OUTBOX.mkdir(parents=True, exist_ok=True)

                    enc = subprocess.run(
                        ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt",
                         "-pass", f"pass:{bundle_key}",
                         "-in", str(local_tar), "-out", str(enc_bundle)],
                        text=True, capture_output=True, timeout=60,
                    )
                    if enc.returncode != 0:
                        raise RuntimeError("snapshot encryption failed: " + enc.stderr[-1000:])

                    keyenc = subprocess.run(
                        ["openssl", "pkeyutl", "-encrypt", "-pubin",
                         "-inkey", str(local_pub),
                         "-pkeyopt", "rsa_padding_mode:oaep",
                         "-in", "/dev/stdin", "-out", str(enc_key)],
                        input=bundle_key, text=True, capture_output=True, timeout=30,
                    )
                    if keyenc.returncode != 0:
                        raise RuntimeError("snapshot key encryption failed: " + keyenc.stderr[-1000:])

                    result.update(
                        ok=True,
                        returncode=0,
                        package=package,
                        component=component,
                        target_title=target_title,
                        evidence="encrypted_visible_whatsapp_snapshot",
                        encrypted_bundle=str(enc_bundle.relative_to(REPO)),
                        encrypted_key=str(enc_key.relative_to(REPO)),
                        plaintext_published=False,
                    )

                    for p in (local_xml, local_png, local_tar, local_pub):
                        try:
                            p.unlink()
                        except FileNotFoundError:
                            pass
                else:
                    result.update(
                        ok=True,
                        returncode=0,
                        package=package,
                        component=component,
                        target_title=target_title,
                        evidence="local_visible_whatsapp_snapshot",
                        local_snapshot_dir=str(private_dir),
                        local_xml=str(local_xml),
                        local_png=str(local_png),
                        plaintext_published=False,
                        note="Private evidence kept on phone because no return_public_key_pem was supplied.",
                    )

        elif action == "android_whatsapp_read_unread_summary":
            package = "com.whatsapp"
            component = "com.whatsapp/.home.ui.HomeActivity"
            tmp1 = "/data/local/tmp/tomo_wa_unread_home.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1}; }}
trap cleanup EXIT

am force-stop {package} >/dev/null 2>&1 || true
sleep 0.5
am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

echo UNREAD_SUMMARY_BEGIN
grep -o '<node[^>]*>' {tmp1} | grep -E 'resource-id="com.whatsapp:id/(conversations_row_contact_name|conversations_row_message_count|single_msg_tv|conversations_row_date)"' || true
echo UNREAD_SUMMARY_END
echo UNREAD_SUMMARY_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""
            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO, text=True, capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "UNREAD_SUMMARY_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                stdout=r.stdout[-12000:],
                stderr=r.stderr[-12000:],
            )

        elif action == "android_guarded_whatsapp_scroll_draft_and_send":
            package = "com.whatsapp"
            component = "com.whatsapp/.home.ui.HomeActivity"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if not target_title or len(target_title) > 120:
                raise ValueError("target_title is required")
            if not text_value or len(text_value) > 256:
                raise ValueError("text must be 1-256 characters")
            if any(ord(ch) < 32 for ch in target_title + text_value):
                raise ValueError("text contains control characters")

            encoded_text = text_value.replace(" ", "%s")
            tmp1 = "/data/local/tmp/tomo_wa_scroll_ds_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_scroll_ds_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_scroll_ds_draft.xml"
            tmp4 = "/data/local/tmp/tomo_wa_scroll_ds_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3} {tmp4}; }}
trap cleanup EXIT

am force-stop {package} >/dev/null 2>&1 || true
sleep 0.5
am start -n {component} >/dev/null
sleep 1

result_node=""
for pass in 1 2 3 4 5 6 7 8 9 10 11 12; do
  uiautomator dump {tmp1} >/dev/null
  result_node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
  count="$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)"
  if [ "$count" -eq 1 ]; then
    break
  fi
  input swipe 360 1280 360 650 350
  sleep 0.7
done

[ "$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_MAIN_LIST_MATCH_AFTER_FULL_SCAN; exit 251; }}

bounds="$(printf '%s' "$result_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_MAIN_LIST_BOUNDS; exit 252; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 253; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_ENTRY_MATCH; exit 254; }}

existing="$(printf '%s' "$entry" | sed -n 's/.* text="\\([^"]*\\)".*/\\1/p')"
if [ "$existing" = "{text_value}" ]; then
  echo EXISTING_DRAFT_ALREADY_MATCHES
else
  [ -z "$existing" ] || [ "$existing" = "Message" ] || {{ echo ABORT_DIFFERENT_EXISTING_DRAFT; exit 255; }}

  bounds="$(printf '%s' "$entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
  set -- $bounds
  [ "$#" -eq 4 ] || {{ echo ABORT_ENTRY_BOUNDS; exit 256; }}
  input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
  input text "{encoded_text}"
fi

uiautomator dump {tmp3} >/dev/null
new_entry="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$new_entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_NOT_VERIFIED; exit 257; }}

send_node="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'resource-id="com.whatsapp:id/send"' || true)"
[ "$(printf '%s\n' "$send_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEND_BUTTON_MATCH; exit 258; }}

bounds="$(printf '%s' "$send_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEND_BOUNDS; exit 259; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp4} >/dev/null
grep -F 'resource-id="com.whatsapp:id/entry"' {tmp4} | grep -F 'text="Message"' >/dev/null || {{ echo ABORT_ENTRY_NOT_CLEARED; exit 260; }}
grep -F 'text="{text_value}"' {tmp4} >/dev/null || {{ echo ABORT_SENT_TEXT_NOT_VISIBLE; exit 261; }}
echo SCROLL_DRAFT_SEND_VERIFIED
cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""
            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO, text=True, capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SCROLL_DRAFT_SEND_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_scroll_draft":
            package = "com.whatsapp"
            component = "com.whatsapp/.home.ui.HomeActivity"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if not target_title or len(target_title) > 120:
                raise ValueError("target_title is required")
            if not text_value or len(text_value) > 256:
                raise ValueError("text must be 1-256 characters")
            if any(ord(ch) < 32 for ch in target_title + text_value):
                raise ValueError("text contains control characters")

            encoded_text = text_value.replace(" ", "%s")
            tmp1 = "/data/local/tmp/tomo_wa_scroll_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_scroll_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_scroll_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am force-stop {package} >/dev/null 2>&1 || true
sleep 0.5
am start -n {component} >/dev/null
sleep 1

result_node=""

# A force-stopped fresh WhatsApp launch returns to the top of Chats on this device.
# Scan deterministically downward from that known starting point.
for pass in 1 2 3 4 5 6 7 8 9 10 11 12; do
  uiautomator dump {tmp1} >/dev/null
  result_node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
  count="$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)"
  if [ "$count" -eq 1 ]; then
    break
  fi
  # Finger swipe UP reveals chats farther down the list.
  input swipe 360 1280 360 650 350
  sleep 0.7
done

[ "$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_MAIN_LIST_MATCH_AFTER_FULL_SCAN; exit 211; }}

bounds="$(printf '%s' "$result_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_MAIN_LIST_BOUNDS; exit 212; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 213; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_ENTRY_MATCH; exit 214; }}

existing="$(printf '%s' "$entry" | sed -n 's/.* text="\\([^"]*\\)".*/\\1/p')"

if [ "$existing" = "{text_value}" ]; then
  echo EXISTING_DRAFT_ALREADY_MATCHES
else
  [ -z "$existing" ] || [ "$existing" = "Message" ] || {{ echo ABORT_DIFFERENT_EXISTING_DRAFT; exit 215; }}

  bounds="$(printf '%s' "$entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
  set -- $bounds
  [ "$#" -eq 4 ] || {{ echo ABORT_ENTRY_BOUNDS; exit 216; }}
  input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
  input text "{encoded_text}"
fi

uiautomator dump {tmp3} >/dev/null
new_entry="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$new_entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_NOT_VERIFIED; exit 217; }}
echo SCROLL_DRAFT_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SCROLL_DRAFT_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_search_draft":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if not target_title or len(target_title) > 120:
                raise ValueError("target_title is required")
            if not text_value or len(text_value) > 256:
                raise ValueError("text must be 1-256 characters")
            if any(ord(ch) < 32 for ch in target_title + text_value):
                raise ValueError("text contains control characters")

            search_text = target_title.replace(" ", "%s")
            encoded_text = text_value.replace(" ", "%s")

            tmp1 = "/data/local/tmp/tomo_wa_search_draft_home.xml"
            tmp2 = "/data/local/tmp/tomo_wa_search_draft_box.xml"
            tmp3 = "/data/local/tmp/tomo_wa_search_draft_results.xml"
            tmp4 = "/data/local/tmp/tomo_wa_search_draft_chat.xml"
            tmp5 = "/data/local/tmp/tomo_wa_search_draft_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3} {tmp4} {tmp5}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

search_node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/search_bar_inner_layout"' || true)"
[ "$(printf '%s\n' "$search_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEARCH_BAR_MATCH; exit 181; }}

bounds="$(printf '%s' "$search_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEARCH_BAR_BOUNDS; exit 182; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
search_entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | head -n 1 || true)"
[ -n "$search_entry" ] || {{ echo ABORT_NO_SEARCH_EDITTEXT; exit 183; }}

bounds="$(printf '%s' "$search_entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEARCH_ENTRY_BOUNDS; exit 184; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
input text "{search_text}"
sleep 1

uiautomator dump {tmp3} >/dev/null
# WhatsApp search may repeat the same name in Chats, Groups in common, and Messages.
# Use a tiny bounded scroll hand: inspect, swipe up, inspect again, max 6 passes.
result_node=""
for pass in 1 2 3 4 5 6; do
  uiautomator dump {tmp3} >/dev/null

  chats_top="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'resource-id="com.whatsapp:id/title"' | grep -F 'text="Chats"' | sed -n 's/.*bounds="\\[[0-9]*,\\([0-9]*\\)\\]\\[[0-9]*,\\([0-9]*\\)\\]".*/\\2/p' | head -n 1)"
  next_top="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'resource-id="com.whatsapp:id/title"' | grep -E 'text="(Groups in common|Messages)"' | sed -n 's/.*bounds="\\[[0-9]*,\\([0-9]*\\)\\]\\[[0-9]*,\\([0-9]*\\)\\]".*/\\1/p' | head -n 1)"
  [ -n "$next_top" ] || next_top=1600

  if [ -n "$chats_top" ]; then
    result_node=""
    while IFS= read -r n; do
      [ -n "$n" ] || continue
      y1="$(printf '%s' "$n" | sed -n 's/.*bounds="\\[[0-9]*,\\([0-9]*\\)\\]\\[[0-9]*,[0-9]*\\]".*/\\1/p')"
      [ -n "$y1" ] || continue
      if [ "$y1" -ge "$chats_top" ] && [ "$y1" -lt "$next_top" ]; then
        result_node="$result_node$n
"
      fi
    done <<'EOF'
$(grep -o '<node[^>]*>' {tmp3} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)
EOF
    if [ "$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)" -eq 1 ]; then
      break
    fi
  fi

  # Scroll search results upward to reveal lower sections/rows.
  input swipe 360 1260 360 620 350
  sleep 1
done

[ "$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_CHATS_RESULT_MATCH_AFTER_SCROLL; exit 185; }}

bounds="$(printf '%s' "$result_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEARCH_RESULT_BOUNDS; exit 186; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp4} >/dev/null
grep -o '<node[^>]*>' {tmp4} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 187; }}

entry="$(grep -o '<node[^>]*>' {tmp4} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_ENTRY_MATCH; exit 188; }}

bounds="$(printf '%s' "$entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_ENTRY_BOUNDS; exit 189; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"

# Draft-only requires an empty entry to avoid overwriting an existing human draft.
existing="$(printf '%s' "$entry" | sed -n 's/.* text="\\([^"]*\\)".*/\\1/p')"
[ -z "$existing" ] || [ "$existing" = "Message" ] || {{ echo ABORT_EXISTING_DRAFT; exit 190; }}

input text "{encoded_text}"

uiautomator dump {tmp5} >/dev/null
new_entry="$(grep -o '<node[^>]*>' {tmp5} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$new_entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_NOT_VERIFIED; exit 191; }}
echo SEARCH_DRAFT_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SEARCH_DRAFT_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_search_replace_and_send":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            expected_before = str(cmd.get("expected_before", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if target_title != "Mum (Julianne)":
                raise ValueError("search replace-and-send proof is currently locked to Mum (Julianne)")
            if expected_before != "HELLO FROM TOMO":
                raise ValueError("unexpected existing draft")
            if text_value != "Hello":
                raise ValueError("unexpected send text")

            search_text = target_title.replace(" ", "%s")
            encoded_text = text_value.replace(" ", "%s")
            deletes = " ".join(["input keyevent KEYCODE_DEL;" for _ in expected_before])

            tmp1 = "/data/local/tmp/tomo_wa_search_home.xml"
            tmp2 = "/data/local/tmp/tomo_wa_search_box.xml"
            tmp3 = "/data/local/tmp/tomo_wa_search_results.xml"
            tmp4 = "/data/local/tmp/tomo_wa_search_chat.xml"
            tmp5 = "/data/local/tmp/tomo_wa_search_draft.xml"
            tmp6 = "/data/local/tmp/tomo_wa_search_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3} {tmp4} {tmp5} {tmp6}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

search_node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/search_bar_inner_layout"' || true)"
[ "$(printf '%s\n' "$search_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEARCH_BAR_MATCH; exit 161; }}

bounds="$(printf '%s' "$search_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEARCH_BAR_BOUNDS; exit 162; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
search_entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | head -n 1 || true)"
[ -n "$search_entry" ] || {{ echo ABORT_NO_SEARCH_EDITTEXT; exit 163; }}

bounds="$(printf '%s' "$search_entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEARCH_ENTRY_BOUNDS; exit 164; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
input text "{search_text}"
sleep 1

uiautomator dump {tmp3} >/dev/null
result_node="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
[ "$(printf '%s\n' "$result_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEARCH_RESULT_MATCH; exit 165; }}

bounds="$(printf '%s' "$result_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEARCH_RESULT_BOUNDS; exit 166; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp4} >/dev/null
grep -o '<node[^>]*>' {tmp4} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 167; }}

entry="$(grep -o '<node[^>]*>' {tmp4} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{expected_before}"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_EXPECTED_DRAFT_NOT_FOUND; exit 168; }}

bounds="$(printf '%s' "$entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_ENTRY_BOUNDS; exit 169; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
input keyevent KEYCODE_MOVE_END
{deletes}
input text "{encoded_text}"

uiautomator dump {tmp5} >/dev/null
new_entry="$(grep -o '<node[^>]*>' {tmp5} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$new_entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_REPLACEMENT_NOT_VERIFIED; exit 170; }}

send_node="$(grep -o '<node[^>]*>' {tmp5} | grep -F 'resource-id="com.whatsapp:id/send"' || true)"
[ "$(printf '%s\n' "$send_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEND_BUTTON_MATCH; exit 171; }}

bounds="$(printf '%s' "$send_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEND_BOUNDS; exit 172; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp6} >/dev/null
grep -F 'resource-id="com.whatsapp:id/entry"' {tmp6} | grep -F 'text="Message"' >/dev/null || {{ echo ABORT_ENTRY_NOT_CLEARED; exit 173; }}
grep -F 'text="{text_value}"' {tmp6} >/dev/null || {{ echo ABORT_SENT_TEXT_NOT_VISIBLE; exit 174; }}
echo SEARCH_REPLACE_SEND_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SEARCH_REPLACE_SEND_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                expected_before=expected_before,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_replace_and_send":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            expected_before = str(cmd.get("expected_before", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if not target_title or len(target_title) > 120:
                raise ValueError("target_title is required")
            if not expected_before or len(expected_before) > 256:
                raise ValueError("expected_before is required")
            if not text_value or len(text_value) > 256:
                raise ValueError("text must be 1-256 characters")
            if any(ord(ch) < 32 for ch in expected_before + text_value):
                raise ValueError("text contains control characters")

            encoded_text = text_value.replace(" ", "%s")
            deletes = " ".join(["input keyevent KEYCODE_DEL;" for _ in expected_before])
            tmp1 = "/data/local/tmp/tomo_wa_replace_send_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_replace_send_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_replace_send_draft.xml"
            tmp4 = "/data/local/tmp/tomo_wa_replace_send_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3} {tmp4}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
[ "$(printf '%s\n' "$node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_CHAT_MATCH; exit 151; }}

bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_CHAT_BAD_BOUNDS; exit 152; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 153; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{expected_before}"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_EXPECTED_DRAFT_NOT_FOUND; exit 154; }}

bounds="$(printf '%s' "$entry" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_ENTRY_BAD_BOUNDS; exit 155; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
input keyevent KEYCODE_MOVE_END
{deletes}
input text "{encoded_text}"

uiautomator dump {tmp3} >/dev/null
new_entry="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$new_entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_REPLACEMENT_NOT_VERIFIED; exit 156; }}

send_node="$(grep -o '<node[^>]*>' {tmp3} | grep -F 'resource-id="com.whatsapp:id/send"' || true)"
[ "$(printf '%s\n' "$send_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEND_BUTTON_MATCH; exit 157; }}

bounds="$(printf '%s' "$send_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEND_BAD_BOUNDS; exit 158; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp4} >/dev/null
grep -F 'resource-id="com.whatsapp:id/entry"' {tmp4} | grep -F 'text="Message"' >/dev/null || {{ echo ABORT_ENTRY_NOT_CLEARED; exit 159; }}
grep -F 'text="{text_value}"' {tmp4} >/dev/null || {{ echo ABORT_SENT_TEXT_NOT_VISIBLE; exit 160; }}
echo REPLACE_SEND_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "REPLACE_SEND_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                expected_before=expected_before,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_current_chat_send":
            package = "com.whatsapp"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()
            if not target_title or not text_value:
                raise ValueError("target_title and text are required")

            tmp1 = "/data/local/tmp/tomo_wa_current_send_before.xml"
            tmp2 = "/data/local/tmp/tomo_wa_current_send_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2}; }}
trap cleanup EXIT

uiautomator dump {tmp1} >/dev/null

grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 231; }}

entry="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_TEXT_NOT_VERIFIED; exit 232; }}

send_node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/send"' || true)"
[ "$(printf '%s\\n' "$send_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEND_BUTTON_MATCH; exit 233; }}

bounds="$(printf '%s' "$send_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEND_BOUNDS; exit 234; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
grep -F 'resource-id="com.whatsapp:id/entry"' {tmp2} | grep -F 'text="Message"' >/dev/null || {{ echo ABORT_ENTRY_NOT_CLEARED; exit 235; }}
grep -F 'text="{text_value}"' {tmp2} >/dev/null || {{ echo ABORT_SENT_TEXT_NOT_VISIBLE; exit 236; }}
echo CURRENT_CHAT_SEND_VERIFIED
cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""
            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO, text=True, capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "CURRENT_CHAT_SEND_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode, package=package,
                target_title=target_title, text=text_value,
                stdout=r.stdout[-8000:], stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_send_text":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if not target_title or len(target_title) > 120:
                raise ValueError("android_guarded_whatsapp_send_text requires a target_title")
            if not text_value or len(text_value) > 256:
                raise ValueError("text must be 1-256 characters")
            if any(ord(ch) < 32 for ch in text_value):
                raise ValueError("text contains control characters")

            tmp1 = "/data/local/tmp/tomo_wa_send_generic_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_send_generic_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_send_generic_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
[ "$(printf '%s\n' "$node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_CHAT_MATCH; exit 141; }}

bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_CHAT_BAD_BOUNDS; exit 142; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_CHAT; exit 143; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_TEXT_NOT_VERIFIED; exit 144; }}

send_node="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/send"' || true)"
[ "$(printf '%s\n' "$send_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEND_BUTTON_MATCH; exit 145; }}

bounds="$(printf '%s' "$send_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEND_BAD_BOUNDS; exit 146; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp3} >/dev/null
grep -F 'resource-id="com.whatsapp:id/entry"' {tmp3} | grep -F 'text="Message"' >/dev/null || {{ echo ABORT_ENTRY_NOT_CLEARED; exit 147; }}
grep -F 'text="{text_value}"' {tmp3} >/dev/null || {{ echo ABORT_SENT_TEXT_NOT_VISIBLE; exit 148; }}
echo SEND_TEXT_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SEND_TEXT_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_self_send_text":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if target_title != "+64 20 449 8229 (You)":
                raise ValueError("android_guarded_whatsapp_self_send_text is restricted to the verified self-chat")
            if not text_value or len(text_value) > 256:
                raise ValueError("text must be 1-256 characters")
            if any(ord(ch) < 32 for ch in text_value):
                raise ValueError("text contains control characters")

            tmp1 = "/data/local/tmp/tomo_wa_send_text_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_send_text_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_send_text_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
[ "$(printf '%s\n' "$node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SELF_CHAT_MATCH; exit 131; }}

bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SELF_CHAT_BAD_BOUNDS; exit 132; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp2} >/dev/null
grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' >/dev/null || {{ echo ABORT_WRONG_SELF_CHAT; exit 133; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_TEXT_NOT_VERIFIED; exit 134; }}

send_node="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/send"' || true)"
[ "$(printf '%s\n' "$send_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEND_BUTTON_MATCH; exit 135; }}

bounds="$(printf '%s' "$send_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEND_BAD_BOUNDS; exit 136; }}
input tap "$(( ($1 + $3) / 2 ))" "$(( ($2 + $4) / 2 ))"
sleep 1

uiautomator dump {tmp3} >/dev/null
grep -F 'resource-id="com.whatsapp:id/entry"' {tmp3} | grep -F 'text="Message"' >/dev/null || {{ echo ABORT_ENTRY_NOT_CLEARED; exit 137; }}
grep -F 'text="{text_value}"' {tmp3} >/dev/null || {{ echo ABORT_SENT_TEXT_NOT_VISIBLE; exit 138; }}
echo SEND_TEXT_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SEND_TEXT_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_whatsapp_self_send":
            package = "com.whatsapp"
            component = "com.whatsapp/.Main"
            target_title = str(cmd.get("target_title", "")).strip()
            text_value = str(cmd.get("text", "")).strip()

            if target_title != "+64 20 449 8229 (You)":
                raise ValueError("android_guarded_whatsapp_self_send is restricted to the verified self-chat")
            if text_value != "TOMO TEST":
                raise ValueError("android_guarded_whatsapp_self_send currently allows only TOMO TEST")

            tmp1 = "/data/local/tmp/tomo_wa_send_list.xml"
            tmp2 = "/data/local/tmp/tomo_wa_send_chat.xml"
            tmp3 = "/data/local/tmp/tomo_wa_send_after.xml"

            shell = f"""
set -e
cleanup() {{ rm -f {tmp1} {tmp2} {tmp3}; }}
trap cleanup EXIT

am start -n {component} >/dev/null
sleep 1
uiautomator dump {tmp1} >/dev/null

node="$(grep -o '<node[^>]*>' {tmp1} | grep -F 'resource-id="com.whatsapp:id/conversations_row_contact_name"' | grep -F 'text="{target_title}"' || true)"
count="$(printf '%s\n' "$node" | sed '/^$/d' | wc -l)"
[ "$count" -eq 1 ] || {{ echo ABORT_SELF_CHAT_MATCH_COUNT_"$count"; exit 101; }}

bounds="$(printf '%s' "$node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SELF_CHAT_BAD_BOUNDS; exit 102; }}
x=$(( ($1 + $3) / 2 ))
y=$(( ($2 + $4) / 2 ))
input tap "$x" "$y"
sleep 1

uiautomator dump {tmp2} >/dev/null
title_node="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/conversation_contact_name"' | grep -F 'text="{target_title}"' || true)"
[ "$(printf '%s\n' "$title_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_WRONG_SELF_CHAT_TITLE; exit 103; }}

entry="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'class="android.widget.EditText"' | grep -F 'resource-id="com.whatsapp:id/entry"' | grep -F 'text="{text_value}"' || true)"
[ "$(printf '%s\n' "$entry" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_DRAFT_NOT_PRESENT; exit 104; }}

send_node="$(grep -o '<node[^>]*>' {tmp2} | grep -F 'resource-id="com.whatsapp:id/send"' || true)"
[ "$(printf '%s\n' "$send_node" | sed '/^$/d' | wc -l)" -eq 1 ] || {{ echo ABORT_SEND_BUTTON_MATCH_COUNT; exit 105; }}

bounds="$(printf '%s' "$send_node" | sed -n 's/.*bounds="\\[\\([0-9]*\\),\\([0-9]*\\)\\]\\[\\([0-9]*\\),\\([0-9]*\\)\\]".*/\\1 \\2 \\3 \\4/p')"
set -- $bounds
[ "$#" -eq 4 ] || {{ echo ABORT_SEND_BAD_BOUNDS; exit 106; }}
x=$(( ($1 + $3) / 2 ))
y=$(( ($2 + $4) / 2 ))
input tap "$x" "$y"
sleep 1

uiautomator dump {tmp3} >/dev/null
grep -F 'resource-id="com.whatsapp:id/entry"' {tmp3} | grep -F 'text="Message"' >/dev/null || {{ echo ABORT_ENTRY_NOT_CLEARED; exit 107; }}
grep -F 'text="{text_value}"' {tmp3} >/dev/null || {{ echo ABORT_SENT_TEXT_NOT_VISIBLE; exit 108; }}
echo SEND_VERIFIED

cleanup
trap - EXIT
echo CLEANUP_VERIFIED
"""

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 45)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "SEND_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                package=package,
                component=component,
                target_title=target_title,
                text=text_value,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "android_guarded_markor_cycle":
            text_value = str(cmd.get("text", "")).strip()
            expected_before = str(cmd.get("expected_before", "")).strip()
            expected_after = str(cmd.get("expected_after", "")).strip()
            test_path = str(cmd.get("test_path", "/sdcard/Documents/TOMO_FINGERS_TEST.md")).strip()

            if test_path != "/sdcard/Documents/TOMO_FINGERS_TEST.md":
                raise ValueError("only the disposable Markor test path is allowed")
            if expected_before != "BASELINE" or expected_after != "BASELINETOMO_TEST" or text_value != "TOMO_TEST":
                raise ValueError("unexpected guarded Markor test payload")

            tmp1 = "/sdcard/tomo_markor_fast_before.xml"
            tmp2 = "/sdcard/tomo_markor_fast_after.xml"
            tmp3 = "/sdcard/tomo_markor_fast_restore.xml"
            deletes = " ".join(["input keyevent KEYCODE_DEL;" for _ in text_value])

            shell = f'''
set -e
rm -f {test_path} {tmp1} {tmp2} {tmp3}
printf BASELINE > {test_path}
am start -a android.intent.action.VIEW -d file://{test_path} -t text/markdown -p net.gsantner.markor >/dev/null
sleep 1
focus="$(dumpsys window | grep mCurrentFocus | head -n 1)"
case "$focus" in *"net.gsantner.markor/"*) ;; *) echo ABORT_WRONG_FOREGROUND_OPEN; rm -f {test_path}; exit 51;; esac

uiautomator dump {tmp1} >/dev/null
grep -F 'package="net.gsantner.markor"' {tmp1} >/dev/null
grep -F 'class="android.widget.EditText"' {tmp1} >/dev/null
grep -F 'text="{expected_before}"' {tmp1} >/dev/null

input tap 360 300
focus="$(dumpsys window | grep mCurrentFocus | head -n 1)"
case "$focus" in *"net.gsantner.markor/"*) ;; *) echo ABORT_WRONG_FOREGROUND_TAP; rm -f {test_path} {tmp1}; exit 52;; esac

input keyevent KEYCODE_MOVE_END
input text {text_value}

uiautomator dump {tmp2} >/dev/null
grep -F 'package="net.gsantner.markor"' {tmp2} >/dev/null
grep -F 'text="{expected_after}"' {tmp2} >/dev/null
echo APPEND_VERIFIED

{deletes}

uiautomator dump {tmp3} >/dev/null
grep -F 'package="net.gsantner.markor"' {tmp3} >/dev/null
grep -F 'text="{expected_before}"' {tmp3} >/dev/null
[ "$(cat {test_path})" = "{expected_before}" ]
echo RESTORE_VERIFIED

rm -f {test_path} {tmp1} {tmp2} {tmp3}
echo CLEANUP_VERIFIED
'''

            r = subprocess.run(
                [str(Path.home() / "bin" / "rish"), "-c", shell],
                cwd=REPO,
                text=True,
                capture_output=True,
                timeout=int(cmd.get("timeout", 60)),
            )
            proof_output = (r.stdout or "") + "\n" + (r.stderr or "")
            result.update(
                ok=(r.returncode == 0 and "APPEND_VERIFIED" in proof_output and "RESTORE_VERIFIED" in proof_output and "CLEANUP_VERIFIED" in proof_output),
                returncode=r.returncode,
                stdout=r.stdout[-8000:],
                stderr=r.stderr[-8000:],
            )

        elif action == "repo_status":
            r = git("status", "--short")
            result.update(ok=True, stdout=r.stdout, stderr=r.stderr)
        else:
            raise ValueError(f"action not allowed: {action}")
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"

    write_result(cmd_id, result)
    archive_command(path)
    git("add", "-A", "tomo_bridge/inbox_v2", "tomo_bridge/outbox_v2", "tomo_bridge/archive_v2", check=False)
    git("commit", "-m", f"Termux v2 result: {cmd_id}", check=False)

    # The repo is shared with cloud workers, so main can advance while a phone job
    # is running. Publish the result robustly instead of silently losing a rejected push.
    published = False
    last_error = ""
    for attempt in range(3):
        push = git("push", "origin", "main", check=False)
        if push.returncode == 0:
            published = True
            break
        last_error = (push.stderr or push.stdout or "").strip()
        git("fetch", "origin", "main", check=False)
        rebase = git("rebase", "origin/main", check=False)
        if rebase.returncode != 0:
            git("rebase", "--abort", check=False)
            last_error = (rebase.stderr or rebase.stdout or last_error).strip()
            break

    if not published:
        print(f"result publish pending for {cmd_id}: {last_error}")

def push_wake_loop(wake_event):
    while True:
        try:
            req = urllib.request.Request(WAKE_URL, headers={"User-Agent": "Three-Amigos-Termux-Bridge-v2/1.0"})
            with urllib.request.urlopen(req, timeout=90) as response:
                for raw in response:
                    try:
                        msg = json.loads(raw.decode("utf-8", "replace"))
                    except Exception:
                        continue
                    if msg.get("event") == "message":
                        wake_event.set()
        except Exception as e:
            print("push wake reconnect:", e)
            time.sleep(3)

def main():
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(parents=True, exist_ok=True)
    print("TOMO BRIDGE V2 — TERMUX LISTENER")
    print(f"Repo: {REPO}")
    print(f"Push wake: {WAKE_TOPIC}")
    print(f"Fallback poll every {POLL_SECONDS}s")
    print("Actions: git_sync, run_repo_python, codex_exec, android_launch, android_guarded_text_cycle, android_guarded_open_text_cycle, android_guarded_find_edittext_cycle, android_guarded_find_edittext_submit, android_guarded_whatsapp_self_draft, android_guarded_whatsapp_draft, android_guarded_whatsapp_self_repair_draft, android_whatsapp_search_inspect, android_whatsapp_notification_summary, android_whatsapp_notification_inspect, android_whatsapp_message_snapshot, android_whatsapp_read_unread_summary, android_guarded_whatsapp_scroll_draft_and_send, android_guarded_whatsapp_scroll_send, android_guarded_whatsapp_scroll_draft, android_guarded_whatsapp_search_draft, android_guarded_whatsapp_search_replace_and_send, android_guarded_whatsapp_replace_and_send, android_guarded_whatsapp_current_chat_send, android_guarded_whatsapp_send_text, android_guarded_whatsapp_self_send_text, android_guarded_whatsapp_self_send, android_guarded_markor_cycle, repo_status")
    wake_event = threading.Event()
    threading.Thread(target=push_wake_loop, args=(wake_event,), daemon=True).start()
    while True:
        try:
            git("pull", "--ff-only", "origin", "main", check=False)
            for path in sorted(INBOX.glob("*.command.json")):
                process(path)
        except Exception as e:
            print("listener error:", e)
        wake_event.wait(timeout=POLL_SECONDS)
        wake_event.clear()

if __name__ == "__main__":
    main()
