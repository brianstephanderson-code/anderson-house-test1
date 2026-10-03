# Android Codex + Termux + Shizuku Field Guide

Status: working proof of concept on Android 11, non-root.

## Goal

Run OpenAI Codex locally in Termux, authenticate with ChatGPT, execute Termux shell commands, and bridge from Termux into Android shell through Shizuku/rish.

Final proven chain:

```
Codex -> Termux -> rish -> Shizuku -> Android shell
```

Verified Android shell identity:

```
uid=2000(shell)
```

## Important safety boundary

This is **not root**. Shizuku/rish provides Android shell-level access.

Codex had to be launched with:

```sh
codex-termux --no-daemon -s danger-full-access
```

`danger-full-access` disables Codex's normal local command sandbox. Keep normal approval prompts enabled and use read-only tests first. Do not use the separate `--dangerously-bypass-approvals-and-sandbox` flag unless there is a compelling, controlled reason.

## Working components

- Android 11
- Termux
- Shizuku 13.5 started via Wireless debugging
- rish exported from Shizuku
- Codex CLI 0.160.0
- pnpm 11.8.0
- proot
- termux-codex-login community wrapper

## Shizuku / rish setup

In Shizuku:

1. Enable Wireless debugging.
2. Pair Shizuku with Android's six-digit pairing flow.
3. Start Shizuku.
4. Export terminal files into a shared folder such as:
   `Download/ShizukuBridge`

Files exported:

```
rish
rish_shizuku.dex
```

Termux path to shared folder:

```
~/storage/downloads/ShizukuBridge
```

Edit the launcher for Termux:

```sh
sed -i 's/PKG/com.termux/g' ~/storage/downloads/ShizukuBridge/rish
```

Copy into a stable Termux-local directory:

```sh
mkdir -p ~/bin
cp ~/storage/downloads/ShizukuBridge/rish ~/bin/rish
cp ~/storage/downloads/ShizukuBridge/rish_shizuku.dex ~/bin/rish_shizuku.dex
chmod +x ~/bin/rish
```

Verify:

```sh
~/bin/rish -c id
```

Expected:

```
uid=2000(shell)
```

## Codex installation on Termux

A normal npm install installed the JS launcher but skipped the Linux ARM64 optional package.

Install pnpm and use pnpm 11.8.0:

```sh
npm install -g pnpm@11.8.0
```

Create the pnpm architecture override:

```yaml
supportedArchitectures:
  os:
    - linux
  cpu:
    - arm64
```

Stored at:

```
~/.local/share/pnpm/global/v11/pnpm-workspace.yaml
```

Install Codex:

```sh
pnpm add -g @openai/codex@latest
```

The platform alias can be installed directly if needed:

```sh
pnpm add -g '@openai/codex-linux-arm64@npm:@openai/codex@0.160.0-linux-arm64'
```

Working pnpm Codex launcher:

```
~/.local/share/pnpm/bin/codex
```

Verify:

```sh
~/.local/share/pnpm/bin/codex --version
```

Expected:

```
codex-cli 0.160.0
```

## Codex login problem and fix

Symptoms on native Termux:

- browser OAuth callback returned to localhost but token exchange failed
- Device Code flow also failed
- IPv4 curl worked
- IPv6 curl failed

A purpose-built wrapper solved the Termux DNS / TLS mismatch:

```sh
npm install -g termux-codex-login
```

Ensure the working pnpm Codex appears first on PATH:

```sh
export PATH="$HOME/.local/share/pnpm/bin:$PATH"
```

Run:

```sh
termux-codex-login
```

Verify:

```sh
codex login status
```

Expected:

```
Logged in using ChatGPT
```

The wrapper creates its own resolver file under:

```
~/.termux-codex-login/resolv.conf
```

and runs Codex under proot with that file bound as `/etc/resolv.conf`, plus Termux's CA bundle via `SSL_CERT_FILE`.

## Daemon / bubblewrap issue

Launching Codex normally failed because the background app-server path expected bubblewrap.

Working launch mode:

```sh
codex-termux --no-daemon -s danger-full-access
```

This avoids the daemon and disables Codex's local bubblewrap sandbox while retaining the separate approval system.

## Final verification

Inside Codex:

```
Run pwd and tell me the current directory.
```

Succeeded.

Then:

```
Run ~/bin/rish -c 'id' and tell me the result.
```

Succeeded with:

```
uid=2000(shell)
```

This proves the complete chain:

```
Codex -> Termux shell -> rish -> Shizuku -> Android shell
```

## Operational notes

- Shizuku must be running before rish works.
- On a non-root Android device, Shizuku may need to be restarted after reboot or if its Wireless debugging session drops.
- If rish reports `Server is not running`, first check Shizuku itself.
- Keep the old GitHub/Termux polling bridge as a fallback path.
- Do not publish OAuth URLs, one-time codes, auth files, tokens, or device-specific network addresses.
- Before publishing this guide externally, re-test from a clean Termux session and replace version-specific commands with current stable versions where practical.

## Next phase: capability survey

Explore Android through harmless, read-only commands first and categorize results:

```
CAN READ -> CAN LAUNCH -> CAN CHANGE -> NEEDS USER -> BLOCKED
```

Candidate read-only probes:

- Android build/version
- battery state
- display state
- network state
- installed package list
- storage state
- running services/process summaries
- available system intents

Only after the read-only map is complete should write/change actions be tested.
