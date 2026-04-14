#!/usr/bin/env bash
set -euo pipefail

if swaync-client -D 2>/dev/null | grep -qi true; then
  printf '{"text":"","class":"dnd"}\n'
else
  printf '{"text":"","class":"active"}\n'
fi
