#!/usr/bin/env bash
set -euo pipefail

if ! command -v playerctl >/dev/null 2>&1; then
  printf '{"text":"󰐎","class":"inactive","tooltip":"playerctl is not installed"}\n'
  exit 0
fi

if ! playerctl status >/dev/null 2>&1; then
  printf '{"text":"󰎈","class":"inactive","tooltip":"Open media controller"}\n'
  exit 0
fi

status="$(playerctl status 2>/dev/null || true)"

case "$status" in
  Playing)
    icon="󰐊"
    class="active"
    tooltip="$(printf 'Open media controller\nPlayback is active')"
    ;;
  Paused)
    icon="󰏤"
    class="active"
    tooltip="$(printf 'Open media controller\nPlayback is paused')"
    ;;
  *)
    icon="󰎈"
    class="inactive"
    tooltip="Open media controller"
    ;;
esac

escaped_tooltip="$(printf '%s' "$tooltip" | sed ':a;N;$!ba;s/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g')"
printf '{"text":"%s","class":"%s","tooltip":"%s"}\n' "$icon" "$class" "$escaped_tooltip"
