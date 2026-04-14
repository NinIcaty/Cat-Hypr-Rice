#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HYPRCAT_CONFIG_DIR:-${PYPRLAND_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/hyprcat}}/anyrun"
DATA_DIR="${HYPRCAT_DATA_DIR:-${PYPRLAND_DATA_DIR:-/usr/share/hyprcat}}"

if command -v anyrun >/dev/null 2>&1; then
  exec anyrun --config-dir "$CONFIG_DIR"
fi

exec "$DATA_DIR/scripts/launch-rofi.sh"
