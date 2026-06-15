#!/usr/bin/env python3
"""Procedurally capture a gallery of GGate previews — themes, playback, timing
diagram, preferences and properties — to ./gallery/.

Bootstraps exactly like run.py (compiles + registers the dev gresource, so themes
and icons load), then drives the real app through a sequence of "scenes", grabbing
an in-app snapshot of each (no external screenshot tool; X11 and Wayland both work).

Run on a real desktop session with GTK4/libadwaita:

    python3 build-aux/capture_screenshots.py

Must NOT run under a setuid/setgid shell (GTK refuses to init there).
"""

import os
import re
import sys
import unicodedata

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("PangoCairo", "1.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gdk, Gio, GLib, Adw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import run as ggate_run  # noqa: E402  (run.py's bootstrap helpers)
from ggate import Preference  # noqa: E402
from ggate.Themes import THEME_REGISTRY, apply_theme, apply_chrome  # noqa: E402
from ggate.MainFrame import GLogicApplication  # noqa: E402
from ggate.const import definitions as const  # noqa: E402
from ggate.Components.Windows.Preferences import PreferencesWindow  # noqa: E402

EXAMPLE = os.path.join(ROOT, "data", "examples", "oscillators.glc")
OUTDIR = os.path.join(ROOT, "gallery")
WINDOW_SIZE = (1280, 800)
SETTLE_MS = 800     # repaint/animation settle before a grab
GAP_MS = 350        # pause between scenes
RUN_SETTLE_MS = 2200  # let compute finish + playback start


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def snapshot(window, name):
    width, height = window.get_width(), window.get_height()
    if width <= 0 or height <= 0:
        print("skip (not realized):", name)
        return
    paintable = Gtk.WidgetPaintable.new(window)
    snap = Gtk.Snapshot.new()
    paintable.snapshot(snap, width, height)
    node = snap.to_node()
    if node is None:
        print("skip (empty node):", name)
        return
    texture = window.get_native().get_renderer().render_texture(node, None)
    path = os.path.join(OUTDIR, f"ggate-{name}.png")
    texture.save_to_png(path)
    print("saved", path)


def first_component(win):
    # prefer a component that actually has editable properties for a richer dialog
    comps = [c for c in win.circuit.components if c[0] != const.component_net]
    for c in comps:
        if getattr(c[1], "properties", None):
            return c
    return comps[0] if comps else None


def build_scenes(win):
    scenes = []

    # one canvas/palette shot per registered theme
    for name in THEME_REGISTRY:
        def setup(w, n=name):
            apply_theme(n, Preference)
            apply_chrome(n, Gdk.Display.get_default())
            # match the libadwaita chrome to the theme variant (screenshot only)
            scheme = Adw.ColorScheme.FORCE_LIGHT if "Light" in n else Adw.ColorScheme.FORCE_DARK
            Adw.StyleManager.get_default().set_color_scheme(scheme)
            w.drawarea.redraw = True
            w.drawarea.queue_draw()
        scenes.append({"name": f"theme-{slug(name)}", "setup": setup})

    # start a run -> playback bar visible
    scenes.append({
        "name": "playback",
        "setup": lambda w: w.toggle_run(),
        "settle": RUN_SETTLE_MS,
    })

    # timing diagram (history exists from the run above)
    scenes.append({
        "name": "timing-diagram",
        "setup": lambda w: w.timing_diagram.display(),
        "teardown": lambda w: w.timing_diagram.force_close(),
    })

    # stop the run, back to edit mode
    scenes.append({
        "name": None,
        "setup": lambda w: w.action_run.set_active(False),
    })

    # preferences dialog
    def open_prefs(w):
        w._gallery_prefs = PreferencesWindow(w)
        w._gallery_prefs.present(w)
    scenes.append({
        "name": "preferences",
        "setup": open_prefs,
        "teardown": lambda w: w._gallery_prefs.force_close(),
    })

    # properties dialog for the first real component
    def open_props(w):
        comp = first_component(w)
        if comp is not None:
            w.prop_window.show_properties(comp[1], w)
    scenes.append({
        "name": "properties",
        "setup": open_props,
        "teardown": lambda w: w.prop_window.dismiss(),
    })

    return scenes


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    # same bootstrap as run.py so the dev gresource (themes, icons) is live
    ggate_run.build_dev_resources()
    try:
        Gio.Resource.load(os.path.join(ROOT, "dev-resources.gresource"))._register()
    except GLib.Error as exc:
        print("warning: could not register dev gresource:", exc)

    sys.argv = [sys.argv[0], EXAMPLE]  # MainFrame opens sys.argv[1] on startup
    app = GLogicApplication()

    def on_ready(_app):
        win = app.get_active_window()
        win.set_default_size(*WINDOW_SIZE)
        win.present()
        scenes = build_scenes(win)

        def run_scene(i):
            if i >= len(scenes):
                app.quit()
                return False
            scene = scenes[i]
            try:
                if scene.get("setup"):
                    scene["setup"](win)
            except Exception as exc:  # one bad scene shouldn't abort the gallery
                print(f"scene {scene['name']} setup failed:", exc)
            GLib.timeout_add(scene.get("settle", SETTLE_MS), lambda: capture(i))
            return False

        def capture(i):
            scene = scenes[i]
            try:
                if scene.get("name"):
                    snapshot(win, scene["name"])
                if scene.get("teardown"):
                    scene["teardown"](win)
            except Exception as exc:
                print(f"scene {scene['name']} capture failed:", exc)
            GLib.timeout_add(GAP_MS, lambda: run_scene(i + 1))
            return False

        GLib.timeout_add(900, lambda: run_scene(0))

    app.connect_after("activate", on_ready)
    app.run([sys.argv[0]])


if __name__ == "__main__":
    main()
