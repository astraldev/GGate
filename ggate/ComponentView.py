import os
from ggate import config
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.const import definitions
from gettext import gettext as _
from gi.repository import Gtk, GdkPixbuf, GObject

def _get_icon_path(icon: str):
    svg_path = os.path.join(config.DATADIR, "images", "components", f"{icon}.svg")
    png_path = os.path.join(config.DATADIR, "images", "components", f"{icon}.png")
    return svg_path if os.path.exists(svg_path) else png_path

class ComponentViewListBoxRow(Gtk.ListBoxRow):
    type = BaseComponent

class ComponentView(Gtk.Box):
    __gsignals__ = {
        "component-checked": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "window-hidden": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_margin_start(6)
        self.set_margin_end(6)
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_size_request(200, -1)

        self.components: list[ComponentViewListBoxRow] = []
        self.listboxes: list[Gtk.ListBox] = []
        self.category_groups = []

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("Search gates"))
        self.search_entry.set_margin_start(4)
        self.search_entry.set_margin_end(4)
        self.search_entry.set_margin_top(4)
        self.search_entry.set_margin_bottom(4)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.append(self.search_entry)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        self.append(scrolled)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.main_box.set_margin_start(4)
        self.main_box.set_margin_end(4)
        scrolled.set_child(self.main_box)

        # Create toggle buttons
        self.button_names = {
            "Logic Gates": [
                definitions.component_NOT,
                definitions.component_AND,
                definitions.component_OR,
            ],
            "Advanced Gates": [
                definitions.component_XOR,
                definitions.component_NAND,
                definitions.component_NOR,
                definitions.component_tribuff,
            ],
            "Basic Components": [
                definitions.component_SW,
                definitions.component_7seg,
                definitions.component_LED,
                definitions.component_VDD,
                definitions.component_GND,
                definitions.component_OSC,
                definitions.component_probe,
                definitions.component_text,
            ],
            "Misc components": [
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

        for button_types in self.button_names.keys():
            group_label = Gtk.Label()
            group_label.set_markup("<b>" + _(button_types).capitalize() + "</b>")
            group_label.add_css_class("dimmed")
            group_label.set_halign(Gtk.Align.START)
            group_label.set_margin_start(4)
            group_label.set_margin_top(4)
            group_label.set_margin_bottom(2)
            self.main_box.append(group_label)

            # ListBox for this category
            lb = Gtk.ListBox()
            lb.add_css_class("navigation-sidebar")
            lb.connect("row-activated", self.on_row_activated)
            self.main_box.append(lb)
            self.listboxes.append(lb)

            group_rows = []
            for gate in self.button_names[button_types]:
                gate_row: ComponentViewListBoxRow = ComponentViewListBoxRow()
                content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                content_box.set_valign(Gtk.Align.CENTER)

                icon = Gtk.Image.new_from_file(_get_icon_path(gate))
                icon.set_margin_end(4)
                icon.set_margin_start(4)
                icon.set_size_request(24, 24)

                label = Gtk.Label(label=str(gate).upper())
                label.add_css_class("subtitle")

                content_box.append(icon)
                content_box.append(label)

                # Setup row
                gate_row.type = gate
                gate_row.set_child(content_box)
                gate_row.set_activatable(True)

                lb.append(gate_row)
                self.components.append(gate_row)
                group_rows.append(gate_row)

            self.category_groups.append((group_label, lb, group_rows))

    def set_all_sensitive(self, state, *args):
        [row.set_selectable(bool(state)) for row in self.components]

    def on_row_activated(self, listbox, row, *args):
        for lb in self.listboxes:
            if lb != listbox:
                lb.unselect_all()

        gate = row.type
        gates = []
        for item in self.button_names.values():
            gates += item

        if gate in gates:
            self.emit("component-checked", gate)

    def on_search_changed(self, entry):
        query = entry.get_text().strip().lower()

        for group_label, lb, gates in self.category_groups:
            visible_count = 0
            for row in gates:
                match = not query or (query in str(row.type).lower())
                row.set_visible(match)
                if match:
                    visible_count += 1

            lb.set_visible(visible_count > 0)
            group_label.set_visible(visible_count > 0)
