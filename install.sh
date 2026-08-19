#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-codex}"
STAMP="$(date +%Y%m%d-%H%M%S)"

case "$TARGET" in
  codex)
    TARGET_ROOT="${HOME}/.codex"
    ;;
  claude)
    TARGET_ROOT="${HOME}/.claude"
    ;;
  both)
    "${BASH_SOURCE[0]}" codex
    "${BASH_SOURCE[0]}" claude
    exit 0
    ;;
  *)
    echo "用法: $0 [codex|claude|both]" >&2
    exit 2
    ;;
esac

SKILL_ROOT="${TARGET_ROOT}/skills"
BACKUP_ROOT="${TARGET_ROOT}/backups/vibe-coding/skills"

for skill in prd-master design-master tdd-master; do
  source_dir="${PACKAGE_ROOT}/skills/${skill}"
  source_file="${source_dir}/SKILL.md"
  target_dir="${SKILL_ROOT}/${skill}"
  backup_dir="${BACKUP_ROOT}/${skill}/${STAMP}"

  if [[ ! -r "$source_file" ]]; then
    echo "源文件不可读，停止安装: $source_file" >&2
    exit 1
  fi

  mkdir -p "$SKILL_ROOT"
  if [[ -e "$target_dir" ]]; then
    mkdir -p "$backup_dir"
    mv "$target_dir" "$backup_dir/"
    echo "已备份: $target_dir -> $backup_dir"
  fi

  cp -R "$source_dir" "$target_dir"
  echo "已安装: $target_dir"
done

echo "安装完成。请重启当前工具，然后使用：开始 PRD"
