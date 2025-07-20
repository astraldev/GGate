# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from typing import Optional
from ggate.Components.LogicGates.SystemComponents import BaseComponent, PropertyError
from ggate.const import Definitions, definitions as const
from gi.repository import Gtk, GObject, Adw
from gettext import gettext as _

class PropertyWindow(Adw.Dialog):
    __gsignals__ = {
        "property-changed": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "window-hidden": (GObject.SIGNAL_RUN_LAST, None, ()),
    }

    def on_window_delete(self, *args):
        self.emit("window-hidden")

    def __init__(self):
        self.title = _("Properties")

        Adw.Dialog.__init__(self, title=self.title)
        self.set_size_request(310, -1)

        self.prop_controls = []
        self.old_values = []
        self.content_box: Gtk.Box = None
        self.banner: Adw.Banner = None

        self.set_content_width(350)
        self.connect("close-request", self.on_window_delete)
    
    def _set_invalid_state(self, positions):
        for idx, ctrl in enumerate(self.prop_controls):
            if idx in positions:
                ctrl.add_css_class("error")
            else:
                ctrl.remove_css_class("error")

    def on_apply_btn_clicked(self, *widget):
        values = []
        property_index = 0

        if self.component is None:
            return

        for property in self.component.properties:
            if isinstance(property[1], tuple):
                if property[1][0] == const.property_select:
                    values.append(self.prop_controls[property_index].get_selected())

                elif property[1][0] == const.property_int:
                    values.append(int(self.prop_controls[property_index].get_value()))

                elif property[1][0] == const.property_float:
                    values.append(self.prop_controls[property_index].get_value())

                else:
                    values.append(self.prop_controls[property_index].get_text())

            elif property[1] == const.property_bool:
                values.append(self.prop_controls[property_index].get_active())

            else:
                property_index -= 1

            property_index += 1

        valid_property_spec = self.component.propertyChanged(values)

        if valid_property_spec is not False and isinstance(valid_property_spec, PropertyError) and self.banner is not None:
            message = valid_property_spec.message
            property_pos = valid_property_spec.positions
            self.banner.set_title(message)
            self.banner.set_revealed(True)
            self._set_invalid_state(property_pos)
        else:
            self.component.values = values
            self.component.set_rot_props()
            self.banner.set_revealed(False)
            self._set_invalid_state([])

        self.emit("property-changed")

    def show_properties(self, component: Optional[BaseComponent]):
        if component is None:
            return

        self.component = component
        if self.vbox is not None:
            self.set_child(None)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_show_start_title_buttons(False)
        self.header_bar.set_decoration_layout("close")

        self.set_title("%s - %s" % (self.title, component.description))

        if len(component.properties) == 0:
            status_page = Adw.StatusPage(
                title="No properties",
                description="This component has no editable properties.",
            )

            self.set_child(status_page)
            return

        property_idx = 0
        group_location = 0

        # Create property editor
        self.prop_controls = []

        # Property Groups
        groups = []

        for property in component.properties:
            has_property = True

            if property[1] == Definitions.property_bool:
                ctrl = Adw.SwitchRow(title=property[0])
                ctrl.set_active(component.values[property_idx])
                ctrl.connect("notify::active", self.on_apply_btn_clicked)

            elif isinstance(property[1], tuple):
                if property[1][0] == const.property_select:
                    ctrl = Adw.ComboRow(title=property[0])
                    model = Gtk.StringList.new(property[1][1:])

                    ctrl.set_model(model)
                    ctrl.set_selected(self.component.values[property_idx])
                    ctrl.set_enable_search(True)
                    ctrl.connect("changed", self.on_apply_btn_clicked)

                elif property[1][0] == const.property_int:
                    ctrl = Adw.SpinRow.new_with_range(
                        property[1][1],
                        property[1][2],
                        1.0
                    )

                    ctrl.set_digits(0)
                    ctrl.set_numeric(True)
                    ctrl.set_title(property[0])
                    ctrl.set_value(component.values[property_idx])
                    ctrl.connect("changed", self.on_apply_btn_clicked)

                elif property[1][0] == const.property_float:
                    floating_points = property[1][3] if property[1][3] < 3 else 2
                    ctrl = Adw.SpinRow.new_with_range(
                        property[1][1],
                        property[1][2],
                        floating_points
                    )

                    ctrl.set_numeric(True)
                    ctrl.set_title(property[0])
                    ctrl.set_value(component.values[property_idx])
                    ctrl.connect("changed", self.on_apply_btn_clicked)

                else:
                    ctrl = Adw.EntryRow(
                        title=property[0],
                        text=component.values[property_idx]
                    )

                    ctrl.set_width_chars(property[1][1])
                    ctrl.connect("changed", self.on_apply_btn_clicked)

            else:
                property_idx -= 1
                group_location += 1
                has_property = False

            # Create initial group if it doesn't exist
            if group_location >= len(groups) and has_property:
                group = Adw.PreferencesGroup.new()
                group.set_title(property[2])
                group.set_description(property[0])
                groups.append(group)

            # Set current group to the previous one
            elif has_property:
                self.prop_controls.append(ctrl)

                group = groups[group_location]
                group.add(ctrl)

            # Create a new group
            elif not has_property:
                group = Adw.PreferencesGroup.new()
                group.set_title(property[2])
                group.set_description(property[0])
                groups.append(group)

            # Update the property index
            property_idx += 1

        self.banner = Adw.Banner()
        self.banner.set_revealed(False)

        preference_page = Adw.PreferencesPage.new()

        # Add all groups to the preference page
        for group in groups:
            if group.get_children():
                preference_page.add(group)

        self.vbox.append(self.header_bar)
        self.vbox.append(self.banner)
        self.vbox.append(preference_page)
        self.set_child(self.vbox)

        self.present()