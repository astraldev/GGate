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
        self._is_presented = False
        self.emit("window-hidden")

    def dismiss(self):
        if self._is_presented:
            self.close()

    def __init__(self):
        self.title = _("Properties")

        Adw.Dialog.__init__(self, title=self.title)
        self.set_size_request(310, -1)

        self.prop_controls = []
        self.old_values = []
        self.content_box: Gtk.Box = None
        self.banner: Adw.Banner = None
        self.component = None
        self._is_presented = False

        self.set_content_width(350)
        self.connect("closed", self.on_window_delete)
    
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

    def show_properties(self, component: Optional[BaseComponent], parent: Optional[Gtk.Widget] = None):
        if component is None:
            self.dismiss()
            return

        self.component = component
        self.set_child(None)

        self.header_bar = Adw.HeaderBar()

        self.set_title("%s - %s" % (self.title, component.description))

        self.banner = Adw.Banner()
        self.banner.set_revealed(False)

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(self.header_bar)
        toolbar_view.add_top_bar(self.banner)

        if len(component.properties) == 0:
            status_page = Adw.StatusPage(
                title=_("No properties"),
                description=_("This component has no editable properties."),
            )

            toolbar_view.set_content(status_page)
            self.set_child(toolbar_view)
            if parent is not None:
                self.present(parent)
                self._is_presented = True
            return

        property_idx = 0
        self.prop_controls = []
        groups = []
        group_counts = {}
        current_group = None

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
                    ctrl.connect("notify::selected", self.on_apply_btn_clicked)

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
                    ctrl.connect("notify::value", self.on_apply_btn_clicked)

                elif property[1][0] == const.property_float:
                    floating_points = property[1][3] if property[1][3] < 3 else 2
                    step = 10.0 ** -floating_points if floating_points > 0 else 1.0
                    ctrl = Adw.SpinRow.new_with_range(
                        property[1][1],
                        property[1][2],
                        step
                    )

                    ctrl.set_digits(floating_points)
                    ctrl.set_numeric(True)
                    ctrl.set_title(property[0])
                    ctrl.set_value(component.values[property_idx])
                    ctrl.connect("notify::value", self.on_apply_btn_clicked)

                else:
                    ctrl = Adw.EntryRow(
                        title=property[0],
                        text=component.values[property_idx]
                    )

                    ctrl.set_width_chars(property[1][1])
                    ctrl.connect("changed", self.on_apply_btn_clicked)

            else:
                property_idx -= 1
                has_property = False

            if has_property:
                if current_group is None:
                    current_group = Adw.PreferencesGroup.new()
                    groups.append(current_group)
                    group_counts[current_group] = 0

                # self.prop_controls stays 1:1 and in-order with non-separator properties
                self.prop_controls.append(ctrl)
                current_group.add(ctrl)
                group_counts[current_group] += 1
            else:
                current_group = Adw.PreferencesGroup.new()
                current_group.set_title(property[0])
                groups.append(current_group)
                group_counts[current_group] = 0

            property_idx += 1

        preference_page = Adw.PreferencesPage.new()

        for group in groups:
            if group_counts.get(group, 0) > 0:
                preference_page.add(group)

        toolbar_view.set_content(preference_page)
        self.set_child(toolbar_view)

        if parent is not None:
            self.present(parent)
            self._is_presented = True