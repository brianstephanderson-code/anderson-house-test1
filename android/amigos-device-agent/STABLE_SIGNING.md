# Three Amigos Device Agent — Stable Signing

Status: pipeline prepared; private signing material still required.

## Why this exists

GitHub's temporary debug signing keys can change between fresh runners.
Android will then reject an APK update even when the package name is unchanged.

The permanent path is the signed release workflow:

`.github/workflows/amigos-device-agent-release.yml`

## Required GitHub Actions secrets

Create these repository secrets. Never commit their values to this public repository.

- `AMIGOS_KEYSTORE_B64`
- `AMIGOS_KEYSTORE_PASSWORD`
- `AMIGOS_KEY_ALIAS`
- `AMIGOS_KEY_PASSWORD`

`AMIGOS_KEYSTORE_B64` is the base64 encoding of the permanent private JKS keystore.

## Migration rule

The currently installed debug-signed app cannot be updated in-place by the first
permanently signed release unless both happen to use the same signing key.

Therefore the migration is one final uninstall/install:

1. Create and protect the permanent signing key.
2. Add the four private repository secrets.
3. Run **Release Three Amigos Device Agent**.
4. Download `three-amigos-device-agent-signed`.
5. Uninstall the current debug-signed app.
6. Install the signed release and re-enable Accessibility + Notification Access.

After that migration, future signed releases install normally over the existing app,
provided the same keystore remains available.

## Security rule

The private keystore and passwords must never be committed to this repository,
placed in the public bridge inbox/outbox, or written into public workflow logs.
