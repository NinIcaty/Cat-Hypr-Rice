#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HYPRCAT_CONFIG_DIR:-${PYPRLAND_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/hyprcat}}/waybar"
pkill -x waybar >/dev/null 2>&1 || true
exec waybar --config "$CONFIG_DIR/config.jsonc" --style "$CONFIG_DIR/style.css"
