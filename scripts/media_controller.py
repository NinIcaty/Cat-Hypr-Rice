#!/usr/bin/env python3
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gdk, GLib, Gtk, Pango  # noqa: E402


def run_playerctl(args: list[str]) -> str:
    result = subprocess.run(
        ["playerctl", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def format_seconds(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


class MediaController(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="Media Controller")
        self.set_default_size(360, 168)
        self.set_resizable(False)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_position(Gtk.WindowPosition.CENTER)

        screen = Gdk.Screen.get_default()
        if screen is not None:
            visual = screen.get_rgba_visual()
            if visual is not None and screen.is_composited():
                self.set_visual(visual)

        self.dragging = False
        self.duration = 0.0

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"""
            window {
              background: rgba(17, 17, 27, 0.88);
              border: 1px solid rgba(202, 214, 255, 0.32);
              border-radius: 22px;
            }
            #card {
              background: linear-gradient(180deg, rgba(30, 30, 46, 0.98), rgba(24, 24, 37, 0.98));
              border-radius: 22px;
              padding: 16px;
            }
            #title {
              color: #cdd6f4;
              font-size: 15px;
              font-weight: 700;
            }
            #subtitle,
            #time {
              color: #9399b2;
              font-size: 12px;
            }
            scale trough {
              min-height: 8px;
              background: rgba(108, 112, 134, 0.24);
              border-radius: 999px;
            }
            scale highlight {
              background: linear-gradient(90deg, #89dceb, #cad6ff);
              border-radius: 999px;
            }
            scale slider {
              min-width: 14px;
              min-height: 14px;
              background: #cad6ff;
              border-radius: 999px;
              border: 2px solid #11111b;
              margin: -4px 0;
            }
            button {
              background: rgba(49, 50, 68, 0.95);
              color: #cdd6f4;
              border: 1px solid rgba(202, 214, 255, 0.16);
              border-radius: 14px;
              padding: 10px 14px;
              box-shadow: none;
            }
            button:hover {
              background: rgba(69, 71, 90, 0.98);
            }
            button:disabled {
              color: rgba(147, 153, 178, 0.65);
            }
            """
        )
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.set_name("card")
        outer.set_border_width(16)
        self.add(outer)

        self.title_label = Gtk.Label(label="No active media")
        self.title_label.set_name("title")
        self.title_label.set_xalign(0)
        self.title_label.set_ellipsize(Pango.EllipsizeMode.END)

        self.subtitle_label = Gtk.Label(label="Start playback to use the controller")
        self.subtitle_label.set_name("subtitle")
        self.subtitle_label.set_xalign(0)
        self.subtitle_label.set_ellipsize(Pango.EllipsizeMode.END)

        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header.pack_start(self.title_label, False, False, 0)
        header.pack_start(self.subtitle_label, False, False, 0)
        outer.pack_start(header, False, False, 0)

        slider_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        slider_box.set_margin_top(14)
        outer.pack_start(slider_box, False, False, 0)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.set_draw_value(False)
        self.scale.connect("button-press-event", self.on_slider_press)
        self.scale.connect("button-release-event", self.on_slider_release)
        slider_box.pack_start(self.scale, False, False, 0)

        time_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.position_label = Gtk.Label(label="0:00")
        self.position_label.set_name("time")
        self.position_label.set_xalign(0)
        self.duration_label = Gtk.Label(label="0:00")
        self.duration_label.set_name("time")
        self.duration_label.set_xalign(1)
        time_row.pack_start(self.position_label, True, True, 0)
        time_row.pack_end(self.duration_label, False, False, 0)
        slider_box.pack_start(time_row, False, False, 0)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        buttons.set_margin_top(14)
        outer.pack_end(buttons, False, False, 0)

        self.prev_button = Gtk.Button(label="Previous")
        self.prev_button.connect("clicked", self.on_transport, "previous")
        buttons.pack_start(self.prev_button, True, True, 0)

        self.play_button = Gtk.Button(label="Play/Pause")
        self.play_button.connect("clicked", self.on_transport, "play-pause")
        buttons.pack_start(self.play_button, True, True, 0)

        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.on_transport, "next")
        buttons.pack_start(self.next_button, True, True, 0)

        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self.on_key_press)

        GLib.timeout_add(500, self.refresh)
        self.refresh()

    def on_key_press(self, _: Gtk.Widget, event: Gdk.EventKey) -> bool:
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def on_slider_press(self, *_args) -> bool:
        self.dragging = True
        return False

    def on_slider_release(self, *_args) -> bool:
        self.dragging = False
        target = self.scale.get_value()
        run_playerctl(["position", str(int(target))])
        self.refresh()
        return False

    def on_transport(self, _: Gtk.Button, action: str) -> None:
        run_playerctl([action])
        self.refresh()

    def set_enabled(self, enabled: bool) -> None:
        self.scale.set_sensitive(enabled)
        self.prev_button.set_sensitive(enabled)
        self.play_button.set_sensitive(enabled)
        self.next_button.set_sensitive(enabled)

    def refresh(self) -> bool:
        status = run_playerctl(["status"])
        if not status:
            self.title_label.set_text("No active media")
            self.subtitle_label.set_text("Start playback to use the controller")
            self.position_label.set_text("0:00")
            self.duration_label.set_text("0:00")
            self.scale.set_range(0, 1)
            self.scale.set_value(0)
            self.set_enabled(False)
            return True

        title = run_playerctl(["metadata", "title"]) or "Unknown track"
        artist = run_playerctl(["metadata", "artist"])
        player = run_playerctl(["metadata", "--format", "{{playerName}}"])
        duration_raw = run_playerctl(["metadata", "mpris:length"])
        position_raw = run_playerctl(["position"])

        subtitle_parts = [part for part in (artist, player, status) if part]
        self.title_label.set_text(title)
        self.subtitle_label.set_text("  •  ".join(subtitle_parts))
        self.set_enabled(True)

        try:
            self.duration = int(duration_raw) / 1_000_000 if duration_raw else 0.0
        except ValueError:
            self.duration = 0.0

        try:
            position = float(position_raw) if position_raw else 0.0
        except ValueError:
            position = 0.0

        self.position_label.set_text(format_seconds(position))
        self.duration_label.set_text(format_seconds(self.duration))
        self.play_button.set_label("Pause" if status == "Playing" else "Play")

        upper = max(1.0, self.duration if self.duration > 0 else position + 1)
        self.scale.set_range(0, upper)
        self.scale.set_increments(1, 10)

        if not self.dragging:
            self.scale.set_value(min(position, upper))

        return True


def main() -> None:
    window = MediaController()
    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
