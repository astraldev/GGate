from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ggate.MainFrame import MainFrame

from gi.repository import Gtk, Adw
from gettext import gettext as _
from ggate.Components.Windows.TimingGraph.Diagram import TimingGraphDiagram
from ggate import Preference

class TimingGraphDisplayWindow(Adw.Dialog):
    def __init__(self, parent: MainFrame):
        Adw.Dialog.__init__(self, can_close=True)
        self._parent = parent
        self._is_presented = False
        
        self.set_title(_("Timing Graph"))
        self.set_content_width(650)
        self.set_content_height(450)
        
        toolbar_view = Adw.ToolbarView()
        
        header_bar = Adw.HeaderBar()
        toolbar_view.add_top_bar(header_bar)
        
        sub_toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        sub_toolbar.set_margin_start(12)
        sub_toolbar.set_margin_end(12)
        sub_toolbar.set_margin_top(6)
        sub_toolbar.set_margin_bottom(6)
        
        scale_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        scale_box.append(Gtk.Label(label=_("Scale:")))
        
        self.scale_spin = Gtk.SpinButton.new_with_range(0.1, 1000.0, 0.5)
        self.scale_spin.set_value(5.0)
        self.scale_spin.set_digits(1)
        self.scale_spin.connect("value-changed", self.on_parameters_changed)
        scale_box.append(self.scale_spin)
        
        self.scale_unit = Gtk.DropDown.new_from_strings(["ns", "µs", "ms"])
        self.scale_unit.set_selected(1)
        self.scale_unit.connect("notify::selected", self.on_parameters_changed)
        scale_box.append(self.scale_unit)
        
        sub_toolbar.append(scale_box)
        
        spacer = Gtk.Box(hexpand=True)
        sub_toolbar.append(spacer)
        
        range_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        range_box.append(Gtk.Label(label=_("Range From:")))
        
        self.from_spin = Gtk.SpinButton.new_with_range(0.0, 100000.0, 1.0)
        self.from_spin.set_value(0.0)
        self.from_spin.set_digits(2)
        self.from_spin.connect("value-changed", self.on_parameters_changed)
        range_box.append(self.from_spin)
        
        range_box.append(Gtk.Label(label=_("To:")))
        
        self.to_spin = Gtk.SpinButton.new_with_range(0.0, 100000.0, 10.0)
        max_dur = getattr(Preference, "max_calc_duration", 0.0002)
        self.to_spin.set_value(max_dur * 1e6)
        self.to_spin.set_digits(2)
        self.to_spin.connect("value-changed", self.on_parameters_changed)
        range_box.append(self.to_spin)
        
        self.range_unit = Gtk.DropDown.new_from_strings(["ns", "µs", "ms"])
        self.range_unit.set_selected(1)
        self.range_unit.connect("notify::selected", self.on_parameters_changed)
        range_box.append(self.range_unit)
        
        sub_toolbar.append(range_box)
        
        save_button = Gtk.Button(label=_("Save Image"))
        save_button.connect("clicked", self.on_save_clicked)
        sub_toolbar.append(save_button)
        
        toolbar_view.add_top_bar(sub_toolbar)
        
        self._draw_area = TimingGraphDiagram(parent)
        toolbar_view.set_content(self._draw_area)
        
        self.set_child(toolbar_view)
        self.connect("closed", self.on_closed)

    def on_parameters_changed(self, *args):
        if getattr(self, "_blocking_updates", False):
            return
        # spin value is in display-unit (ns/μs/ms); divide by seconds-per-unit to get px/s
        multipliers = {0: 1e-9, 1: 1e-6, 2: 1e-3}
        scale_val = self.scale_spin.get_value()
        scale_mult = multipliers.get(self.scale_unit.get_selected(), 1e-6)
        
        self._draw_area.scale = scale_val / scale_mult
        
        range_mult = multipliers.get(self.range_unit.get_selected(), 1e-6)
        self._draw_area.start_time = self.from_spin.get_value() * range_mult
        self._draw_area.end_time = self.to_spin.get_value() * range_mult
        self._draw_area.timing_unit = self.range_unit.get_selected()
        
        self._draw_area.draw()

    def on_save_clicked(self, button):
        from ggate.Exporter import save_timing_diagram_as_image
        save_timing_diagram_as_image(self._draw_area, self._parent)

    def on_closed(self, dialog):
        self._is_presented = False

    def display(self):
        self._is_presented = True
        
        history = self._parent.circuit.probe_levels_history
        if not history or len(history) <= 1:
            self.on_parameters_changed()
            self.present(self._parent)
            return

        start_t = history[0][0]
        end_t = history[-1][0]
        duration = end_t - start_t
        if duration <= 1e-12:
            self.on_parameters_changed()
            self.present(self._parent)
            return

        self._blocking_updates = True
        
        multipliers = {0: 1e9, 1: 1e6, 2: 1e3}
        selected_unit = self.range_unit.get_selected()
        mult = multipliers.get(selected_unit, 1e6)
        
        self.from_spin.set_value(start_t * mult)
        self.to_spin.set_value(end_t * mult)
        
        # Saner default zoom: scale so that the duration fits ~500 pixels wide
        scale_unit_mult = multipliers.get(self.scale_unit.get_selected(), 1e6)
        ideal_scale_val = (500.0 / duration) / scale_unit_mult
        clamped_scale_val = max(0.1, min(ideal_scale_val, 1000.0))
        self.scale_spin.set_value(clamped_scale_val)
        
        self._blocking_updates = False
        
        self.on_parameters_changed()
        self.present(self._parent)

    # Adw.Dialog has no usable get_visible(); return our own tracking flag instead
    def get_visible(self) -> bool:
        return self._is_presented