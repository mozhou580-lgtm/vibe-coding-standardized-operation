#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-codex}"
REPO_URL="https://github.com/mozhou580-lgtm/vibe-coding-standardized-operation.git"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/vibe-coding-install.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

if ! command -v git >/dev/null 2>&1; then
  echo "需要先安装 Git，或下载仓库 ZIP 后运行 install.sh。" >&2
  exit 1
fi

git clone --depth 1 "$REPO_URL" "$WORK_DIR/package" >/dev/null
bash "$WORK_DIR/package/install.sh" "$TARGET"
