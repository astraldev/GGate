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
  base = os.path.dirname(os.path.abspath(__file__))
  images_dir = os.path.join(base, "data", "images")
  xml = os.path.join(images_dir, "dev-resources.xml")
  target = os.path.join(base, "dev-resources.gresource")

  try:
    subprocess.run(
      [
        sys.executable,
        os.path.join(base, "build-aux", "generate-resources-xml.py"),
        "--prefix", "/org/astralco/ggate/Dev",
        "--output", xml,
        "--source-dir", images_dir,
      ],
      check=True,
    )
  except (OSError, subprocess.CalledProcessError):
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
