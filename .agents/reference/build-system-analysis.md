# GGate Remaining Build & Packaging Issues

This document tracks the outstanding build, packaging, and resource issues in GGate. All previously identified issues (such as local variable shadowing, missing imports in the launcher, CLI version mismatch, static version unification, app ID casing, and desktop file naming) have been resolved.

---

## 1. Resource and Icon Path Handling (P2)
* **Status**: **Still Pending**
* **Linked Plan**: [.agents/plans/icon-creation.md](file:///.agents/plans/icon-creation.md)
* **Description**: Component icons are still loaded using direct filesystem path lookups (e.g. `_get_icon_path` in `ComponentView.py` and absolute file path constructs in `MenuPopover.py`).
* **Issues**:
  1. This breaks when the application is installed globally (since the source `data/images` path is not present at the python site-packages folder level).
  2. The GResource path layout is non-standard (redundant `data/` subdirectory, missing icon theme folder hierarchy like `hicolor`, and double actions paths).
* **Recommended Resolution**: 
  - Restructure the icons folder hierarchy inside both the dev and release GResource bundles to follow the Freedesktop icon theme standards: `/org/astralco/ggate/icons/hicolor/[size]/[context]/[name].[ext]`.
  - Use `GResource` aliases to map resource paths cleanly.
  - Load all icons strictly by name using `Gtk.Image.new_from_icon_name` or `resource://` URLs.

---

## 2. Flatpak Build Improvements
* **Status**: **Still Pending**
* **Description**: The Flatpak manifest (`build-aux/flatpak/org.astralco.ggate.json`) compiles python modules using pip with active network access (`--share=network`).
* **Issues**: For official distribution on Flathub, builds must be fully offline and reproducible.
* **Recommended Resolution**: Use `flatpak-pip-generator` to generate a static list of dependencies with SHA-256 hashes, allowing local offline pip installation.

---

## 3. Snapcraft Build Improvements
* **Status**: **Still Pending**
* **Description**: 
  1. The snapcraft recipe (`build-aux/snapcraft/snapcraft.yaml`) uses a remote installer script via `curl` and pipes it to python (`curl -sSL https://install.python-poetry.org | python3 -`) to fetch Poetry.
  2. The recipe passes a hardcoded prefix: `--prefix=/snap/ggate/current/usr`.
* **Issues**: Downloading third-party installer scripts at build time is insecure and prone to network failure. Hardcoded snap prefix paths make snap execution non-relocatable across alternative snap channels.
* **Recommended Resolution**: Use native Snapcraft python plugins or local offline packaging of pip dependencies, and let Snapcraft handle the meson installation prefix automatically.
