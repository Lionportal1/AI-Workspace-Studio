#!/usr/bin/env bash
set -Eeuo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
for tier in minimal balanced max; do
 case "$tier" in minimal) count=20;; balanced) count=35;; max) count=50;; esac
 python3 "$ROOT/ai_workspace_portable.py" "$TMP/$tier workspace" --agent universal --preset "$tier" --offline --no-git >/dev/null
 actual=$(find "$TMP/$tier workspace/.agents/skills" -name SKILL.md | wc -l | tr -d ' ')
 [[ "$actual" = "$count" ]] || exit 1
done
python3 "$ROOT/ai_workspace_portable.py" "$TMP/preview" --dry-run --offline >/dev/null
[[ ! -e "$TMP/preview" ]]
bash "$ROOT/ai-workspace-setup.sh" "$TMP/unix" --offline --no-git --mcp none --preset minimal >/dev/null
[[ -f "$TMP/unix/AGENTS.md" ]]
echo 'CLI integration passed'
