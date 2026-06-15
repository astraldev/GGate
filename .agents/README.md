# `.agents/` — agent working docs for GGate

Index of the working docs and reference material agents use on GGate
(logic-circuit simulator, **GTK 4 + libadwaita**, heavy **Cairo** canvas).

## Directory map

- `TODO.md` — working backlog (P-levels; Done at the bottom).
- `plans/` — forward-looking implementation plans (icons).
- `skills/` — actionable how-to: `developing-gtk-apps.md` (architecture/plumbing),
  `designing-gnome-ui.md` (HIG), `glc-format/SKILL.md` (authoring `.glc` circuits;
  self-contained, portable to external models).
- `reference/` — `delegation-brief.md` (read first when delegating: repo facts,
  conventions, verification) and `build-system-analysis.md` (build audit).
- `gtk4/` — raw GTK4/libadwaita/Pango/Gio/Cairo API docs by namespace; index at
  `gtk4/README.md`.

## GTK4 documentation database — how to use

Scoped to the widgets/APIs this project actually uses, not the whole toolkit, so an
agent can continue UI work without re-deriving it from scratch.

1. **Architecture / plumbing question** (lifecycle, threading, GSettings, actions,
   packaging, "app crashes/freezes") → `skills/developing-gtk-apps.md`.
2. **UI / widget choice / HIG / "which widget, how to lay it out"** →
   `skills/designing-gnome-ui.md`.
3. **Exact API of a widget already chosen** (constructor, methods, signals, gotchas)
   → the relevant file in `gtk4/`. Start at `gtk4/README.md` for the index.

Always prefer these over guessing. For anything version-sensitive or not covered,
confirm against the canonical docs:

- Libadwaita 1.x: https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/
- GTK 4: https://docs.gtk.org/gtk4/
- PyGObject: https://api.pygobject.gnome.org/  •  PyCairo: https://pycairo.readthedocs.io/

## Project context (why these widgets)

- **The canvas is the app.** `Gtk.DrawingArea` + Cairo draw every gate, wire, and the
  new timing-waveform graph. `gtk4/drawing-cairo.md` is the most load-bearing file here.
- **Input = event controllers**, not legacy signals: `GestureClick`,
  `EventControllerMotion/Key/Focus` drive placing/dragging/selecting components.
- **Dialogs are migrating to libadwaita**: the rewritten `PropertyWindow`
  (`ggate/Components/Windows/Properties.py`) uses `Adw.Dialog` + boxed-list rows +
  `Adw.Banner` for inline validation. See `gtk4/adwaita/`.
- **Text on canvas = Pango**, measured/rendered through Cairo. See `gtk4/pango/`.

## Layout

`gtk4/` holds the **raw canonical HTML reference pages** (one per class), fetched from
the official docs — read them directly. They are grouped by namespace:

| Path | Source | Pages |
|------|--------|-------|
| `gtk4/README.md`     | (navigation index) widget → where used in GGate → which file | — |
| `gtk4/adwaita/`      | libadwaita 1.x — gnome.pages.gitlab.gnome.org/libadwaita | 17: Dialog, Application(Window), Preferences{Page,Group}, EntryRow, SpinRow, ComboRow, SwitchRow, Banner, StatusPage, HeaderBar, AboutDialog, AlertDialog, ResponseAppearance, Toast, ToastOverlay |
| `gtk4/gtk/`          | GTK 4 — docs.gtk.org/gtk4 | 35: DrawingArea, Box, Label, Image, ScrolledWindow, ListBox(Row), Frame, Paned, Button, MenuButton, ToggleButton, SpinButton, CheckButton, ComboBox(Text), Color/FontDialog(Button), PopoverMenu, Gesture/EventController*, FileDialog, FileFilter, StringList, ListStore, CellRendererText, Builder, Window, HeaderBar, ActionBar |
| `gtk4/pango/`        | Pango — docs.gtk.org/Pango | 2: Layout, FontDescription |
| `gtk4/gio/`          | GIO — docs.gtk.org/gio | 2: SimpleAction, ListStore |
| `gtk4/cairo/`        | PyCairo — pycairo.readthedocs.io | 4: context, surfaces, patterns, matrix |

`skills/` holds three installable skills as authored guidance (not raw docs):

| File | Covers |
|------|--------|
| `skills/developing-gtk-apps.md` | App architecture, lifecycle, threading, GSettings, packaging |
| `skills/designing-gnome-ui.md`  | GNOME HIG, widget selection, UI polish |
| `skills/glc-format/SKILL.md`    | GGate GLC circuit file format specification and catalog |

> Pages are full HTML (nav chrome included) — read the class's *Constructors / Methods /
> Properties / Signals* sections. To refresh or add a class, curl the canonical URL, e.g.
> `curl -sL https://docs.gtk.org/gtk4/class.<Name>.html -o gtk4/gtk/<Name>.html`
> (libadwaita: `.../libadwaita/doc/1-latest/class.<Name>.html`).

## Cross-cutting rules (do not violate)

- **GTK is single-threaded.** Touch widgets only on the main thread; marshal with
  `GLib.idle_add(...)`. (Cairo draw funcs already run on the main thread.)
- **GTK 4 has no `show_all()`** — widgets are visible by default; use `set_visible()`.
- **No `container.add()`** — use `box.append()`, `set_child()`, `Adw.PreferencesGroup.add()`.
- **Dialogs**: prefer `Adw.Dialog`/`Adw.AlertDialog` (adaptive, `.present(parent)`) over
  `Gtk.Dialog`/`Gtk.MessageDialog` (deprecated in GTK 4.10).
- **File chooser**: prefer async `Gtk.FileDialog` (4.10+) over `Gtk.FileChooserDialog`.
