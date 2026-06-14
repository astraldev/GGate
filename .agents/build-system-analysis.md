# GGate Build & Packaging System Analysis

This document provides a read-only analysis of the GGate logic-circuit simulator's build, packaging, and runtime asset-handling configurations.

---

## 1. Meson Build Setup

### Description of Existing Setup
The project uses **Meson** as its primary build configuration system:
- **Root `meson.build`**: Defines the project `ggate` with version `5.0.0` and minimum Meson version `1.4.0`. 
  - It checks for external system dependencies: `pygobject-3.0`, `gtk4 >= 4.16.0`, and `libadwaita-1 >= 1.6.8`.
  - It uses python's `find_installation` module check to ensure that required library imports (`gi`, `cairo`, `packaging`, `igraph`, `shapely`) are present in the target Python environment.
  - It defines a `profile` option via `meson_options.txt`. If the profile is `development` (the default), the app-id is `org.astralco.GGate.Dev` and the resource prefix is `/org/astralco/GGate/Dev`. If `release`, the app-id is `org.astralco.GGate` and the prefix is `/org/astralco/GGate`.
  - It configures build variables via `configuration_data()` (setting `PYTHON`, `VERSION`, `bindir`, and `pkgdatadir`).
  - Python sources are installed recursively using `install_subdir('ggate')` directly into Python's `site-packages` directory. It uses a shell callout via `run_command` with Unix tools (`find` and `sed`) to compute which `__pycache__` directories to exclude, along with excluding `*.pyc`.
  - Commented-out post-install triggers for desktop files, schemas, and icon caches are present at the bottom.
- **`bin/meson.build`**: Uses `configure_file` to interpolate build variables into `bin/ggate.in`, yielding an executable python file `ggate` installed to the system binary directory (`bindir`) with execute permissions.
- **`data/images/meson.build`**: 
  - Generates `resources.xml` from `resources.xml.in` by dynamically inserting `@ICON_FILES@` (compiled from a list of SVGs in `components/` and `actions/`) and the profile-specific `@PREFIX@`.
  - Compiles the generated XML into a binary GResource bundle `ggate-resources.gresource` using `gnome.compile_resources` and installs it to the package data directory (`pkgdatadir`).
  - Directly copies raw SVGs into `pkgdatadir / 'icons'` via `install_subdir`.

### Issues, Inconsistencies & Risks
* **Issue 1.1: Brittle Python Cache Exclusion (Unix-dependent)**
  * **Severity**: `should-fix`
  * **Details**: Root `meson.build` calls a shell command (`find ggate -type d -name __pycache__ | sed ...`) to construct directory exclusion lists. This is not portable (will fail on Windows) and depends on the configuration-time state of the repository. If configured in a completely clean repository, no directories will be found, but subsequent builds or updates might generate cache files that bypass the exclusion because it was computed statically at configure time.
  * **Recommended Fix**: Rely on python's built-in packaging tools, or use Meson's native filesystem functions/Python helper script to filter directories portably.
* **Issue 1.2: Local Variable `prefix` Shadowing**
  * **Severity**: `nice-to-have`
  * **Details**: In root `meson.build`, a local variable is named `prefix` (used for GResource prefix paths). Meson has a built-in option `prefix` representing the installation base path (e.g. `/usr`). This naming overlap is confusing for developers.
  * **Recommended Fix**: Rename the local variable `prefix` to `gresource_prefix`.
* **Issue 1.3: Commented-out Post-Install Actions**
  * **Severity**: `should-fix`
  * **Details**: `gnome.post_install` is commented out. On direct system installs (e.g., Linux distro packaging), the desktop icon database, GLib schemas, and mime databases will not update immediately, requiring manual system restarts or command execution to display app icons.
  * **Recommended Fix**: Uncomment `gnome.post_install` and guard it so it only executes when not building for sandboxed targets (like Flatpak).

---

## 2. Entry Points

### Description of Existing Setup
There are two main entry points in GGate:
- **`run.py` (Development Mode)**: 
  - Initializes PyGObject requirements (`Gtk 4.0`, `PangoCairo 1.0`, `Adw 1`).
  - Loads the compiled resource bundle `./dev-resources.gresource` directly from the current working directory.
  - Registers the resource model with `resource._register()`.
  - Instantiates and runs `GLogicApplication`.
- **`bin/ggate.in` (Installed Mode)**:
  - Shebang is interpolated to point to the build environment's Python path.
  - Receives package datadir `@pkgdatadir@` via Meson template compilation.
  - Attempts to load resources from `os.path.join(pkgdatadir, "ggate-resources.gresource")` and register them.
  - Instantiates and runs `GLogicApplication`.

### Issues, Inconsistencies & Risks
* **Issue 2.1: Missing Imports in Installed Executable (Crash on Launch)**
  * **Severity**: `blocker`
  * **Details**: `bin/ggate.in` references `Gio.Resource` and `os.path.join` but fails to import the `Gio` repository or the standard `os` library. It only imports `gi` and `sys`. 
  * **Recommended Fix**: Add `import os` and `from gi.repository import Gio` to `bin/ggate.in`.
* **Issue 2.2: Inconsistent CLI `--version` Output**
  * **Severity**: `nice-to-have`
  * **Details**: `run.py` prints `GGate {__version__}` (no prefix letter), whereas `bin/ggate.in` prints `GGate: v{__version__}`.
  * **Recommended Fix**: Standardize the console formatting across both launcher files.

---

## 3. Resources & GResource Bundling

### Description of Existing Setup
- **`data/images/dev-resources.xml`**: Checked into git. Hardcodes the prefix `/org/astralco/GGate/Dev/data/icons/scalable/actions/`.
- **`data/images/resources.xml.in`**: Configured by Meson. Prefix template is `@PREFIX@/data/icons/scalable/actions/` (resolving to `/org/astralco/GGate/data/icons/scalable/actions/` in release).
- Both resource structures package:
  - Component SVGs (e.g. `components/7seg.svg`)
  - Action SVGs (e.g. `actions/flip-horizontal.svg`)

### Issues, Inconsistencies & Risks
* **Issue 3.1: Non-standard Path Hierarchy Breaking Icon-Theme Discovery**
  * **Severity**: `should-fix`
  * **Details**: Modern GTK4 apps rely on `Gtk.IconTheme` to automatically discover assets compiled into application GResource bundles under the standard Freedesktop structure: `/org/astralco/GGate/icons/hicolor/[size]/[context]/[name].[ext]`.
  GGate's resource structure breaks this in multiple ways:
    1. It introduces a redundant `data/` subdirectory (yielding `/data/icons/` instead of `/icons/`).
    2. It completely omits the theme directory (e.g. `hicolor`).
    3. It causes double-directory naming for action items (`.../scalable/actions/actions/flip-horizontal.svg`).
    4. It misfiles components under the action prefix path (`.../scalable/actions/components/7seg.svg`).
  Because of this layout, GTK's automatic icon theme lookup fails. The application is forced to resolve absolute file system paths or use custom workarounds to load images.
  * **Recommended Fix**: Redesign the GResource structure. Use standard Freedesktop folder hierarchies in the XML file (e.g. `@PREFIX@/icons/hicolor/scalable/actions/` and `@PREFIX@/icons/hicolor/scalable/devices/`) and use GResource `alias` attributes to strip directory prefixes from resource IDs (e.g., mapping `actions/rotate-left.svg` to the resource name `rotate-left.svg` under the actions prefix).

---

## 4. Configurations & Versioning

### Description of Existing Setup
- **`ggate/config.py`**: A static Python file. It defines the application version (`VERSION = "4.0.0"`), base application ID prefix (`APP_PREFIX = "org.astralco.GGate"`), and runtime directory path (`DATADIR = '/'.join(__file__.split("/")[:-1]) + '/'`).
- **`ggate/__init__.py`**: Hardcodes the package variable `__version__ = '4.0.0'`.
- **`GLogicApplication`**: Instantiated with `application_id="org.astralco.ggate"`.

