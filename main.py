#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from typing import Callable


DEFAULT_ANIMATION_SPEEDS = {
    "windows": 5.0,
    "windowsOut": 4.0,
    "border": 6.0,
    "fade": 5.0,
    "workspaces": 5.0,
}

APP_VARIABLES = {
    "Terminal": "$terminal",
    "File manager": "$fileManager",
    "Main launcher": "$menu",
    "Quick runner": "$quickRunner",
    "Media controller": "$mediaController",
}

ACCENT_COLORS = {
    "Blue": "#89dceb",
    "Lavender": "#b4befe",
    "Rose": "#f5c2e7",
    "Green": "#a6e3a1",
    "Peach": "#fab387",
    "Red": "#f38ba8",
}


@dataclass
class ConfigPaths:
    root: Path
    data_root: Path
    hyprland: Path
    hyprlock: Path
    theme: Path
    apps: Path
    keybinds: Path
    wallpaper_dir: Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def detect_data_root() -> Path:
    env_root = os.environ.get("HYPRCAT_DATA_DIR") or os.environ.get("PYPRLAND_DATA_DIR")
    if env_root:
        return Path(env_root).expanduser()
    return repo_root()


def build_shortcut_targets(config_root: Path) -> dict[str, tuple[str, str, str]]:
    return {
        "Open terminal": ("bind", "exec", "$terminal"),
        "Open file manager": ("bind", "exec", "$fileManager"),
        "Open app launcher": ("bind", "exec", "$menu"),
        "Open quick runner": ("bind", "exec", "$quickRunner"),
        "Close active window": ("bind", "killactive", ""),
        "Toggle floating": ("bind", "togglefloating", ""),
        "Fullscreen": ("bind", "fullscreen", ""),
        "Lock screen": (
            "bind",
            "exec",
            f"hyprlock --config {config_root}/hypr/hyprlock.conf",
        ),
    }


def detect_config_paths() -> ConfigPaths:
    xdg_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")).expanduser()
    env_root = os.environ.get("HYPRCAT_CONFIG_DIR") or os.environ.get("PYPRLAND_CONFIG_DIR")
    candidates = []
    if env_root:
        candidates.append(Path(env_root).expanduser())
    candidates.extend(
        [
            xdg_home / "hyprcat",
            xdg_home / "pyprland",
            xdg_home / "hypr-material3",
            repo_root() / "config",
        ]
    )
    root = next((candidate for candidate in candidates if (candidate / "hypr" / "hyprland.conf").exists()), repo_root() / "config")
    hypr_dir = root / "hypr"
    return ConfigPaths(
        root=root,
        data_root=detect_data_root(),
        hyprland=hypr_dir / "hyprland.conf",
        hyprlock=hypr_dir / "hyprlock.conf",
        theme=hypr_dir / "theme.conf",
        apps=hypr_dir / "apps.conf",
        keybinds=hypr_dir / "keybinds.conf",
        wallpaper_dir=(root / "wallpapers") if (root / "wallpapers").exists() else detect_data_root() / "wallpapers",
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def replace_or_append(text: str, pattern: str, replacement: str, anchor: str | None = None) -> str:
    new_text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if count:
        return new_text
    if anchor and anchor in text:
        return text.replace(anchor, f"{anchor}\n{replacement}")
    return text.rstrip() + "\n" + replacement + "\n"


def replace_block(text: str, block_name: str, transform: Callable[[str], str]) -> str:
    pattern = rf"({re.escape(block_name)}\s*\{{\n)(.*?)(^\}})"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"Missing block {block_name}")
    prefix, body, suffix = match.groups()
    updated_body = transform(body)
    return text[: match.start()] + prefix + updated_body + suffix + text[match.end() :]


def normalize_hex_color(value: str) -> str:
    color = value.strip().lstrip("#")
    if len(color) != 6 or not all(char in "0123456789abcdefABCDEF" for char in color):
        raise ValueError("Expected a 6-digit hex color.")
    return color.lower()


def hex_to_hypr_rgb(value: str) -> str:
    return f"rgb({normalize_hex_color(value)})"


def hex_to_hypr_rgba(value: str) -> str:
    return f"rgba({normalize_hex_color(value)}ff)"


