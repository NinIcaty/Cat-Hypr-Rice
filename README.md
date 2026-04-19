# Hyprcat

Hyprcat is a standalone Hyprland desktop session with a Material 3 style, bundled launcher and panel defaults, and a settings app for common tweaks.

## What it includes

- a dedicated `Hyprcat` Wayland session entry
- a first-run config bootstrap into `~/.config/hyprcat`
- `hyprpaper`, `swaync`, `waybar`, `rofi`, and optional `anyrun` integration
- a Tk settings app for wallpaper, animations, brightness, cursor, window highlight, shortcuts, and default app commands

## Package layout

The package installs:

- `/usr/bin/hyprcat-session`
- `/usr/bin/hyprcat-settings`
- `/usr/share/hyprcat`
- `/usr/share/wayland-sessions/hyprcat.desktop`

The session launcher bootstraps a per-user config on first start and runs:

```bash
Hyprland --config ~/.config/hyprcat/hypr/hyprland.conf
```

This keeps Hyprcat separate from a normal `~/.config/hypr/hyprland.conf`.

## AUR

This repo includes an AUR-ready `PKGBUILD` for `hyprcat`.

For local testing from this checkout, `makepkg` packages the current working tree if the source files are present locally. That avoids depending on a pushed GitHub state just to test package changes.

## Local install from checkout

```bash
chmod +x install.sh
./install.sh
```

That installs:

- user config into `~/.config/hyprcat`
- local helper launchers into `~/.local/bin`
- a settings desktop file into `~/.local/share/applications`

Run the settings app with:

```bash
hyprcat-settings
```

Or from the local checkout wrapper:

```bash
~/.local/bin/hyprcat-settings
```

## Settings app

The settings app can change:

- animation speed and animation enable or disable
- screen brightness when `brightnessctl` is installed
- wallpaper selection and wallpaper import
- cursor theme and cursor size
- active window highlight colors
- shortcut bindings for common actions
- the default commands used for the terminal, file manager, launcher, quick runner, and media controller

## Wallpaper behavior

- the settings app updates the wallpaper used by both `hyprpaper` and `hyprlock`
- imported wallpapers are copied into `~/.config/hyprcat/wallpapers/`
- the active wallpaper path is stored in `~/.config/hyprcat/hypr/hyprlock.conf`

## Notes

- Existing `pyprland` and `hypr-material3` config directories are still detected by the settings app as fallbacks.
- `license=('custom')` is still a placeholder until you decide on the project license text.
