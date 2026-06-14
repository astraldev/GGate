# Delegation Brief — GGate

Stable preliminary context for any implementer (subagent / agy) working on GGate.
Delegations reference this file instead of restating it. Read this first, then the
task-specific prompt.

## Repo
- Path / working dir: `/Users/ekureedem/Documents/Projects/GGate` (git repo, branch off `main`).
- Stack: Python `>=3.10`, GTK 4 (`>=4.16`), libadwaita (`>=1.6.8`), Cairo-rendered canvas.
- App IDs: `org.astralco.GGate` (installed), `org.astralco.GGate.Dev` (dev).
- Authoritative architecture notes: `CLAUDE.md` (read it). Working backlog: `.agents/TODO.md`.

## Conventions (enforced in review)
- Double quotes for strings, always.
- Minimal inline comments — single-line, only on genuinely non-obvious / "magic" code.
  NO docstrings, NO line-by-line narration, NO `# ...existing code...` markers.
- No unused/dangling imports or variables. No extra methods/types unless necessary.
- Avoid deep nesting: extract a helper at ~3 levels; prefer early returns.
- GTK4: single-threaded UI (`GLib.idle_add` to marshal); no `show_all()`/`container.add()`
  (use `set_visible`/`append`/`set_child`); prefer `Adw.Dialog`/`Adw.AlertDialog` and
  `Gtk.FileDialog`. Never call `set_size_request` inside a draw callback (layout loop).
- Commits: Conventional Commits, one-line subject. **Do NOT commit unless told.**

## Build & resources
- Meson is the build system. Resources compile to gresource bundles:
  - Dev: `run.py` loads `dev-resources.gresource` (from `data/images/dev-resources.xml`).
  - Installed: `ggate-resources.gresource` (from `data/images/resources.xml.in`, via
    `data/images/meson.build` which does dynamic XML generation — reuse that technique).
- Resource prefixes follow `/org/astralco/GGate/...` (installed) and
  `/org/astralco/GGate/Dev/...` (dev). Dev-vs-installed detection lives in `config.py`.
- New bundled assets MUST go through Meson + both gresource XMLs and load by resource
  path — never an absolute/relative filesystem path (breaks in venv/installed prefixes).
- Icon/asset gresource conventions are detailed in `.agents/plans/icon-creation.md`.

## Sandbox / verification
- GTK CANNOT headless-launch here (setuid sandbox blocks GTK init). Verify at LOGIC level:
  `python3 -c "import ast; ast.parse(open(p).read())"` per changed .py; `json.load` per
  JSON; small comparison scripts; `grep` assertions; `meson setup build`/`--reconfigure`
  if `meson` is on PATH (else paste the generated XML/meson snippets for review).

## Plans (specs live here)
- `.agents/plans/theming.md` — theming system (palettes §2, JSON schema §5).
- `.agents/plans/icon-creation.md` — icon generation + dynamic gresource/meson globbing.
- `.agents/plans/timing-diagram-revamp.md` — timing dialog rewrite (done; §7 draw-area).
- `.agents/plans/preferences-revamp.md`, `theming.md`, `component-animation.md`.

## Reporting
- Re-read current on-disk state before editing (prior partial work may exist).
- Report: per-task summary, files created/changed (precise paths), verification results,
  and anything deferred or uncertain. Do not commit.
