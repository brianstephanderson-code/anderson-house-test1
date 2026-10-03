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
    print("Actions: git_sync, run_repo_python, codex_exec, android_launch, android_guarded_text_cycle, android_guarded_open_text_cycle, android_guarded_find_edittext_cycle, android_guarded_find_edittext_submit, android_guarded_whatsapp_self_draft, android_guarded_whatsapp_self_send, android_guarded_markor_cycle, repo_status")
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
