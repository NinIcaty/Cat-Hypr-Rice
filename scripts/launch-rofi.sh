#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${HYPRCAT_CONFIG_DIR:-${PYPRLAND_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/hyprcat}}"
DATA_DIR="${HYPRCAT_DATA_DIR:-${PYPRLAND_DATA_DIR:-/usr/share/hyprcat}}"
THEME="$CONFIG_DIR/rofi/material3.rasi"
EXEC_WRAPPER="$DATA_DIR/scripts/rofi-exec.sh"
TERMINAL_BIN="${TERMINAL:-ghostty}"

exec rofi \
  -show combi \
  -combi-modes "drun,run" \
  -modi "combi,drun,run" \
  -show-icons \
  -terminal "$TERMINAL_BIN" \
  -run-command "$EXEC_WRAPPER {cmd}" \
  -run-shell-command "$EXEC_WRAPPER {cmd}" \
  -theme "$THEME"
