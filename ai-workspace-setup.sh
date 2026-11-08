#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec python3 "$SCRIPT_DIR/ai_workspace_portable.py" "$@"
