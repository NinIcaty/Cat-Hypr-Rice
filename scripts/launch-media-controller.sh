#!/usr/bin/env bash
set -euo pipefail

if ! command -v playerctl >/dev/null 2>&1; then
  notify-send "Media controller" "playerctl is not installed."
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$SCRIPT_DIR/media_controller.py"

if ! playerctl status >/dev/null 2>&1; then
  notify-send "Media controller" "No active media session."
  exit 0
fi

existing_pid="$(pgrep -f "$APP" | head -n1 || true)"

if [ -n "$existing_pid" ]; then
  kill "$existing_pid"
  exit 0
fi

exec python3 "$APP" >/dev/null 2>&1 &
