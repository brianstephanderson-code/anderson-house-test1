# GitHub → APK Warehouse Function

Purpose: turn an approved, signed Android build into one stable APK download link.

Flow:

`GitHub source → build → signed APK → SHA-256 → GitHub Release asset → stable download URL`

The function is intentionally generic. A workflow calls `publish_latest.sh` with:

1. path to the APK produced by the build
2. public asset filename
3. fixed release tag
4. release title

On the first successful signed build it creates the release. On later builds it replaces the APK and checksum in place, so the download URL does not change.

Safety gate: production workflows should invoke this only for signed builds from an approved repository/branch. Debug builds should remain ordinary Actions artifacts and should not overwrite the stable public download.

This is a warehouse function: projects may reuse it without duplicating the publication logic.
