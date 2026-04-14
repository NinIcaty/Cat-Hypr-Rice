#!/usr/bin/env bash
set -euo pipefail

CONFIG_ROOT="${XDG_CONFIG_HOME:-$HOME/.config}/hypr-material3"
CONFIG_FILE="$CONFIG_ROOT/swaync/config.json"
STYLE_FILE="$CONFIG_ROOT/swaync/style.css"

if pgrep -x swaync >/dev/null 2>&1; then
  pkill -x swaync
  sleep 0.2
fi

exec swaync --skip-system-css -c "$CONFIG_FILE" -s "$STYLE_FILE"
