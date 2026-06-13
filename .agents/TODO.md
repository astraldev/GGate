# GGate — working backlog

Consolidated from the root `TODO` file, inline `# TODO` markers, and agy's project scan
(session d60b8a4c). Status legend: `[ ]` open · `[~]` in progress · `[x]` done.
Items marked **(verify)** are from the scan and should be confirmed against current code
before agy acts. Owner model: Claude specs → agy implements → Claude reviews.

## P0 — broken integration (app likely won't run clean)

- [ ] **`bin/ggate.in` missing imports** — uses `Gio.Resource.load()` and `os.path.join()`
  without importing `gi`/`Gio`/`os`. `bin/ggate.in:16`. **(verify)**
- [ ] **Version mismatch** — `pyproject.toml` + `meson.build` say `5.0.0`; `ggate/config.py`
  + `ggate/__init__.py` hardcode `4.0.0`. Pick one source of truth (ideally meson
  `configure_file` → `config.py`). **(verify)**
- [ ] **`MainFrame` → `PropertyWindow` API drift** — MainFrame calls window-only methods
  (`set_transient_for`/`set_hide_on_close`/`set_modal`/`destroy`) and `set_component()` on
  an `Adw.Dialog` subclass that no longer has them (now `show_properties`). `Adw.Dialog`
  uses `.present(parent)`. `MainFrame.py:~564`. **(verify — branch diff already removed
  some of these; confirm what remains)**
- [ ] **`MainFrame.about_dialog` never created** — `self.about_dialog.present()` called but
  the object is never instantiated; `AboutGGate` (`Windows/About.py`) is not imported.
  `MainFrame.py:~335`. Wire `AboutGGate.create()` + an `app.about` action.
- [ ] **`MainFrame.statusbar` never created** — appended at `MainFrame.py:~295` but never
  instantiated; `StatusDisplay` not imported. **(verify)**

## P1 — micro-windows cleanup (current focus)

### `Windows/Properties.py` (PropertyWindow) — grounded against `.agents/gtk4/adwaita/`
- [ ] `close-request` signal doesn't exist on `Adw.Dialog` → use `closed`. (`:30`)
- [ ] `self.vbox` / `self.component` read before being set in `__init__` → init to `None`.
- [ ] `Adw.ComboRow` has no `changed` signal → `notify::selected`. (`:133`)
- [ ] `Adw.SpinRow` has no `changed` signal → `notify::value`. (`:146`, `:159`)
- [ ] `Adw.EntryRow` has no `set_width_chars` → remove (it's a `Gtk.Entry` method). (`:167`)
- [ ] Float `SpinRow.new_with_range(min,max,step)` passes digit-count as *step* and never
  calls `set_digits`. Separate step from digits. (`:149-154`)
- [ ] Group-assignment logic drops the first control of each group (creates the group but
  neither adds the widget nor appends to `prop_controls`), desyncing `prop_controls` from
  value indices. (`:176-194`)
- [ ] `Adw.PreferencesGroup` has no `get_children()` → `AttributeError`. (`:206`)
- [ ] Rebuilds all widgets + `present()` on every `show_properties`; old children leak.
  Consider `Adw.ToolbarView` (top bar + content) over manual `HeaderBar`-in-`Box`.

### `MainFrame` window chrome
- [ ] App now launches (header moved into a content `Gtk.Box` + `set_content`, since
  `Adw.ApplicationWindow` has no `set_titlebar`/`set_child`). Refinement: use the idiomatic
  `Adw.ToolbarView` (`add_top_bar(header)` + `set_content(body)`) instead of the plain box.

### `Windows/About.py`
- [ ] Not wired into MainFrame (see P0). Duplicate `set_comments` call. `:21` TODO:
  release notes / support url / debug info.

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

## P2 — dead code / hygiene

- [ ] Remove GTK3 leftovers: `ggate/TimingDiagramWindow.py`, `ggate/DiagramArea.py`
  (confirm no imports first). `DiagramArea.py:205` TODO.
- [ ] `ggate/Components/Managers/Exporter.py` is a dead stub; real exporter is
  `ggate/Exporter.py`. Remove stub or consolidate.
- [ ] Commented-out translator-credits block `MainFrame.py:~569-570`; commented gnome
  post-install in `meson.build:59-63`.
- [ ] Style inconsistency: 2-space vs 4-space indent across files; mixed single/double
  quotes; stale `indent-tabs-mode: t` magic header comments while code uses spaces.
  (Convention per `.vscode/copilot-instructions.md`: double quotes, no comments.)

## P3 — feature backlog (from root `TODO`)

- [ ] Animate logic circuit.
- [ ] **Native SVG icon set (gemini to build later).** First check for a usable
  open/licensed icon pack; if none fits (logic-gate symbols are domain-specific), have
  gemini author SVGs matching the existing `data/images/**.svg` style. Scope: PNG-only
  component icons (`led, not, osc, probe, sw, tribuff, vdd, xor`) + the deleted toolbar
  icons (`add-net`, `add-component`, currently a `list-add-symbolic` placeholder in
  `set_up_action_bar`). Consider rendering component icons from each component's Cairo
  `drawComponent` via `cairo.SVGSurface` (self-maintaining, matches the canvas).

## Other inline TODOs

- [ ] `Managers/Alerts.py:8`, `MainFrame.py:374` — i18n/translations.
- [ ] `Managers/FileManager.py:104` — implement schematics export.
- [ ] `MainFrame.py:491` — toast on clipboard parse failure.
- [ ] `DrawArea.py:516` — optimize redraw.
