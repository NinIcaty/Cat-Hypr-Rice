#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/hypr-material3/anyrun"
exec anyrun --config-dir "$CONFIG_DIR"
