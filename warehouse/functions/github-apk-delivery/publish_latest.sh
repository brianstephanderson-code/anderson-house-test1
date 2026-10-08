#!/usr/bin/env bash
set -euo pipefail

APK_PATH="${1:?APK path required}"
ASSET_NAME="${2:?asset name required}"
RELEASE_TAG="${3:?release tag required}"
RELEASE_TITLE="${4:-$RELEASE_TAG}"

if [[ ! -f "$APK_PATH" ]]; then
  echo "APK not found: $APK_PATH" >&2
  exit 2
fi

: "${GH_TOKEN:?GH_TOKEN must be set}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY must be set}"
: "${GITHUB_SHA:?GITHUB_SHA must be set}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cp "$APK_PATH" "$TMP_DIR/$ASSET_NAME"
(
  cd "$TMP_DIR"
  sha256sum "$ASSET_NAME" > "$ASSET_NAME.sha256"
)

if gh release view "$RELEASE_TAG" --repo "$GITHUB_REPOSITORY" >/dev/null 2>&1; then
  gh release upload "$RELEASE_TAG"     "$TMP_DIR/$ASSET_NAME"     "$TMP_DIR/$ASSET_NAME.sha256"     --clobber     --repo "$GITHUB_REPOSITORY"
else
  gh release create "$RELEASE_TAG"     "$TMP_DIR/$ASSET_NAME"     "$TMP_DIR/$ASSET_NAME.sha256"     --target "$GITHUB_SHA"     --title "$RELEASE_TITLE"     --notes "Warehouse APK delivery. Built from commit $GITHUB_SHA. The APK and SHA-256 checksum are replaced automatically by each approved signed build."     --repo "$GITHUB_REPOSITORY"
fi

echo "APK_DOWNLOAD=https://github.com/$GITHUB_REPOSITORY/releases/download/$RELEASE_TAG/$ASSET_NAME"
