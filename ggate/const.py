# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import os
import gettext
from gettext import gettext as _

gettext.textdomain("ggate")

class DefinitionError(TypeError):
    pass

class Definitions(object):
    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise (DefinitionError, "Can't rebind const(%s)" % name)
        self.__dict__[name] = value

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

    component_tribuff = "tribuff"

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

    glcfile_text = _("GGate files (*.glc)")
    pngfile_text = _("Portable Network Graphics (*.png)")
    svgfile_text = _("Scalable Vector Graphics (*.svg)")
    pdffile_text = _("Portable Document Format (*.pdf)")
    psfile_text = _("Post Script (*.ps)")
    anyfile_text = _("All files")

    config_path = os.path.join(os.path.expanduser("~"), ".config/ggate")

    app_name = _("GGate")
    description = _(
        "GGate is a logic circuit simulator developed with GTK+ and Python.")
    copyright = "Copyright © 2012 - 2022 Koichi Akabe"
    developer = ["Koichi Akabe <vbkaisetsu@gmail.com>",
                 'Ekure Edem <ekureedem480@gmail.com>']
    website = "https://launchpad.net/ggate"
    help = "help:ggate"
    license = """GGate is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

GGate is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>."""

    devel_bug = "https://github.com/astraldev/GGate/issues/new"

definitions = Definitions