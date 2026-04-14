#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob
batteries=(/sys/class/power_supply/BAT*)
shopt -u nullglob

if [ "${#batteries[@]}" -eq 0 ]; then
  exit 0
fi

capacity_sum=0
count=0
status="Unknown"

for battery in "${batteries[@]}"; do
  [ -r "$battery/capacity" ] || continue

  capacity="$(tr -dc '0-9' < "$battery/capacity")"
  [ -n "$capacity" ] || continue

  capacity_sum=$((capacity_sum + capacity))
  count=$((count + 1))

  if [ -r "$battery/status" ]; then
    current_status="$(tr -d '\n' < "$battery/status")"
    if [ "$current_status" = "Charging" ]; then
      status="Charging"
    elif [ "$status" != "Charging" ]; then
      status="$current_status"
    fi
  fi
done

if [ "$count" -eq 0 ]; then
  exit 0
fi

percent=$((capacity_sum / count))

case "$status" in
  Charging) icon="" ;;
  Full) icon="" ;;
  *)
    if [ "$percent" -ge 90 ]; then
      icon=""
    elif [ "$percent" -ge 60 ]; then
      icon=""
    elif [ "$percent" -ge 40 ]; then
      icon=""
    elif [ "$percent" -ge 20 ]; then
      icon=""
    else
      icon=""
    fi
    ;;
esac

if [ "${1:-}" = "--json" ]; then
  class="$(printf '%s' "$status" | tr '[:upper:]' '[:lower:]')"
  printf '{"text":"%s %s%%","tooltip":"Battery: %s%% (%s)","class":"%s"}\n' \
    "$icon" "$percent" "$percent" "$status" "$class"
else
  printf '%s %s%%\n' "$icon" "$percent"
fi
