#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


TEXT_SUFFIXES = {
    ".conf",
    ".css",
    ".desktop",
    ".json",
    ".jsonc",
    ".md",
    ".py",
    ".rasi",
    ".ron",
    ".service",
    ".sh",
    ".txt",
}


def default_data_dir() -> Path:
    env = os.environ.get("PYPRLAND_DATA_DIR")
    if env:
        return Path(env).expanduser()
    return Path(__file__).resolve().parents[1]


def default_config_dir() -> Path:
    env = os.environ.get("PYPRLAND_CONFIG_DIR")
    if env:
        return Path(env).expanduser()
    xdg = os.environ.get("XDG_CONFIG_HOME")
    root = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return root / "pyprland"


def render_template(content: str, config_dir: Path, data_dir: Path) -> str:
    return (
        content.replace("@PYPRLAND_CONFIG_DIR@", str(config_dir))
        .replace("@PYPRLAND_DATA_DIR@", str(data_dir))
    )


def copy_file(source: Path, destination: Path, config_dir: Path, data_dir: Path, force: bool) -> None:
    if destination.exists() and not force:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix in TEXT_SUFFIXES:
        text = source.read_text(encoding="utf-8")
        destination.write_text(render_template(text, config_dir, data_dir), encoding="utf-8")
    else:
        shutil.copy2(source, destination)


def sync_tree(source_dir: Path, destination_dir: Path, config_dir: Path, data_dir: Path, force: bool) -> None:
    for source in sorted(source_dir.rglob("*")):
        relative = source.relative_to(source_dir)
        destination = destination_dir / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        copy_file(source, destination, config_dir, data_dir, force)


def bootstrap(data_dir: Path, config_dir: Path, force: bool) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    sync_tree(data_dir / "config", config_dir, config_dir, data_dir, force)
    sync_tree(data_dir / "wallpapers", config_dir / "wallpapers", config_dir, data_dir, force)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap the Pyprland user config.")
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
    parser.add_argument("--config-dir", type=Path, default=default_config_dir())
    parser.add_argument("--force", action="store_true", help="overwrite existing user config files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bootstrap(args.data_dir.expanduser().resolve(), args.config_dir.expanduser().resolve(), args.force)


if __name__ == "__main__":
    main()
