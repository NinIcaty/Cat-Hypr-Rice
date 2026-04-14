#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${PYPRLAND_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/pyprland}"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

mkdir -p "$BIN_DIR" "$APP_DIR"

export PYPRLAND_DATA_DIR="$PROJECT_DIR"
export PYPRLAND_CONFIG_DIR="$CONFIG_DIR"

python3 "$PROJECT_DIR/scripts/bootstrap_config.py" --data-dir "$PROJECT_DIR" --config-dir "$CONFIG_DIR"

cat > "$BIN_DIR/pyprland-session" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export PYPRLAND_DATA_DIR="$PROJECT_DIR"
export PYPRLAND_CONFIG_DIR="$CONFIG_DIR"
exec "$PROJECT_DIR/bin/pyprland-session"
EOF

cat > "$BIN_DIR/pyprland-settings" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export PYPRLAND_DATA_DIR="$PROJECT_DIR"
export PYPRLAND_CONFIG_DIR="$CONFIG_DIR"
exec "$PROJECT_DIR/bin/pyprland-settings"
EOF

chmod +x "$BIN_DIR/pyprland-session" "$BIN_DIR/pyprland-settings"
install -m644 "$PROJECT_DIR/packaging/pyprland-settings.desktop" "$APP_DIR/pyprland-settings.desktop"

printf 'Pyprland config was installed to %s\n' "$CONFIG_DIR"
printf 'Local launchers were installed to %s\n' "$BIN_DIR"
printf 'Open the settings app with: %s\n' "$BIN_DIR/pyprland-settings"
printf '\nFor a display-manager session entry, install the AUR package so the wayland session file is placed in /usr/share/wayland-sessions.\n'
