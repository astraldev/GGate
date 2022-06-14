# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import sys, os, gettext
from gettext import gettext as _

gettext.textdomain("glogic")

class _const:
	class ConstError(TypeError): pass
	def __setattr__(self, name, value):
		if name in self.__dict__:
			raise (self.ConstError, "Can't rebind const(%s)" % name)
		self.__dict__[name] = value

	menu_xml = """
	<?xml version="1.0" encoding="UTF-8"?>
    <interface>
        <menu id="app-menu">
            <section> 
                <item>
                    <attribute name="label">New</attribute>
                    <attribute name="action">app.on_action_new_pressed</attribute>
               </item>
                <item>
                    <attribute name="label">Open</attribute>
                    <attribute name="action">app.on_action_open_pressed</attribute>
               </item>
                <item>
                    <attribute name="label">Save</attribute>
                    <attribute name="action">app.on_action_save_pressed</attribute>
               </item>
                <item>
                    <attribute name="label">Save as</attribute>
                    <attribute name="action">app.on_action_saveas_pressed</attribute>
               </item>
                <item>
                    <attribute name="label">Save Image</attribute>
                    <attribute name="action">app.on_action_save_image</attribute>
               </item>
            </section>
            <section>
                <item>
                    <attribute name="label">About</attribute>
                    <attribute name="action">app.on_action_about_pressed</attribute>
               </item>
               <item>
                    <attribute name="label">Quit</attribute>
                    <attribute name="action">app.on_action_quit_pressed</attribute>
               </item>
            </section>
        </menu>
    </interface>"""

	# Definitions
	component_none = "none"
	component_net = "net"
	component_NOT = "not"
	component_AND = "and"
	component_OR = "or"
	component_XOR = "xor"
	component_NAND = "nand"
	component_NOR = "nor"
	component_RSFF = "rsff"
	component_JKFF = "jkff"
	component_DFF = "dff"
	component_TFF = "tff"
	component_counter = "counter"
	component_SISO = "siso"
	component_SIPO = "sipo"
	component_PISO = "piso"
	component_PIPO = "pipo"
	component_adder = "adder"
	component_SW = "sw"
	component_7seg = "7seg"
	component_LED = "led"
	component_VDD = "vdd"
	component_GND = "gnd"
	component_OSC = "osc"
	component_probe = "probe"
	component_text = "text"

	direction_none = (0, 0)
	direction_E = (1, 0)
	direction_N = (0, -1)
	direction_W = (-1, 0)
	direction_S = (0, 1)

	property_bool = 0
	property_int = 1
	property_float = 2
	property_select = 3
	property_string = 4

	text_notitle = _("No title")
	text_modified = _("Modified")

	glcfile_text = _("gLogic files (*.glc)")
	pngfile_text = _("Portable Network Graphics (*.png)")
	svgfile_text = _("Scalable Vector Graphics (*.svg)")
	pdffile_text = _("Portable Document Format (*.pdf)")
	psfile_text = _("Post Script (*.ps)")
	anyfile_text = _("All files")

	config_path = os.path.join(os.path.expanduser("~"), ".config/glogic")

	app_name = _("gLogic")
	description = _("gLogic is a logic circuit simulator developed with GTK+ and Python.")
	copyright = "Copyright © 2012 Koichi Akabe"
	developer = ["Koichi Akabe <vbkaisetsu@gmail.com>"]
	website = "https://launchpad.net/glogic"
	help = "help:glogic"
	license = """gLogic is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

gLogic is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>."""

	devel_translate = "https://translations.launchpad.net/glogic/"
	devel_bug = "https://bugs.launchpad.net/glogic"

sys.modules[__name__] = _const()
