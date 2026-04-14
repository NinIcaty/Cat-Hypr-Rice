# Pyprland Desktop

Pyprland Desktop is a standalone Hyprland session with a Material 3 style, bundled launcher/status-bar/notification defaults, and a local settings app for common tweaks.

## What it includes

- a dedicated `Pyprland` Wayland session entry
- a first-run config bootstrap into `~/.config/pyprland`
- `hyprpaper`, `swaync`, `waybar`, `rofi`, and optional `anyrun` integration
- a Tk settings app for animations, cursor, window highlight, shortcuts, and default app commands

## AUR packaging

This repo now includes an AUR-friendly `PKGBUILD` for `pyprland-desktop-git`.

Expected install layout:

- `/usr/bin/pyprland-session`
- `/usr/bin/pyprland-settings`
- `/usr/share/pyprland-desktop`
- `/usr/share/wayland-sessions/pyprland.desktop`

The session launcher bootstraps a per-user config on first start and runs:

```bash
Hyprland --config ~/.config/pyprland/hypr/hyprland.conf
```

That means it does not need to replace `~/.config/hypr/hyprland.conf`.

## Local install from checkout

```bash
chmod +x install.sh
./install.sh
```

That installs:

- user config into `~/.config/pyprland`
- local helper launchers into `~/.local/bin`
- a settings desktop file into `~/.local/share/applications`

For a display-manager session chooser, use the packaged install path so `pyprland.desktop` lands in `/usr/share/wayland-sessions`.

## Settings app

Run the settings app with:

```bash
pyprland-settings
```

Or from a local checkout install:

```bash
~/.local/bin/pyprland-settings
```

The app can change:

- animation speed and animation enable/disable
- cursor theme and cursor size
- active window highlight colors
- shortcut bindings for common actions
- the default commands used for the terminal, file manager, launcher, quick runner, and media controller

## Wallpaper behavior

- `hyprpaper` loads the first image in `~/.config/pyprland/wallpapers/` alphabetically
- the lock screen background is configured in `~/.config/pyprland/hypr/hyprlock.conf`
- replacing `NewMainDark.png` is the simplest way to update both

## AUR submission notes

- `PKGBUILD` is ready for a `-git` package flow
- the package metadata still uses `license=('custom')`
- before submitting to AUR, add the exact license you want this project distributed under
