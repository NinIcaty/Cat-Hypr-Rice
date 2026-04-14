# Material 3 Hyprland Theme

This repository contains an installable Material 3-inspired Hyprland setup with:

- `anyrun` as the main launcher
- `swaync` as the notification center
- `hyprpaper` wallpaper support
- `Ghostty` as the terminal
- `nautilus` as the file manager
- `rofi` as a quick app/command runner
- a separate keybind file so controls are easy to change
- a local Python settings app for common tweaks

## Install

```bash
chmod +x install.sh
./install.sh
```

After install, edit:

- `~/.config/hypr-material3/hypr/keybinds.conf`
- `~/.config/hypr-material3/hypr/apps.conf`
- put a wallpaper image in `~/.config/hypr-material3/wallpapers/`

Or use the settings app:

```bash
python3 ~/.config/hypr-material3/settings_app.py
```

The app can update:

- animation speed and animation enable/disable
- cursor theme and cursor size
- active window highlight colors
- shortcut bindings for common actions
- the default commands used for the terminal, file manager, launcher, and quick runner

Wallpaper selection:

- `hyprpaper` loads the first image in `~/.config/hypr-material3/wallpapers/` alphabetically
- the lock screen background is set separately in `~/.config/hypr-material3/hypr/hyprlock.conf`
- the simplest way to change both is to replace `NewMainDark.png` and then restart Hyprland or run `~/.config/hypr-material3/scripts/launch-hyprpaper.sh`

If you already have a `~/.config/hypr/hyprland.conf`, the installer will back it up and replace it with a small loader that sources the new theme entrypoint.