def hypr_color_to_hex(value: str) -> str:
    match = re.search(r"(?:rgb|rgba)\(([0-9a-fA-F]{6})", value)
    if not match:
        raise ValueError(f"Unsupported color format: {value}")
    return f"#{match.group(1).lower()}"


def parse_variable(text: str, variable: str) -> str:
    match = re.search(rf"^{re.escape(variable)}\s*=\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"Missing variable {variable}")
    return match.group(1).strip()


def set_variable(text: str, variable: str, value: str) -> str:
    pattern = rf"^{re.escape(variable)}\s*=\s*.+$"
    return replace_or_append(text, pattern, f"{variable} = {value}")


def parse_cursor(text: str) -> tuple[str, int]:
    theme_match = re.search(r"^env\s*=\s*XCURSOR_THEME,(.+)$", text, flags=re.MULTILINE)
    size_match = re.search(r"^env\s*=\s*XCURSOR_SIZE,(\d+)$", text, flags=re.MULTILINE)
    theme = theme_match.group(1).strip() if theme_match else "Bibata-Modern-Classic"
    size = int(size_match.group(1)) if size_match else 24
    return theme, size


def set_cursor(text: str, theme: str, size: int) -> str:
    result = replace_or_append(
        text,
        r"^env\s*=\s*XCURSOR_THEME,.+$",
        f"env = XCURSOR_THEME,{theme}",
        anchor="monitor=,preferred,auto,1",
    )
    return replace_or_append(
        result,
        r"^env\s*=\s*XCURSOR_SIZE,\d+$",
        f"env = XCURSOR_SIZE,{size}",
        anchor=f"env = XCURSOR_THEME,{theme}",
    )


def parse_border_colors(text: str) -> tuple[str, str, str]:
    active_match = re.search(
        r"col\.active_border\s*=\s*(rgba\([^)]+\))\s+(rgba\([^)]+\))",
        text,
    )
    inactive_match = re.search(r"col\.inactive_border\s*=\s*(rgba\([^)]+\))", text)
    if not active_match or not inactive_match:
        raise ValueError("Border colors not found in config.")
    return (
        hypr_color_to_hex(active_match.group(1)),
        hypr_color_to_hex(active_match.group(2)),
        hypr_color_to_hex(inactive_match.group(1)),
    )


def set_border_colors(text: str, active_start: str, active_end: str, inactive: str) -> str:
    result = replace_or_append(
        text,
        r"^\s*col\.active_border\s*=.+$",
        f"    col.active_border = {hex_to_hypr_rgba(active_start)} {hex_to_hypr_rgba(active_end)} 45deg",
    )
    return replace_or_append(
        result,
        r"^\s*col\.inactive_border\s*=.+$",
        f"    col.inactive_border = {hex_to_hypr_rgba(inactive)}",
    )


def parse_wallpaper_path(text: str) -> str:
    match = re.search(r"^\s*path\s*=\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        raise ValueError("Wallpaper path not found in hyprlock config.")
    return match.group(1).strip()


def set_wallpaper_path(text: str, value: str) -> str:
    return replace_or_append(text, r"^\s*path\s*=.+$", f"    path = {value}")


def parse_theme_color(text: str, variable: str) -> str:
    value = parse_variable(text, variable)
    return hypr_color_to_hex(value)


def set_theme_color(text: str, variable: str, value: str) -> str:
    return set_variable(text, variable, hex_to_hypr_rgb(value))


def parse_animation_multiplier(text: str) -> float:
    match = re.search(r"animation\s*=\s*windows,\s*1,\s*([0-9.]+),", text)
    if not match:
        return 1.0
    speed = float(match.group(1))
    return max(0.2, min(3.0, speed / DEFAULT_ANIMATION_SPEEDS["windows"]))


def set_animation_multiplier(text: str, multiplier: float, enabled: bool) -> str:
    def transform(body: str) -> str:
        updated = re.sub(
            r"^\s*enabled\s*=\s*(true|false)$",
            f"    enabled = {'true' if enabled else 'false'}",
            body,
            flags=re.MULTILINE,
        )
        for name, base_speed in DEFAULT_ANIMATION_SPEEDS.items():
            speed = f"{base_speed * multiplier:.2f}".rstrip("0").rstrip(".")
            updated = re.sub(
                rf"(^\s*animation\s*=\s*{re.escape(name)},\s*1,\s*)([0-9.]+)(,.*$)",
                rf"\g<1>{speed}\g<3>",
                updated,
                flags=re.MULTILINE,
            )
        return updated

    return replace_block(text, "animations", transform)


def parse_animation_enabled(text: str) -> bool:
    match = re.search(r"^\s*enabled\s*=\s*(true|false)$", text, flags=re.MULTILINE)
    return not match or match.group(1) == "true"


def parse_shortcuts(text: str, shortcut_targets: dict[str, tuple[str, str, str]]) -> dict[str, str]:
    shortcuts: dict[str, str] = {}
    for label, (bind_type, action, target) in shortcut_targets.items():
        for line in text.splitlines():
            parsed = parse_bind_line(line)
            if not parsed:
                continue
            if (
                parsed["bind_type"] != bind_type
                or parsed["action"] != action
                or parsed["value"] != target
            ):
                continue
            shortcuts[label] = build_combo_string(parsed["mods"], parsed["key"])
            break
    return shortcuts


def build_combo_string(mods: str, key: str) -> str:
    parts = [part.strip() for part in mods.split() if part.strip()]
    if key:
        parts.append(key.strip())
    return "+".join(parts) if parts else key.strip()


def split_combo_string(combo: str) -> tuple[str, str]:
    cleaned = combo.strip()
    if not cleaned:
        raise ValueError("Shortcut cannot be empty.")
    parts = [part.strip() for part in cleaned.split("+") if part.strip()]
    if not parts:
        raise ValueError("Shortcut cannot be empty.")
    return (" ".join(parts[:-1]), parts[-1])


def set_shortcuts(
    text: str,
    shortcuts: dict[str, str],
    shortcut_targets: dict[str, tuple[str, str, str]],
) -> str:
    result = text
    for label, combo in shortcuts.items():
        bind_type, action, target = shortcut_targets[label]
        mods, key = split_combo_string(combo)
        value = f", {target}" if target else ","
        replacement = f"{bind_type} = {mods}, {key}, {action}{value}" if mods else f"{bind_type} = , {key}, {action}{value}"
        updated = False
        new_lines = []
        for line in result.splitlines():
            parsed = parse_bind_line(line)
            if (
                parsed
                and parsed["bind_type"] == bind_type
                and parsed["action"] == action
                and parsed["value"] == target
            ):
                new_lines.append(replacement)
                updated = True
            else:
                new_lines.append(line)
        result = "\n".join(new_lines) + "\n"
        if not updated:
            result += replacement + "\n"
    return result


def parse_bind_line(line: str) -> dict[str, str] | None:
    match = re.match(r"^(bindm|bindel|bind)\s*=\s*(.*?),\s*(.*?),\s*([^,]+)(?:,\s*(.*))?$", line)
    if not match:
        return None
    return {
        "bind_type": match.group(1).strip(),
        "mods": match.group(2).strip(),
        "key": match.group(3).strip(),
        "action": match.group(4).strip(),
        "value": (match.group(5) or "").strip(),
    }


def run_hyprctl(*args: str) -> None:
    if not os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return
    subprocess.run(["hyprctl", *args], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def apply_wallpaper(data_root: Path) -> None:
    if not os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return
    launcher = data_root / "scripts" / "launch-hyprpaper.sh"
    if not launcher.exists():
        return
    subprocess.run([str(launcher)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SettingsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.paths = detect_config_paths()
        self.shortcut_targets = build_shortcut_targets(self.paths.root)
        self.root.title("Hyprcat Settings")
        self.root.geometry("980x720")
        self.root.minsize(880, 640)
        self.root.configure(bg="#111318")

        self.status_var = tk.StringVar()
        self.config_location_var = tk.StringVar(
            value=f"Editing: {self.paths.root}"
        )

        self.animation_enabled_var = tk.BooleanVar()
        self.animation_multiplier_var = tk.DoubleVar()
        self.wallpaper_var = tk.StringVar()
        self.cursor_theme_var = tk.StringVar()
        self.cursor_size_var = tk.IntVar()
        self.active_start_var = tk.StringVar()
        self.active_end_var = tk.StringVar()
        self.inactive_border_var = tk.StringVar()
        self.primary_color_var = tk.StringVar()
        self.secondary_color_var = tk.StringVar()
        self.app_vars = {label: tk.StringVar() for label in APP_VARIABLES}
        self.shortcut_vars = {label: tk.StringVar() for label in self.shortcut_targets}
        self.wallpaper_combo: ttk.Combobox | None = None

        self.build_ui()
        self.load()

    def build_ui(self) -> None:
        self.configure_style()

        container = ttk.Frame(self.root, padding=18, style="App.TFrame")
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="Card.TFrame", padding=18)
        header.pack(fill="x")
        ttk.Label(header, text="Hyprcat Settings", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Tweak the Material 3 Hyprland theme without editing config files by hand.",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(6, 0))
        ttk.Label(header, textvariable=self.config_location_var, style="Muted.TLabel").pack(anchor="w", pady=(8, 0))

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True, pady=16)

        appearance_tab = ttk.Frame(notebook, style="App.TFrame", padding=14)
        apps_tab = ttk.Frame(notebook, style="App.TFrame", padding=14)
        shortcuts_tab = ttk.Frame(notebook, style="App.TFrame", padding=14)

        notebook.add(appearance_tab, text="Appearance")
        notebook.add(apps_tab, text="Apps")
        notebook.add(shortcuts_tab, text="Shortcuts")

        self.build_appearance_tab(appearance_tab)
        self.build_apps_tab(apps_tab)
        self.build_shortcuts_tab(shortcuts_tab)

        footer = ttk.Frame(container, style="App.TFrame")
        footer.pack(fill="x", pady=(6, 0))
        ttk.Label(footer, textvariable=self.status_var, style="Muted.TLabel").pack(side="left")
        ttk.Button(footer, text="Reload", command=self.load, style="Secondary.TButton").pack(side="right")
        ttk.Button(footer, text="Save and Apply", command=self.save, style="Primary.TButton").pack(side="right", padx=(0, 10))

    def configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("App.TFrame", background="#111318")
        style.configure("Card.TFrame", background="#181c23", relief="flat")
        style.configure("Title.TLabel", background="#181c23", foreground="#f2f4f8", font=("TkDefaultFont", 20, "bold"))
        style.configure("Section.TLabel", background="#181c23", foreground="#f2f4f8", font=("TkDefaultFont", 12, "bold"))
        style.configure("Body.TLabel", background="#181c23", foreground="#d6dae4", font=("TkDefaultFont", 10))
        style.configure("Muted.TLabel", background="#111318", foreground="#98a1b3", font=("TkDefaultFont", 9))
        style.configure("Field.TLabel", background="#181c23", foreground="#e6eaf2", font=("TkDefaultFont", 10))
        style.configure("Primary.TButton", padding=(14, 8), background="#7dd3c3", foreground="#0d1117")
        style.map("Primary.TButton", background=[("active", "#92e3d5")])
        style.configure("Secondary.TButton", padding=(14, 8), background="#29303d", foreground="#e6eaf2")
        style.map("Secondary.TButton", background=[("active", "#343d4d")])
        style.configure("TNotebook", background="#111318", borderwidth=0)
        style.configure("TNotebook.Tab", background="#29303d", foreground="#d6dae4", padding=(18, 10))
        style.map("TNotebook.Tab", background=[("selected", "#181c23")], foreground=[("selected", "#f2f4f8")])
        style.configure("TCheckbutton", background="#181c23", foreground="#e6eaf2")
        style.configure("TEntry", fieldbackground="#0f131a", foreground="#f2f4f8", insertcolor="#f2f4f8")
        style.configure("TScale", background="#181c23")

    def build_appearance_tab(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Wallpaper", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        wallpaper_row = ttk.Frame(card, style="Card.TFrame")
        wallpaper_row.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        wallpaper_row.columnconfigure(0, weight=1)
        self.wallpaper_combo = ttk.Combobox(
            wallpaper_row,
            textvariable=self.wallpaper_var,
            state="readonly",
        )
        self.wallpaper_combo.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(
            wallpaper_row,
            text="Import…",
            command=self.import_wallpaper,
            style="Secondary.TButton",
        ).grid(row=0, column=1, sticky="e", padx=(0, 8))
        ttk.Button(
            wallpaper_row,
            text="Refresh",
            command=self.refresh_wallpaper_choices,
            style="Secondary.TButton",
        ).grid(row=0, column=2, sticky="e")
        ttk.Label(
            card,
            text="Imported files are copied into the theme wallpaper folder and used for both desktop and lock screen.",
            style="Muted.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))

        ttk.Separator(card, orient="horizontal").grid(row=3, column=0, sticky="ew", pady=18)

        ttk.Label(card, text="Animations", style="Section.TLabel").grid(row=4, column=0, sticky="w")
        ttk.Checkbutton(card, text="Enable animations", variable=self.animation_enabled_var).grid(row=5, column=0, sticky="w", pady=(10, 6))
        ttk.Label(card, text="Animation speed", style="Field.TLabel").grid(row=6, column=0, sticky="w", pady=(8, 0))
        ttk.Scale(card, from_=0.4, to=2.5, variable=self.animation_multiplier_var, orient="horizontal").grid(row=7, column=0, sticky="ew", pady=(6, 0))
        ttk.Label(card, text="0.4x is slower and 2.5x is snappier.", style="Muted.TLabel").grid(row=8, column=0, sticky="w")

        ttk.Separator(card, orient="horizontal").grid(row=9, column=0, sticky="ew", pady=18)

        ttk.Label(card, text="Cursor", style="Section.TLabel").grid(row=10, column=0, sticky="w")
        cursor_grid = ttk.Frame(card, style="Card.TFrame")
        cursor_grid.grid(row=11, column=0, sticky="ew", pady=(10, 0))
        cursor_grid.columnconfigure(1, weight=1)
        ttk.Label(cursor_grid, text="Theme", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12))
        ttk.Entry(cursor_grid, textvariable=self.cursor_theme_var).grid(row=0, column=1, sticky="ew")
        ttk.Label(cursor_grid, text="Size", style="Field.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=(10, 0))
        ttk.Spinbox(cursor_grid, from_=16, to=64, textvariable=self.cursor_size_var, increment=1).grid(row=1, column=1, sticky="w", pady=(10, 0))

        ttk.Separator(card, orient="horizontal").grid(row=12, column=0, sticky="ew", pady=18)

        ttk.Label(card, text="Window Highlight", style="Section.TLabel").grid(row=13, column=0, sticky="w")
        colors = ttk.Frame(card, style="Card.TFrame")
        colors.grid(row=14, column=0, sticky="ew", pady=(10, 0))
        colors.columnconfigure(1, weight=1)
        colors.columnconfigure(3, weight=1)
        self.make_color_field(colors, "Active start", self.active_start_var, 0, 0)
        self.make_color_field(colors, "Active end", self.active_end_var, 1, 0)
        self.make_color_field(colors, "Inactive", self.inactive_border_var, 2, 0)

        ttk.Separator(card, orient="horizontal").grid(row=15, column=0, sticky="ew", pady=18)

        ttk.Label(card, text="Theme Accent", style="Section.TLabel").grid(row=16, column=0, sticky="w")
        accent_row = ttk.Frame(card, style="Card.TFrame")
        accent_row.grid(row=17, column=0, sticky="ew", pady=(10, 0))
        accent_row.columnconfigure(1, weight=1)
        accent_row.columnconfigure(3, weight=1)
        self.make_color_field(accent_row, "Primary", self.primary_color_var, 0, 0)
        self.make_color_field(accent_row, "Secondary", self.secondary_color_var, 0, 2)

        presets = ttk.Frame(card, style="Card.TFrame")
        presets.grid(row=18, column=0, sticky="w", pady=(12, 0))
        ttk.Label(presets, text="Quick accents", style="Muted.TLabel").pack(side="left", padx=(0, 8))
        for label, color in ACCENT_COLORS.items():
            ttk.Button(
                presets,
                text=label,
                command=lambda value=color: self.apply_accent_preset(value),
                style="Secondary.TButton",
            ).pack(side="left", padx=(0, 6))

        card.columnconfigure(0, weight=1)

    def build_apps_tab(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True)
        ttk.Label(card, text="Default Commands", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            card,
            text="These are the commands used by the theme’s launcher shortcuts.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(6, 14))

        for label, variable in self.app_vars.items():
            row = ttk.Frame(card, style="Card.TFrame")
            row.pack(fill="x", pady=(0, 12))
            row.columnconfigure(1, weight=1)
            ttk.Label(row, text=label, style="Field.TLabel", width=16).grid(row=0, column=0, sticky="w", padx=(0, 12))
            ttk.Entry(row, textvariable=variable).grid(row=0, column=1, sticky="ew")

    def build_shortcuts_tab(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.pack(fill="both", expand=True)
        ttk.Label(card, text="Shortcuts", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            card,
            text="Use Hyprland-style combos such as SUPER+Q or SUPER+SHIFT+E.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(6, 14))

        for label, variable in self.shortcut_vars.items():
            row = ttk.Frame(card, style="Card.TFrame")
            row.pack(fill="x", pady=(0, 12))
            row.columnconfigure(1, weight=1)
            ttk.Label(row, text=label, style="Field.TLabel", width=20).grid(row=0, column=0, sticky="w", padx=(0, 12))
            ttk.Entry(row, textvariable=variable).grid(row=0, column=1, sticky="ew")

    def make_color_field(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int, column: int) -> None:
        ttk.Label(parent, text=label, style="Field.TLabel").grid(row=row, column=column, sticky="w", padx=(0, 8), pady=(0, 10))
        entry = ttk.Entry(parent, textvariable=variable, width=14)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=(0, 8), pady=(0, 10))
        ttk.Button(
            parent,
            text="Pick",
            command=lambda var=variable: self.pick_color(var),
            style="Secondary.TButton",
        ).grid(row=row, column=column + 2, sticky="w", pady=(0, 10))

    def apply_accent_preset(self, color: str) -> None:
        self.primary_color_var.set(color)
        self.secondary_color_var.set(color)
        self.active_end_var.set(color)

    def pick_color(self, variable: tk.StringVar) -> None:
        selected = colorchooser.askcolor(color=variable.get() or "#89dceb", parent=self.root)
        if selected and selected[1]:
            variable.set(selected[1])

    def refresh_wallpaper_choices(self) -> None:
        self.paths.wallpaper_dir.mkdir(parents=True, exist_ok=True)
        wallpapers = []
        for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            wallpapers.extend(sorted(self.paths.wallpaper_dir.glob(pattern)))
            wallpapers.extend(sorted(self.paths.wallpaper_dir.glob(pattern.upper())))
        values = [self.format_wallpaper_value(path) for path in sorted(set(wallpapers))]
        current = self.wallpaper_var.get().strip()
        if current and current not in values:
            values.insert(0, current)
        if self.wallpaper_combo is not None:
            self.wallpaper_combo["values"] = values

    def format_wallpaper_value(self, path: Path) -> str:
        resolved = path.resolve()
        repo_wallpaper_dir = repo_root() / "wallpapers"
        if self.paths.root == repo_root() / "config" and resolved.parent == repo_wallpaper_dir.resolve():
            return f"@HYPRCAT_CONFIG_DIR@/wallpapers/{resolved.name}"
        return str(resolved)

    def import_wallpaper(self) -> None:
        source = filedialog.askopenfilename(
            parent=self.root,
            title="Import wallpaper",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.webp"),
                ("All files", "*.*"),
            ],
        )
        if not source:
            return

        source_path = Path(source).expanduser().resolve()
        self.paths.wallpaper_dir.mkdir(parents=True, exist_ok=True)
        destination = self.paths.wallpaper_dir / source_path.name
        if destination.exists() and destination.resolve() != source_path:
            suffix = 1
            while True:
                candidate = destination.with_name(f"{destination.stem}-{suffix}{destination.suffix}")
                if not candidate.exists():
                    destination = candidate
                    break
                suffix += 1
        if destination.resolve() != source_path:
            shutil.copy2(source_path, destination)

        self.wallpaper_var.set(self.format_wallpaper_value(destination))
        self.refresh_wallpaper_choices()

    def load(self) -> None:
        hyprland_text = read_text(self.paths.hyprland)
        hyprlock_text = read_text(self.paths.hyprlock)
        theme_text = read_text(self.paths.theme)
        apps_text = read_text(self.paths.apps)
        keybinds_text = read_text(self.paths.keybinds)

        self.wallpaper_var.set(parse_wallpaper_path(hyprlock_text))
        self.refresh_wallpaper_choices()
        self.animation_enabled_var.set(parse_animation_enabled(hyprland_text))
        self.animation_multiplier_var.set(parse_animation_multiplier(hyprland_text))

        cursor_theme, cursor_size = parse_cursor(hyprland_text)
        self.cursor_theme_var.set(cursor_theme)
        self.cursor_size_var.set(cursor_size)

        active_start, active_end, inactive = parse_border_colors(hyprland_text)
        self.active_start_var.set(active_start)
        self.active_end_var.set(active_end)
        self.inactive_border_var.set(inactive)

        self.primary_color_var.set(parse_theme_color(theme_text, "$m3_primary"))
        self.secondary_color_var.set(parse_theme_color(theme_text, "$m3_secondary"))

        for label, variable_name in APP_VARIABLES.items():
            self.app_vars[label].set(parse_variable(apps_text, variable_name))

        shortcuts = parse_shortcuts(keybinds_text, self.shortcut_targets)
        for label, variable in self.shortcut_vars.items():
            variable.set(shortcuts.get(label, ""))

        self.status_var.set("Loaded current settings.")

    def save(self) -> None:
        try:
            cursor_size = int(self.cursor_size_var.get())
            if cursor_size < 16 or cursor_size > 64:
                raise ValueError("Cursor size must be between 16 and 64.")
            wallpaper_value = self.wallpaper_var.get().strip()
            if not wallpaper_value:
                raise ValueError("Wallpaper cannot be empty.")
            for variable in (
                self.active_start_var,
                self.active_end_var,
                self.inactive_border_var,
                self.primary_color_var,
                self.secondary_color_var,
            ):
                normalize_hex_color(variable.get())
            shortcut_values = {label: variable.get() for label, variable in self.shortcut_vars.items()}
            for combo in shortcut_values.values():
                split_combo_string(combo)
        except ValueError as exc:
            messagebox.showerror("Invalid settings", str(exc), parent=self.root)
            return

        hyprland_text = read_text(self.paths.hyprland)
        hyprlock_text = read_text(self.paths.hyprlock)
        theme_text = read_text(self.paths.theme)
        apps_text = read_text(self.paths.apps)
        keybinds_text = read_text(self.paths.keybinds)

        hyprland_text = set_animation_multiplier(
            hyprland_text,
            self.animation_multiplier_var.get(),
            self.animation_enabled_var.get(),
        )
        hyprland_text = set_cursor(
            hyprland_text,
            self.cursor_theme_var.get().strip(),
            cursor_size,
        )
        hyprland_text = set_border_colors(
            hyprland_text,
            self.active_start_var.get(),
            self.active_end_var.get(),
            self.inactive_border_var.get(),
        )

        theme_text = set_theme_color(theme_text, "$m3_primary", self.primary_color_var.get())
        theme_text = set_theme_color(theme_text, "$m3_secondary", self.secondary_color_var.get())
        hyprlock_text = set_wallpaper_path(hyprlock_text, wallpaper_value)

        for label, variable_name in APP_VARIABLES.items():
            apps_text = set_variable(apps_text, variable_name, self.app_vars[label].get().strip())

        keybinds_text = set_shortcuts(keybinds_text, shortcut_values, self.shortcut_targets)

        write_text(self.paths.hyprland, hyprland_text)
        write_text(self.paths.hyprlock, hyprlock_text)
        write_text(self.paths.theme, theme_text)
        write_text(self.paths.apps, apps_text)
        write_text(self.paths.keybinds, keybinds_text)

        run_hyprctl("reload")
        run_hyprctl("setcursor", self.cursor_theme_var.get().strip(), str(cursor_size))
        apply_wallpaper(self.paths.data_root)

        self.status_var.set("Saved. Hyprland reload and wallpaper apply were requested.")
        messagebox.showinfo("Saved", "Settings saved successfully.", parent=self.root)


def main() -> None:
    root = tk.Tk()
    SettingsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
