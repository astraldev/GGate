# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import math
from glogic import config, const
from glogic.Components import comp_dict
from gettext import gettext as _
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject


class ComponentView(Gtk.ScrolledWindow):

    __gsignals__ = {
        'component-checked': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'window-hidden': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):

        super().__init__()
        
        self.listBox = Gtk.ListBox()
        self.set_margin_bottom(4)

        # Create toggle buttons

        self.button_names = {
            'standard':  [const.component_NOT,     const.component_AND,     const.component_OR],
            'alternate': [const.component_XOR,     const.component_NAND,    const.component_NOR],

            'components': [const.component_SW,      const.component_7seg,    const.component_LED,
                           const.component_VDD,     const.component_GND,     const.component_OSC,
                           const.component_probe,   const.component_text],

            'examples':  [const.component_RSFF,    const.component_JKFF,
                          const.component_DFF,     const.component_TFF,
                          const.component_counter, const.component_adder,    const.component_SISO,
                          const.component_SIPO,    const.component_PISO,    const.component_PIPO]
        }

        self.set_size_request(200, -1)

        self.components = []

        for button_types in self.button_names.keys():
            section = Gtk.ListBoxRow()
            section_title = Gtk.Box()

            section_label = Gtk.Label()
            section_label.set_markup(f'<b>{str(button_types).capitalize()}</b>')
            section_label.set_margin_top(5)
            section_label.set_margin_bottom(5)
            section_label.set_name('subtitle')

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
                
                icon = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(config.DATADIR+"/images/components/"+gate+".png"))
                label = Gtk.Label(label=str(gate).capitalize())

                icon.set_margin_end(5)
                icon.set_margin_start(10)
                icon.set_size_request(24, 24)
                label.set_margin_start(5)

                content_box.append(icon)
                content_box.append(label)
                gate_row.set_child(content_box)
                gate_row.set_activatable(True)
                gate_row.type = gate
                self.listBox.append(gate_row)
                self.components.append(gate_row)
            
        self.listBox.connect('row-activated', self.on_row_activated)
        self.set_child(self.listBox)

    def set_all_sensitive(self, state, *args):
        for row in self.components:
            row.set_selectable(not (not state))
    
    def on_row_activated(self, _, row, *args):
        gate = row.type

        gates = []

        for item in self.button_names.values():
            gates+=item
        
        if gate in gates:
            self.emit("component-checked", gate)
    
