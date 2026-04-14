# Material 3 Hyprland Theme

This repository contains an installable Material 3-inspired Hyprland setup with:

- `anyrun` as the main launcher
- `swaync` as the notification center
- `hyprpaper` wallpaper support
- `Ghostty` as the terminal
- `nautilus` as the file manager
- `rofi` as a quick app/command runner
- a separate keybind file so controls are easy to change

## Install

```bash
chmod +x install.sh
./install.sh
```

After install, edit:

- `~/.config/hypr-material3/hypr/keybinds.conf`
- `~/.config/hypr-material3/hypr/apps.conf`
- put a wallpaper image in `~/.config/hypr-material3/wallpapers/`

Wallpaper selection:

- `hyprpaper` loads the first image in `~/.config/hypr-material3/wallpapers/` alphabetically
- the lock screen background is set separately in `~/.config/hypr-material3/hypr/hyprlock.conf`
- the simplest way to change both is to replace `NewMainDark.png` and then restart Hyprland or run `~/.config/hypr-material3/scripts/launch-hyprpaper.sh`

If you already have a `~/.config/hypr/hyprland.conf`, the installer will back it up and replace it with a small loader that sources the new theme entrypoint.
