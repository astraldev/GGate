# CLAUDE.md — GGate

Reference page for working on GGate. Facts here come from a project scan; when in doubt,
read the cited file. Keep this current as the codebase changes.

## What GGate is

A **logic-circuit simulator** — desktop app, **Python + GTK 4 + libadwaita**, with a
**Cairo**-rendered editor canvas. Users place logic gates/components, wire them into nets,
and simulate. Circuit files are `.glc` (examples in `data/examples/`).

Requires: Python `>=3.10,<4`, `gtk4 >= 4.16`, `libadwaita-1 >= 1.6.8`. Runtime deps
(`pyproject.toml`): `pygobject`, `pycairo`, `python-igraph`, `shapely`, `packaging`,
`meson-python`. App ID `org.astralco.GGate` (dev: `org.astralco.GGate.Dev`).

## Working model

- **PM** (user): direction and priorities.
- **Claude** (me): senior dev / project owner — architecture, design, task breakdown,
  review, holding context. I spec the work and verify it; I don't hand-write feature code.
- **agy** (`mcp__agy-bridge__*`, Gemini): the implementer — writes/edits code from my specs.
  Also my recon tool (`delegate`/`analyze_files`) for read-only scans.

Loop: I decide *what* and *how* → write a self-contained delegation (file paths, exact
change, acceptance criteria, `.agents/` references, conventions) → agy implements → I review
the diff → iterate. **Every UI delegation cites the relevant `.agents/gtk4/` page** so agy
works from ground truth, not memory.

## Run flow

- **Dev**: `run.py` loads `./dev-resources.gresource`, instantiates `GLogicApplication`.
- **Installed**: Meson generates `bin/ggate.in` → loads `ggate-resources.gresource` from
  pkgdatadir, runs `GLogicApplication`.
- `GLogicApplication` (`Adw.Application`, in `MainFrame.py`) owns app actions (New/Open/
  Save/Preferences/Help/About…). `MainFrame` (`Adw.ApplicationWindow`, same file) builds
  the UI and wires the canvas, file managers, circuit model, palette, and dialogs.

## Architecture

- **Canvas / rendering** — `ggate/DrawArea.py`: `DrawArea` (a `Gtk.ScrolledWindow`) hosts a
  `Gtk.DrawingArea` with `set_draw_func(on_draw)`. All graphics (grid, components, nets,
  selection) are drawn with **Cairo** onto a cached offscreen surface, then blitted.
- **Circuit model** — `ggate/CircuitManager.py`: stores components/wires/state, undo
  history, snapping, net validation, simulation steps.
  - **igraph** in `analyze_net_connections()` — vertices = pin positions, edges = net
    segments; `graph.components()` resolves electrical connectivity.
  - **shapely** in `split_nets()` — `Point`/`LineString` hit-tests for clicks on nets.
- **Components** — `ggate/Components/LogicGates/`. All subclass `BaseComponent` (ABC in
  `SystemComponents.py`).
  - Abstract: `drawComponent`, `drawComponentEditOverlap`, `drawComponentRunOverlap`.
  - Common overrides: `propertyChanged` (validate; return `bool` or `PropertyError`),
    `calculate` (sim state), `initialize` (defaults).
  - `PropertyError(message, positions)` — error text + indices of invalid property rows
    (drives red highlight + banner in the properties dialog).
  - Concrete gates grouped under `Standard/`, `FlipFlops/`, `Counters/`, `StateViewers/`,
    `Miscellaneous/`. `Calculator.py` does gate computation.
- **Property typing** — `const.py` enums map to libadwaita rows in the properties dialog:
  `property_bool→SwitchRow`, `property_int→SpinRow`, `property_float→SpinRow(digits)`,
  `property_select→ComboRow`, `property_string→EntryRow`.

## Module map (`ggate/`)

