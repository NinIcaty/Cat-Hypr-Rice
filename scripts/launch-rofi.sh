#!/usr/bin/env bash
set -euo pipefail

THEME="${XDG_CONFIG_HOME:-$HOME/.config}/hypr-material3/rofi/material3.rasi"
EXEC_WRAPPER="${XDG_CONFIG_HOME:-$HOME/.config}/hypr-material3/scripts/rofi-exec.sh"
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
