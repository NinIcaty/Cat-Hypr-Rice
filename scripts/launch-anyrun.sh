#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${PYPRLAND_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/pyprland}/anyrun"
DATA_DIR="${PYPRLAND_DATA_DIR:-/usr/share/pyprland-desktop}"

if command -v anyrun >/dev/null 2>&1; then
  exec anyrun --config-dir "$CONFIG_DIR"
fi

exec "$DATA_DIR/scripts/launch-rofi.sh"
