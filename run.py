#!/usr/bin/python3
#
#  Copyright (C) Koichi Akabe 2012 <vbkaisetsu@gmail.com>
#
#  GGate is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  GGate is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import gi
import sys
import os
import subprocess

gi.require_version("Gtk", "4.0")
gi.require_version("PangoCairo", "1.0")
gi.require_version("Adw", "1")

from gi.repository import Gio
from ggate.MainFrame import GLogicApplication
from ggate import __version__


def build_dev_resources():
  import glob
  base = os.path.dirname(os.path.abspath(__file__))
  images_dir = os.path.join(base, "data", "images")
  xml = os.path.join(images_dir, "dev-resources.xml")
  target = os.path.join(base, "dev-resources.gresource")

  comp_files = sorted(glob.glob(os.path.join(images_dir, "components", "*.svg")))
  act_files = sorted(glob.glob(os.path.join(images_dir, "actions", "*.svg")))
  theme_files = sorted(glob.glob(os.path.join(base, "data", "themes", "*.json")))

  icon_lines = []
  for f in comp_files:
    rel = os.path.relpath(f, images_dir).replace("\\", "/")
    icon_lines.append(f"    <file preprocess=\"xml-stripblanks\">{rel}</file>")
  for f in act_files:
    rel = os.path.relpath(f, images_dir).replace("\\", "/")
    icon_lines.append(f"    <file preprocess=\"xml-stripblanks\">{rel}</file>")

  theme_lines = []
  for f in theme_files:
    rel = os.path.relpath(f, images_dir).replace("\\", "/")
    basename = os.path.basename(f)
    theme_lines.append(f"    <file alias=\"{basename}\">{rel}</file>")

  xml_content = (
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    "<gresources>\n"
    "  <gresource prefix=\"/org/astralco/ggate/Dev/data/icons/scalable/actions/\">\n"
    + "\n".join(icon_lines)
    + "\n  </gresource>\n"
    "  <gresource prefix=\"/org/astralco/ggate/Dev/themes/\">\n"
    + "\n".join(theme_lines)
    + "\n  </gresource>\n"
    "</gresources>\n"
  )

  try:
    with open(xml, "w", encoding="utf-8") as f:
      f.write(xml_content)
  except OSError:
    pass

  try:
    subprocess.run(
      ["glib-compile-resources", "--sourcedir", images_dir, "--target", target, xml],
      check=True,
    )
  except (OSError, subprocess.CalledProcessError):
    pass

if __name__ == "__main__":
  build_dev_resources()
  resource = Gio.Resource.load("./dev-resources.gresource")
  resource._register()

  app = GLogicApplication()
  if len(sys.argv) > 1 and sys.argv[1] == "--version":
    print(f"GGate {__version__}")
    sys.exit(0)

  app.run()
