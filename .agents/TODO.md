# GGate — working backlog

Consolidated from the root `TODO` file, inline `# TODO` markers, and agy's project scan.
Status legend: `[ ]` open · `[~]` in progress · `[x]` done. Items marked **(verify)** are
from the scan, confirm against current code first. Owner model: Claude specs → agy
implements → Claude reviews.

## ✅ Fixed this session (working tree, uncommitted since `b87a01a`)

App now launches and is usable. Changes not yet committed:
- [x] **App launches on GTK4/libadwaita** — imported/instantiated `StatusDisplay`
  (`statusbar`); `add-net.png` → `list-add-symbolic` placeholder.
- [x] **Main window chrome → `Adw.ToolbarView`** (`add_top_bar` + `set_content`); removed
  the unsupported `set_titlebar`/`set_child`.
- [x] **PropertyWindow API drift fixed** — `set_component`→`show_properties(comp, parent)`;
  `present(parent)`; `hide()`→`close()`; removed `set_transient_for`/`set_hide_on_close`/
  `set_modal` and the destroy-and-recreate-on-hide block; removed duplicate signal connects.
- [x] **PropertyWindow `closed` signal** (was `close-request`) + `vbox`/`component` init.
- [x] **Adw row signals** — `ComboRow`→`notify::selected`, `SpinRow`→`notify::value`.
- [x] **Float SpinRow crash** — proper positive `step` + `set_digits` (was passing digits as step → step 0 → NULL).
- [x] **PropertyGroup builder** — dropped `get_children()` (use a per-group count) and fixed
  the group-assignment bug that dropped the first control of each group / desynced
  `prop_controls`.
- [x] **AlertDialogs close crash** — `add_responses(*…)` → loop `add_response(id, label)`.
- [x] **Simulation `IndexError`** — `net_levels` now sized to `net_connections` in
  `analyze_net_connections` + `initialize_logic`; also fixed `Exporter` calling the
  non-existent `analyze_connections()`.
- [x] **Context-menu positioning** — use `translate_coordinates` (drawingarea→parent)
  instead of manual scroll subtraction; menu now lands at the cursor.
- [x] **Feature: content centering** on app start / new / open (center on component bbox,
  or canvas middle when empty).
- [x] **Feature: auto-center on resize** + Preferences toggle (`autocenter_resize`, default ON).

## P0 — still open

- [ ] **`bin/ggate.in` missing imports** (`gi`/`Gio`/`os`). `bin/ggate.in:16`. Not hit yet
  (we run via `run.py`), but breaks installed launch. **(verify)**
- [ ] **Version mismatch** — `pyproject.toml`/`meson.build` say `5.0.0`; `config.py`/
  `__init__.py` hardcode `4.0.0`. Pick one source of truth (meson `configure_file` → `config.py`).
- [ ] **`About.py` not wired** — `AboutGGate.create()` never imported/instantiated/presented;
  add an `app.about` action that builds + `present(window)`s it. Duplicate `set_comments`
  call in `About.py`. (Crash not hit at startup; will hit when About is invoked.)

## P1 — micro-windows / polish

### `Windows/Properties.py`
- [ ] Rebuilds all widgets + re-`present()` on every `show_properties`; old children leak.
  Consider building once / reusing, and an `Adw.ToolbarView` layout for the dialog itself.
- [x] ~~`set_width_chars` on `Adw.EntryRow`~~ — **not a bug**: `EntryRow` implements
  `GtkEditable`, which provides `set_width_chars`. Left as-is (no crash).

### `MainFrame` window chrome
- [ ] **`Gtk.HeaderBar` vs `Adw.HeaderBar`** — header is `Gtk.HeaderBar` with
  `set_use_native_controls(True)` (native macOS controls). Works in `ToolbarView`;
  `Adw.HeaderBar` would integrate better but drop native controls. Design call.

