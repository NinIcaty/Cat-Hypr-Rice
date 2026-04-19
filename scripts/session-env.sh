#!/usr/bin/env bash
set -euo pipefail

if ! command -v dbus-update-activation-environment >/dev/null 2>&1; then
  exit 0
fi

exec dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP
