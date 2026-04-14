#!/usr/bin/env bash
set -euo pipefail

CONFIG_ROOT="${HYPRCAT_CONFIG_DIR:-${PYPRLAND_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/hyprcat}}"
WALLPAPER_DIR="$CONFIG_ROOT/wallpapers"
LOCK_CONF="$CONFIG_ROOT/hypr/hyprlock.conf"
RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp}"
TMP_CONF="$RUNTIME_DIR/hyprcat-hyprpaper.conf"

require_cmd() {
  command -v "$1" >/dev/null 2>&1
}

find_wallpaper() {
  local configured=""

  if [ -f "$LOCK_CONF" ]; then
    configured="$(awk -F'= ' '/^[[:space:]]*path[[:space:]]*=/ {print $2; exit}' "$LOCK_CONF")"
    configured="${configured//@HYPRCAT_CONFIG_DIR@/$CONFIG_ROOT}"
    configured="${configured//@PYPRLAND_CONFIG_DIR@/$CONFIG_ROOT}"
    configured="${configured//@HYPRCAT_DATA_DIR@/${HYPRCAT_DATA_DIR:-}}"
    configured="${configured//@PYPRLAND_DATA_DIR@/${PYPRLAND_DATA_DIR:-}}"
    if [ -n "$configured" ] && [ -f "$configured" ]; then
      printf '%s\n' "$configured"
      return 0
    fi
  fi

  find "$WALLPAPER_DIR" -maxdepth 1 -type f \( \
    -iname '*.jpg' -o \
    -iname '*.jpeg' -o \
    -iname '*.png' -o \
    -iname '*.webp' \
  \) | sort | head -n 1
}

find_monitors() {
  local monitors_json

  if monitors_json="$(hyprctl -j monitors 2>/dev/null)" && [ -n "$monitors_json" ]; then
    python3 - "$monitors_json" <<'PY'
import json
import sys

try:
    monitors = json.loads(sys.argv[1])
except Exception:
    sys.exit(1)

for monitor in monitors:
    name = monitor.get("name")
    if name:
        print(name)
PY
    return
  fi

  hyprctl monitors 2>/dev/null | awk '/^Monitor / {print $2}'
}

wait_for_monitors() {
  local monitors=""

  for _ in $(seq 1 50); do
    monitors="$(find_monitors || true)"
    if [ -n "${monitors:-}" ]; then
      printf '%s\n' "$monitors"
      return 0
    fi
    sleep 0.2
  done

  return 1
}

if ! require_cmd hyprctl || ! require_cmd hyprpaper; then
  printf 'hyprpaper: hyprctl and hyprpaper must be installed\n' >&2
  exit 1
fi

WALLPAPER="$(find_wallpaper || true)"
if [ -z "${WALLPAPER:-}" ]; then
  printf 'hyprpaper: no wallpaper found in %s\n' "$WALLPAPER_DIR" >&2
  exit 0
fi

MONITORS="$(wait_for_monitors || true)"
if [ -z "${MONITORS:-}" ]; then
  printf 'hyprpaper: no active monitors reported by hyprctl after waiting for startup\n' >&2
  exit 1
fi

{
  printf 'splash = false\n'
  printf 'ipc = on\n'
  printf '\n'
  printf 'wallpaper {\n'
  printf '    monitor =\n'
  printf '    path = %s\n' "$WALLPAPER"
  printf '    fit_mode = cover\n'
  printf '}\n'
  while IFS= read -r monitor; do
    [ -n "$monitor" ] || continue
    printf '\n'
    printf 'wallpaper {\n'
    printf '    monitor = %s\n' "$monitor"
    printf '    path = %s\n' "$WALLPAPER"
    printf '    fit_mode = cover\n'
    printf '}\n'
  done <<< "$MONITORS"
} > "$TMP_CONF"

if pgrep -x hyprpaper >/dev/null 2>&1; then
  pkill -x hyprpaper
  for _ in 1 2 3 4 5; do
    pgrep -x hyprpaper >/dev/null 2>&1 || break
    sleep 0.2
  done
fi

exec hyprpaper -c "$TMP_CONF"
