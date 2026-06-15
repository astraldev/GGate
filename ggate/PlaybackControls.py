from gi.repository import Gtk, Gdk

_CSS = """
.playback-bar { padding: 5px; }
.playback-bar button { min-height: 0; padding: 3px; }
"""

def _ensure_css():
    if getattr(_ensure_css, "_done", False):
        return
    provider = Gtk.CssProvider()
    provider.load_from_string(_CSS)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    _ensure_css._done = True

def _format_progress(current, total):
    # pick a session-stable unit from the total so width/unit never jump mid-playback
    if total >= 1:
        scale, unit = 1.0, "s"
    elif total >= 1e-3:
        scale, unit = 1e3, "ms"
    elif total >= 1e-6:
        scale, unit = 1e6, "µs"
    elif total > 0:
        scale, unit = 1e9, "ns"
    else:
        scale, unit = 1.0, "s"
    return f"{current * scale:6.2f} / {total * scale:6.2f} {unit}"

class PlaybackControls(Gtk.Box):
    def __init__(self, mainframe):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainframe = mainframe
        self.circuit = mainframe.circuit
        self.playback = self.circuit.playback
        self._suppress_seek = False
        _ensure_css()

        self.add_css_class("playback-bar")
        self.add_css_class("osd")
        self.add_css_class("toolbar")
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.END)
        self.set_margin_bottom(6)
        self.set_spacing(2)
        self.set_visible(False)

        # Stop button — fully ends the run via the header toggle
        self.stop_btn = Gtk.Button()
        self.stop_btn.add_css_class("flat")
        self.stop_img = Gtk.Image.new_from_icon_name("media-playback-stop-symbolic")
        self.stop_img.set_pixel_size(14)
        self.stop_btn.set_child(self.stop_img)
        self.stop_btn.connect("clicked", lambda btn: self.mainframe.action_run.set_active(False))
        self.append(self.stop_btn)

        # Restart button
        self.restart_btn = Gtk.Button()
        self.restart_btn.add_css_class("flat")
        self.restart_img = Gtk.Image.new_from_icon_name("view-refresh-symbolic")
        self.restart_img.set_pixel_size(14)
        self.restart_btn.set_child(self.restart_img)
        self.restart_btn.connect("clicked", lambda btn: self.playback.restart())
        self.append(self.restart_btn)

        # Play/Pause toggle
        self.play_btn = Gtk.Button()
        self.play_btn.add_css_class("flat")
        self.play_img = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
        self.play_img.set_pixel_size(14)
        self.play_btn.set_child(self.play_img)
        self.play_btn.connect("clicked", lambda btn: self.playback.toggle_play())
        self.append(self.play_btn)

        # Vertical divider separator
        self.divider = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.divider.set_margin_top(4)
        self.divider.set_margin_bottom(4)
        self.append(self.divider)

        # Seek scale
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.scale.set_hexpand(True)
        self.scale.set_size_request(140, -1)
        self.scale.set_draw_value(False)
        self.scale.connect("value-changed", self._on_scale_value_changed)
        self.append(self.scale)

        # Time label — fixed width + tabular figures so updates don't jiggle the bar
        self.time_label = Gtk.Label()
        self.time_label.add_css_class("numeric")
        self.time_label.set_width_chars(18)
        self.time_label.set_xalign(1.0)
        self.time_label.set_text("0.00 / 0.00 s")
        self.append(self.time_label)

        # Connect signals
        self.playback.connect("playback-state-changed", self._on_playback_state_changed)
        self.circuit.connect("currenttime-changed", self._on_current_time_changed)

    def _on_playback_state_changed(self, playback, state):
        if state in ("playing", "paused", "ended"):
            self.set_visible(True)
        else:
            self.set_visible(False)

        if state == "playing":
            self.play_img.set_from_icon_name("media-playback-pause-symbolic")
        else:
            self.play_img.set_from_icon_name("media-playback-start-symbolic")

        is_ready = state in ("playing", "paused", "ended")
        self.stop_btn.set_sensitive(True)
        self.play_btn.set_sensitive(is_ready)
        self.restart_btn.set_sensitive(is_ready)
        self.scale.set_sensitive(is_ready)

        if is_ready:
            total_frames = self.playback.frame_count()
            self.scale.set_range(0, max(0, total_frames - 1))
            self._update_time_label()

    def _update_time_label(self):
        self.time_label.set_text(_format_progress(self.circuit.current_time, self.circuit.total_time()))

    def _on_current_time_changed(self, circuit, t):
        self._suppress_seek = True
        self.scale.set_value(self.playback.playback_index)
        self._suppress_seek = False
        self._update_time_label()

    def _on_scale_value_changed(self, scale):
        if self._suppress_seek:
            return
        self.playback.seek(int(scale.get_value()))
