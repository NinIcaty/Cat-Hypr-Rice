#!/usr/bin/env bash
set -euo pipefail

cmd="$*"
cmd="${cmd#"${cmd%%[![:space:]]*}"}"
cmd="${cmd%"${cmd##*[![:space:]]}"}"

[ -z "$cmd" ] && exit 0

terminal_bin="${TERMINAL:-ghostty}"

case "$cmd" in
  nvim\ *|nvim|vim\ *|vim|vi\ *|vi)
    exec "$terminal_bin" -e bash -lc "$cmd"
    ;;
  *)
    exec bash -lc "$cmd"
    ;;
esac
