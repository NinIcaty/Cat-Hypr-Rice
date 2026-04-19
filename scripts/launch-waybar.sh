#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HYPRCAT_CONFIG_DIR:-${PYPRLAND_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/hyprcat}}/waybar"

if ! command -v waybar >/dev/null 2>&1; then
  exit 0
fi

pkill -x waybar >/dev/null 2>&1 || true
exec waybar --config "$CONFIG_DIR/config.jsonc" --style "$CONFIG_DIR/style.css"
