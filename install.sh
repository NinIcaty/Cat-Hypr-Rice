#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HYPRCAT_CONFIG_DIR:-${PYPRLAND_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/hyprcat}}"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
WAYLAND_SESSION_DIR="/usr/share/wayland-sessions"

mkdir -p "$BIN_DIR" "$APP_DIR"

export HYPRCAT_DATA_DIR="$PROJECT_DIR"
export HYPRCAT_CONFIG_DIR="$CONFIG_DIR"

python3 "$PROJECT_DIR/scripts/bootstrap_config.py" --data-dir "$PROJECT_DIR" --config-dir "$CONFIG_DIR"

cat > "$BIN_DIR/hyprcat-session" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export HYPRCAT_DATA_DIR="$PROJECT_DIR"
export HYPRCAT_CONFIG_DIR="$CONFIG_DIR"
exec "$PROJECT_DIR/bin/hyprcat-session"
EOF

cat > "$BIN_DIR/hyprcat-settings" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export HYPRCAT_DATA_DIR="$PROJECT_DIR"
export HYPRCAT_CONFIG_DIR="$CONFIG_DIR"
exec "$PROJECT_DIR/bin/hyprcat-settings"
EOF

chmod +x "$BIN_DIR/hyprcat-session" "$BIN_DIR/hyprcat-settings"
install -m644 "$PROJECT_DIR/packaging/hyprcat-settings.desktop" "$APP_DIR/hyprcat-settings.desktop"

if [[ -w "$WAYLAND_SESSION_DIR" ]]; then
  install -Dm644 "$PROJECT_DIR/packaging/hyprcat.desktop" "$WAYLAND_SESSION_DIR/hyprcat.desktop"
  printf 'Wayland session entry was installed to %s\n' "$WAYLAND_SESSION_DIR/hyprcat.desktop"
else
  printf 'Skipping %s install because it is not writable.\n' "$WAYLAND_SESSION_DIR"
  printf 'Install the package system-wide, or rerun this script with privileges, to make Hyprcat show up in SDDM.\n'
fi

printf 'Hyprcat config was installed to %s\n' "$CONFIG_DIR"
printf 'Local launchers were installed to %s\n' "$BIN_DIR"
printf 'Open the settings app with: %s\n' "$BIN_DIR/hyprcat-settings"