### Issues, Inconsistencies & Risks
* **Issue 4.1: Out-of-sync Static Versions**
  * **Severity**: `should-fix`
  * **Details**: Versioning is hardcoded statically in `config.py` and `__init__.py` as `4.0.0`, while `meson.build` and `pyproject.toml` specify `5.0.0`. This discrepancy can break compatibility validation (`config.is_compatible`) and report inaccurate versions in package managers.
  * **Recommended Fix**: Make `config.py` a generated configuration file (e.g., `config.py.in` compiled by Meson's `configure_file`) to dynamically ingest version numbers from `meson.build` at compile time.
* **Issue 4.2: Application ID Casing Inconsistency**
  * **Severity**: `should-fix`
  * **Details**: 
    - The D-Bus ID and desktop filename expect `org.astralco.GGate` (CamelCase).
    - `GLogicApplication` initializes using the lowercase `org.astralco.ggate`.
    - Meson builds with `org.astralco.GGate` (or `org.astralco.GGate.Dev`).
    This mismatch breaks window management integration under Wayland (the compositor cannot match the window class to the desktop file, resulting in default fallback window icons) and prevents `Gtk.IconTheme` from automatically mapping resource paths.
  * **Recommended Fix**: Standardize on `org.astralco.GGate` (and `org.astralco.GGate.Dev` for dev profiles) across the GLogicApplication codebase and resource path naming.

---

## 5. `pyproject.toml` Build Configurations

### Description of Existing Setup
- Uses `meson-python` (backend `mesonpy`) for PEP-517 compliance.
- Defines package dependencies: `pycairo`, `pygobject`, `packaging`, `python-igraph`, `shapely`, and `meson-python`.
- Target python environment requires `>= 3.10, < 4.0`.

### Issues, Inconsistencies & Risks
* **Issue 5.1: Rigid `shapely` Dependency Version Pin**
  * **Severity**: `should-fix`
  * **Details**: In `pyproject.toml`, `shapely` is pinned exactly to `==2.1.1`. Strict equal pins in Python packages can cause install dependency conflicts on newer distributions or in setups that require slightly different micro-versions of shapely.
  * **Recommended Fix**: Relax the constraint to a compatible range, such as `shapely (>=2.1.1, <3.0.0)`.
* **Issue 5.2: Redundant Runtime Dependency**
  * **Severity**: `nice-to-have`
  * **Details**: `meson-python` is listed as a runtime dependency (`dependencies`) in addition to being a build-system requirement. It is not needed at runtime.
  * **Recommended Fix**: Remove `meson-python` from the runtime `dependencies` array.

---

## 6. Distribution Configurations

### Description of Existing Setup
- **Flatpak (`build-aux/flatpak/org.astralco.GGate.json`)**:
  - Targets GNOME 47 runtime environments.
  - Builds in two modules: standard `python-modules` (via pip) and the root `ggate` repository (via Meson).
- **Snapcraft (`build-aux/snapcraft/snapcraft.yaml`)**:
  - Uses `core22` base snap.
  - Installs requirements using Poetry inside an `override-build` script, followed by the Meson build stage.

### Issues, Inconsistencies & Risks
* **Issue 6.1: Desktop File and Flatpak App ID Mismatch**
  * **Severity**: `should-fix`
  * **Details**: The Flatpak manifest expects the application ID `org.astralco.GGate`. It compiles the repo but the desktop launcher in `data/` is named `org.astralco.ggate.desktop` (lowercase). This name conflict will prevent Flatpak exports from displaying the desktop file on the host machine.
  * **Recommended Fix**: Rename `data/org.astralco.ggate.desktop` to `org.astralco.GGate.desktop`.
* **Issue 6.2: Unsandboxed Pip Network Usage in Flatpak**
  * **Severity**: `should-fix`
  * **Details**: The flatpak manifest uses `--share=network` and `pip install` to install python dependencies. Flathub builds must run fully offline for security and reproducibility.
  * **Recommended Fix**: Use `flatpak-pip-generator` to create a static list of verified source mirrors with SHA hashes for python dependencies.
* **Issue 6.3: Unsafe/Brittle Poetry Installer in Snapcraft**
  * **Severity**: `should-fix`
  * **Details**: The snapcraft recipe retrieves Poetry via `curl` from a remote location and pipes it to python (`curl -sSL https://install.python-poetry.org | python3 -`). This is insecure and fragile, and it can easily fail if internet access is interrupted or remote domains modify the payload.
  * **Recommended Fix**: Install python dependencies via the native Snapcraft python plugins or pip packages.
* **Issue 6.4: Non-Relocatable Prefix in Snapcraft**
  * **Severity**: `should-fix`
  * **Details**: Snapcraft passes `--prefix=/snap/ggate/current/usr` as a Meson parameter. Snaps should be built with relative/relocatable paths, as hardcoding the current snap mount point path can cause layout issues if a system runs alternative channels.
  * **Recommended Fix**: Let Snapcraft handle the target prefix path automatically without passing a static meson-parameter.

---

## 7. `DATADIR` and Runtime Asset-Path Handling

### Description of Existing Setup
- **`ggate/config.py`**: Resolves `DATADIR` relative to the current module file `ggate/config.py` (which points inside the `ggate/` directory).
- **`ggate/ComponentView.py`**: Attempts to locate gate assets by joining `config.DATADIR` with `"images", "components"`.
- **`ggate/MainFrame.py`**: Adds `config.DATADIR + "/images"` to the GTK Icon Theme search paths.
- **`ggate/MenuPopover.py`**: Resolves `_PROJECT_ROOT` based on module layout and builds hardcoded paths targeting `data/images/actions/*.svg`.

### Issues, Inconsistencies & Risks
* **Issue 7.1: Broken Development and Installed Icon Paths**
  * **Severity**: `blocker`
  * **Details**: 
    1. **Development**: `config.DATADIR` resolves to the `ggate/` folder. Since the folder `ggate/images/` does not exist in the source repository (all source images are in `data/images`), search paths resolved by `ComponentView` and `MainFrame` point to non-existent locations, failing to load icons.
    2. **Installed**: `config.DATADIR` resolves to python's site-packages path (e.g. `/usr/lib/python3/dist-packages/ggate/`). The actual assets are installed to the system prefix (e.g., `/usr/share/ggate/icons/components`), meaning the application will look in `/usr/lib/.../ggate/images/` and fail to load icons.
    3. **MenuPopover**: The context menu icon path `_PROJECT_ROOT/data/images/actions/` works in dev because `_PROJECT_ROOT` resolves to the workspace directory. When installed, `_PROJECT_ROOT` becomes `/usr/lib/python3/dist-packages/`, causing context menu icon resolution to fail.
  * **Recommended Fix**: This is the single biggest risk to GGate's deployment:
    - Eliminate the direct file path lookup workarounds (`_get_icon_path` and `config.DATADIR` hacks).
    - Align GResource folder layouts with standard Freedesktop icon theme conventions (see Issue 3.1).
    - Initialize resources at startup and load all assets strictly by name (`Gtk.Image.new_from_icon_name`) or via resource URLs (`resource:///...`), allowing GTK to handle resolution.

---

## Prioritized Punch-List

This punch-list is ordered by severity and structural impact to ensure the application builds, packages, and runs correctly both in local development and installed environments.

1. **[BLOCKER] Fix missing imports in `bin/ggate.in`** (Issue 2.1). Add `import os` and `from gi.repository import Gio`.
2. **[BLOCKER] Resolve runtime asset path failures** (Issue 7.1). Eliminate direct filesystem path lookups in `ComponentView.py` and `MenuPopover.py`.
3. **[SHOULD-FIX] Align GResource structures with Freedesktop icon theme standards** (Issue 3.1). Re-file resources under `@PREFIX@/icons/hicolor/scalable/` and use resource aliases.
4. **[SHOULD-FIX] Standardize Application ID casing** (Issue 4.2). Rename hardcoded instances of `org.astralco.ggate` to `org.astralco.GGate` (or `org.astralco.GGate.Dev`).
5. **[SHOULD-FIX] Generate `config.py` via Meson** (Issue 4.1). Replace static version and path values in `config.py` with variables configured via `configure_file`.
6. **[SHOULD-FIX] Rename Desktop File for Flatpak compliance** (Issue 6.1). Match the desktop file name to the App ID: `org.astralco.GGate.desktop`.
7. **[SHOULD-FIX] Prepare Flatpak for offline compilation** (Issue 6.2). Use `flatpak-pip-generator` to decouple dependencies from network-dependent pip execution.
8. **[SHOULD-FIX] Fix Snapcraft setup** (Issues 6.3 & 6.4). Remove remote `curl | python3` scripts and omit the hardcoded installation prefix.
9. **[SHOULD-FIX] Eliminate Unix-dependent shell call in `meson.build`** (Issue 1.1). Compute `exclude_directories` portably.
10. **[NICE-TO-HAVE] Relax dependency pins in `pyproject.toml`** (Issue 5.1). Use range restrictions instead of a rigid version pin for `shapely`.
11. **[NICE-TO-HAVE] Clean up pyproject/meson clutter** (Issues 1.2, 1.3, 2.2, 5.2). Standardize cli formatting, clean up comments, remove redundant dependency entries, and rename shadow variables.
