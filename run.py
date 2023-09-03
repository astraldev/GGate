#!/usr/bin/python3
# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-
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

import gi, sys

gi.require_version("Gtk", '4.0')
gi.require_version('PangoCairo', '1.0')

from ggate.MainFrame import GLogicApplication
from ggate import __version__

if __name__ == "__main__":
	app = GLogicApplication()
	if len(sys.argv) > 1 and sys.argv[1] == "--version":
		print(f"GGate {__version__}")
		sys.exit(0)

	app.run()
