#!/usr/bin/env bash
set -euo pipefail

if ! command -v playerctl >/dev/null 2>&1; then
  printf '{"text":"󰐎  No playerctl","class":"inactive","tooltip":"playerctl is not installed"}\n'
  exit 0
fi

if ! playerctl status >/dev/null 2>&1; then
  printf '{"text":"󰎈  No media","class":"inactive","tooltip":"Nothing is playing right now"}\n'
  exit 0
fi

status="$(playerctl status 2>/dev/null || true)"
artist="$(playerctl metadata artist 2>/dev/null || true)"
title="$(playerctl metadata title 2>/dev/null || true)"
album="$(playerctl metadata album 2>/dev/null || true)"
player="$(playerctl metadata --format '{{playerName}}' 2>/dev/null | head -n1 || true)"

if [ -z "$artist$title" ]; then
  text="Media playing"
else
  text="${artist:+$artist - }$title"
fi

text="${text//$'\n'/ }"
text="$(printf '%s' "$text" | cut -c1-52)"

case "$status" in
  Playing) icon="" ;;
  Paused) icon="󰏤" ;;
  *) icon="󰓛" ;;
esac

escaped_text="$(printf '%s' "$text" | sed 's/\\/\\\\/g; s/"/\\"/g')"
tooltip="$(printf '%s\n%s\n%s\n%s' "${artist:-Unknown artist}" "${title:-Unknown track}" "${album:-Unknown album}" "${player:-Unknown player}")"
escaped_tooltip="$(printf '%s' "$tooltip" | sed ':a;N;$!ba;s/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g')"
printf '{"text":"%s  %s","class":"%s","tooltip":"%s"}\n' \
  "$icon" \
  "$escaped_text" \
  "$(printf '%s' "$status" | tr '[:upper:]' '[:lower:]')" \
  "$escaped_tooltip"