### Centering
- [ ] **Initial centering is gated by the resize preference** — when `autocenter_resize` is
  OFF, the first-paint centering at startup is also skipped (corner instead of centered).
  Spec was "initial always, resize gated." Split initial-vs-resize if we want it strict.

### `Windows/Preferences.py`
- [ ] Still subclasses deprecated `Gtk.Dialog`. Candidate migration to
  `Adw.PreferencesDialog`. **Confirm scope with PM first.**
- [ ] `:24` `# todo: fix font picker`.

### `Windows/TimingGraph/Display.py` + `Diagram.py`
- [ ] `Display` never adds the diagram canvas as a child → blank dialog; `.present()`
  called without a parent. **(verify)**
- [ ] `Diagram` never registers `name_area_draw_fn` / `chart_area_draw_fn` via
  `set_draw_func()` → draw fns never run. **(verify)**
- [ ] Diagram TODOs (`:135,:148,:170,:179,:210`): stroke/fill colors, name-area border,
  division strokes, text color, tick colors.

### Minor watch-items
- [ ] `AlertDialogs` is one instance that re-adds the same response IDs every time an alert
  opens → may emit a duplicate-response warning on the 2nd+ alert. Not a crash.

## P2 — dead code / hygiene

- [ ] **Proper GTK icon asset management (replaces the `_get_icon_path` `__file__` hack).**
  Context-menu `verb-icon` + toolbar action icons must be **themed icon names** via the icon
  theme, not filesystem paths. Approach: (1) bundle action SVGs in gresource at a clean
  freedesktop layout (`<base>/scalable/actions/<name>.svg`); (2) register on the icon theme
  at startup — `Gtk.IconTheme.get_for_display(display).add_resource_path("<base>")` —
  replacing the vestigial `themed_icons.add_search_path(config.DATADIR + "/images")`;
  (3) reference icons by name in `MenuPopover.menu_xml` and delete `_get_icon_path`.
  Requires fixing the gresource manifest (`dev-resources.xml`, `resources.xml.in`, maybe
  `meson.build`) — currently nested under `…/scalable/actions/` then re-filed as `actions/*`
  (double "actions") and `components/*` (misfiled) — and a dev-vs-release-aware resource base
  in `config`. Scope TBD: action icons only, or also component palette. The current
  `_get_icon_path` is a temporary dev-only patch.
- [ ] Remove GTK3 leftovers: `ggate/TimingDiagramWindow.py`, `ggate/DiagramArea.py`
  (confirm no imports first). `DiagramArea.py:205` TODO.
- [ ] `ggate/Components/Managers/Exporter.py` is a dead stub; real exporter is
  `ggate/Exporter.py`. Remove stub or consolidate.
- [ ] Commented-out translator-credits block `MainFrame.py:~569-570`; commented gnome
  post-install in `meson.build:59-63`.
- [ ] Style inconsistency: 2-space vs 4-space indent; mixed quotes; stale
  `indent-tabs-mode: t` headers. (Convention: double quotes, no comments.)

## P3 — feature backlog

- [ ] Animate logic circuit.
- [ ] **Native SVG icon set (gemini to build later).** Check for a usable open/licensed pack;
  if none fits (logic-gate symbols are domain-specific), author SVGs matching the existing
  `data/images/**.svg` style. Scope: PNG-only component icons
  (`led, not, osc, probe, sw, tribuff, vdd, xor`) + the toolbar icons (`add-net`,
  `add-component`, currently a `list-add-symbolic` placeholder). Consider rendering component
  icons from each component's Cairo `drawComponent` via `cairo.SVGSurface`.

## Other inline TODOs

- [ ] `Managers/Alerts.py:8`, `MainFrame.py:374` — i18n/translations.
- [ ] `Managers/FileManager.py:104` — implement schematics export.
- [ ] `MainFrame.py:491` — toast on clipboard parse failure.
- [ ] `DrawArea.py:516` — optimize redraw.
