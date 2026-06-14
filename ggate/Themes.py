import cairo
import json
import os
from gi.repository import Gio, Adw, Gtk, Gdk, GLib


def hex_to_pattern(hex_color: str) -> cairo.SolidPattern:
    h = hex_color.lstrip("#")
    if len(h) == 8:
        r, g, b, a = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4, 6))
    elif len(h) == 6:
        r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        a = 1.0
    else:
        return cairo.SolidPattern(0.0, 0.0, 0.0)
    return cairo.SolidPattern(r, g, b, a)


class Theme:
    def __init__(self, name: str, dark_chrome: bool, accent_hex: str, colors: dict):
        self.name = name
        self.dark_chrome = dark_chrome
        self.accent_hex = accent_hex
        self.colors = colors

    def get_pattern(self, key: str) -> cairo.SolidPattern:
        hex_val = self.colors.get(key)
        if not hex_val:
            return cairo.SolidPattern(0.0, 0.0, 0.0)
        return hex_to_pattern(hex_val)


THEME_REGISTRY: dict[str, Theme] = {}


def init_registry(is_dev_mode: bool = False) -> None:
    THEME_REGISTRY.clear()

    prefix = "/org/astralco/GGate/Dev/themes" if is_dev_mode else "/org/astralco/GGate/themes"

    try:
        children = Gio.resources_enumerate_children(prefix, Gio.ResourceLookupFlags.NONE)
        for child in children:
            path = f"{prefix}/{child}"
            try:
                data_bytes = Gio.resources_lookup_data(path, Gio.ResourceLookupFlags.NONE)
                data_str = data_bytes.get_data().decode("utf-8")
                data = json.loads(data_str)
                theme = Theme(
                    name=data["name"],
                    dark_chrome=bool(data.get("dark_chrome", True)),
                    accent_hex=data.get("accent_hex", "#ffffff"),
                    colors=data["colors"],
                )
                THEME_REGISTRY[theme.name] = theme
            except (KeyError, ValueError, json.JSONDecodeError):
                pass
    except GLib.Error:
        pass

    _load_user_themes()


def _load_user_themes() -> None:
    from ggate.const import definitions
    themes_dir = os.path.join(definitions.config_path, "themes")
    if not os.path.isdir(themes_dir):
        return
    for fname in os.listdir(themes_dir):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(themes_dir, fname)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            theme = Theme(
                name=data["name"],
                dark_chrome=bool(data.get("dark_chrome", True)),
                accent_hex=data.get("accent_hex", "#ffffff"),
                colors=data["colors"],
            )
            THEME_REGISTRY[theme.name] = theme
        except (KeyError, ValueError, OSError):
            pass


def apply_theme(name: str, preference_module) -> None:
    theme = THEME_REGISTRY.get(name)
    if theme is None:
        return
    for key, hex_val in theme.colors.items():
        pat = hex_to_pattern(hex_val)
        rgba = pat.get_rgba()
        if rgba[3] < 1.0:
            preference_module.__setattr__(key, f"{rgba[0]},{rgba[1]},{rgba[2]},{rgba[3]}")
        else:
            preference_module.__setattr__(key, f"{rgba[0]},{rgba[1]},{rgba[2]}")
    preference_module.__setattr__("theme", name)
    preference_module.save_settings()


def apply_chrome(name: str, display: Gdk.Display) -> None:
    theme = THEME_REGISTRY.get(name)
    if theme is None:
        return

    scheme = Adw.ColorScheme.PREFER_DARK if theme.dark_chrome else Adw.ColorScheme.DEFAULT
    Adw.StyleManager.get_default().set_color_scheme(scheme)

    css = (
        f"@define-color accent_color {theme.accent_hex};"
        f"@define-color accent_bg_color {theme.accent_hex};"
    )
    provider = Gtk.CssProvider()
    provider.load_from_string(css)
    Gtk.StyleContext.add_provider_for_display(
        display,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )
