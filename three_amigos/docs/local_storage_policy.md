# Local Storage Policy — Three Amigos

Canonical rule:

- Durable project work belongs in GitHub, not on the Android phone.
- The phone is an execution edge / bridge, not the warehouse.
- Local copies are disposable once their GitHub-backed source/result is verified.
- Keep only what is required for Termux, Codex, Shizuku/rish, the active repository checkout, and temporary runtime work.
- Prefer read-only inventory before deleting unknown user files.
- Automatic cleanup may remove caches, package archives, logs, and other clearly disposable build/runtime residue.
- Do not delete personal photos, messages, app data, or unknown user-created files automatically.
- Large local project artifacts should be committed/pushed to GitHub first, then removed locally when safe.

Working bridge:
Tomo -> GitHub -> Termux listener -> Codex/rish/Shizuku -> Android -> GitHub -> Tomo
