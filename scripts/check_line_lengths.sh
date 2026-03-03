#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-flutter_app}"

if ! command -v rg >/dev/null 2>&1; then
  echo "rg (ripgrep) is required." >&2
  exit 1
fi

rg --files "$ROOT_DIR" \
  | rg -v "^${ROOT_DIR}/assets/" \
  | rg -v "^${ROOT_DIR}/pubspec.lock$" \
  | rg -v "^${ROOT_DIR}/ios/Runner.xcodeproj/project.pbxproj$" \
  | rg -v "^${ROOT_DIR}/macos/Runner.xcodeproj/project.pbxproj$" \
  | xargs wc -l \
  | awk '$2 != "total" && $1 > 400 {print $1, $2; found=1} END{exit found?1:0}'
