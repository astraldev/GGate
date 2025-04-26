# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from ggate import config
from ggate.const import definitions
from gettext import gettext as _
from gi.repository import Gtk, GdkPixbuf, GObject

class ComponentView(Gtk.ScrolledWindow):

    __gsignals__ = {
        "component-checked": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "window-hidden": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):

        super().__init__()

        self.listBox = Gtk.ListBox()
        self.set_margin_bottom(4)

        # Create toggle buttons

        self.button_names = {
            "Basic Components": [
                definitions.component_NOT,
                definitions.component_AND,
                definitions.component_OR,
            ],
            "alternate": [
                definitions.component_XOR,
                definitions.component_NAND,
                definitions.component_NOR,
                definitions.component_tribuff,
            ],
            "components": [
                definitions.component_SW,
                definitions.component_7seg,
                definitions.component_LED,
                definitions.component_VDD,
                definitions.component_GND,
                definitions.component_OSC,
                definitions.component_probe,
                definitions.component_text,
            ],
            "examples": [
                definitions.component_RSFF,
                definitions.component_JKFF,
                definitions.component_DFF,
                definitions.component_TFF,
                definitions.component_counter,
                definitions.component_adder,
                definitions.component_SISO,
                definitions.component_SIPO,
                definitions.component_PISO,
                definitions.component_PIPO,
            ],
        }

        self.set_size_request(200, -1)

        self.components = []

        for button_types in self.button_names.keys():
            section = Gtk.ListBoxRow()
            section_title = Gtk.Box()

            section_label = Gtk.Label()
            section_label.set_markup("<b>" + _(button_types).capitalize() + "</b>")
            section_label.set_margin_top(5)
            section_label.set_margin_bottom(5)
            section_label.add_css_class("title")

            section_title.append(section_label)
            section_title.set_margin_start(5)

            section.set_size_request(-1, 35)
            section.set_child(section_title)
            section.set_activatable(False)
            section.set_selectable(False)

            self.listBox.append(section)
            self.listBox.set_show_separators(True)

            # The logic gates in that section

            for gate in self.button_names[button_types]:
                gate_row = Gtk.ListBoxRow()
                content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

                icon = Gtk.Image.new_from_pixbuf(
                    GdkPixbuf.Pixbuf.new_from_file(
                        config.DATADIR + "/images/components/" + gate + ".png"
                    )
                )
                label = Gtk.Label(label=str(gate).capitalize())

                icon.set_margin_end(5)
                icon.set_margin_start(10)
                icon.set_size_request(24, 24)
                label.set_margin_start(5)

                content_box.append(icon)
                content_box.append(label)

                label.add_css_class("subtitle")
                gate_row.set_child(content_box)
                gate_row.set_activatable(True)
                gate_row.type = gate
                self.listBox.append(gate_row)
                self.components.append(gate_row)

        self.listBox.connect("row-activated", self.on_row_activated)
        self.set_child(self.listBox)

    def set_all_sensitive(self, state, *args):
        for row in self.components:
            row.set_selectable(not (not state))

    def on_row_activated(self, _, row, *args):
        gate = row.type

        gates = []

        for item in self.button_names.values():
            gates += item

        if gate in gates:
            self.emit("component-checked", gate)