| File | Responsibility |
|------|----------------|
| `MainFrame.py` | `GLogicApplication` + `MainFrame` window; actions, wiring |
| `DrawArea.py` | editor canvas (ScrolledWindow + DrawingArea + Cairo) |
| `CircuitManager.py` | circuit model: storage, history, nets (igraph/shapely), sim |
| `ComponentView.py` | side palette of placeable gate categories |
| `Exporter.py` | render schematic to Cairo image/PDF/PS/SVG (the **real** one) |
| `MenuPopover.py` | context popover menus |
| `Preference.py` | load/save user settings to disk |
| `StatusDisplay.py` | `Gtk.Label` subclass for status text |
| `Utils.py` | vector/text/Cairo helpers |
| `const.py` / `config.py` | constants & metadata / VERSION, APP_PREFIX, paths |
| `Components/Managers/` | `Alerts`, `FileManager`; `Exporter.py` here is a **dead stub** |
| `Components/Windows/` | dialogs — see below |
| `Components/Windows/TimingGraph/` | `Display` (dialog) + `Diagram` (Cairo waveform) |
| `TimingDiagramWindow.py`, `DiagramArea.py` | **dead** GTK3 leftovers |

## The dialogs (`Components/Windows/`)

| File | Class / base | Status |
|------|--------------|--------|
| `About.py` | `AboutGGate` → `Adw.AboutDialog` | built, **not wired** into MainFrame |
| `Preferences.py` | `PreferencesWindow` (`Gtk.Dialog`, deprecated) | wired, works |
| `Properties.py` | `PropertyWindow` (`Adw.Dialog`) | wired but **buggy** (API drift) |
| `TimingGraph/Display.py` | `Adw.Dialog` wrapper | wired but **broken** (empty/parent) |
| `TimingGraph/Diagram.py` | `Gtk.ScrolledWindow` + 2 `DrawingArea` | draw fns **not registered** |

These dialogs are the **current cleanup focus** — details and the grounded bug list live in
`.agents/TODO.md`.

## Build & packaging

- **Meson**: `meson.build` (deps, resource compile → `ggate-resources.gresource`,
  `install_subdir('ggate')`), `meson_options.txt`, `bin/ggate.in`, `data/images/` gresource.
- **Flatpak**: `build-aux/flatpak/org.astralco.GGate.json` (GNOME 47 runtime, pip deps).
- **Snap**: `build-aux/snapcraft/snapcraft.yaml` (`core22`, poetry deps, meson plugin).
- ⚠️ `config.py`/`__init__.py` versions are **static**, not Meson-populated, and currently
  **disagree** with `pyproject.toml`/`meson.build` (4.0.0 vs 5.0.0). See `.agents/TODO.md` P0.

## Conventions (enforce in review)

From `.vscode/copilot-instructions.md`, as amended by PM direction:
- **Comments (PM-amended):** *minimal inline comments* only, on genuinely non-obvious /
  "magic" code (a tricky index trick, a non-obvious workaround). NOT module/class/method
  docstrings, NOT line-by-line narration. Keep it sparse. Still no `// ...existing code...`
  placeholder markers.
- **No unused/dangling** imports or variables. **No extra** methods/types unless necessary.
- **Avoid deep nesting:** ~3 levels of nesting is the signal to extract a helper function.
  Prefer small focused functions + early returns over pyramids of `if`/`for`.
- **Double quotes** for strings, always. Match surrounding style; verify meticulously.
- Commits: **Conventional Commits, one-line subject.**

⚠️ The existing code violates some of this (mixed 2/4-space indent, mixed quotes, stale
`indent-tabs-mode: t` headers). New work should follow the rules above; don't propagate the
old inconsistency.

GTK4 rules (full list in `.agents/README.md`): single-threaded UI (`GLib.idle_add` to
marshal); no `show_all()`/`container.add()` (use `set_visible`/`append`/`set_child`); prefer
`Adw.Dialog`/`Adw.AlertDialog` over `Gtk.Dialog`/`Gtk.MessageDialog`; prefer `Gtk.FileDialog`
(4.10+) over `Gtk.FileChooserDialog`.

## Companion docs

- `.agents/README.md` — GTK4 docs database (60 canonical reference pages) + refresh recipe.
- `.agents/gtk4/` — raw HTML API docs by namespace (adwaita/gtk/pango/gio/cairo).
- `.agents/gtk4/README.md` — widget → where-used-in-GGate map.
- `.agents/skills/` — `developing-gtk-apps` (architecture) + `designing-gnome-ui` (HIG).
- `.agents/TODO.md` — the working backlog (P0–P3), grounded bug lists.
