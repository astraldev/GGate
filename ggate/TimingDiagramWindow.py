# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import gettext
from ggate import config, const
from ggate.DiagramArea import DiagramArea
from ggate.Exporter import save_timing_diagram_as_image
from gi.repository import Gtk, Gdk
from gettext import gettext as _

class TimingDiagramWindow(Gtk.Window):
	def __init__(self, parent):
		Gtk.Window.__init__(self, title=_("Timing diagram"))
		self.set_default_size(480, 480)
		self.parent = parent
		self.set_hide_on_close(True)
		# self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
		self.set_transient_for(parent)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		self.scale_list = Gtk.ListStore(str)
		scales = ["500.0", "200.0", "100.0", "50.0", "20.0", "10.0", "5.0", "2.0", "1.0"]
		for scale in scales:
			self.scale_list.insert_with_values(0, range(len(scales)), [scale])
			
		self.units = ["ns", "µs", "ms"]
		
		# Scale
		vbox.append(self._get_scale())

		# Cursor Position
		vbox.append(self._get_cursor_position())

		# Range
		vbox.append(self._get_range())

		# Save button
		vbox.append(self._get_save())

		self.diagram_area = DiagramArea(self.parent.circuit, self.parent.drawarea)
		self.parent.circuit.connect("currenttime-changed", self.on_diagram_area_current_time_changed)
		vbox.append(self.diagram_area)

		vbox.set_margin_top(3)
		vbox.set_margin_bottom(6)
		vbox.set_margin_start(6)
		vbox.set_margin_end(6)

		self.set_child(vbox)
	
	def _get_save(self): # Save image
		save_image_btn = Gtk.Button(label=_("Save _diagram..."))
		save_image_btn.set_use_underline(True)
		save_image_btn.connect("clicked", self.on_save_image_clicked)
		save_image_btn.set_margin_bottom(6)

		return save_image_btn
	
	def _get_unit_list(self):
		unit_list = Gtk.ListStore(str)
		for unit in self.units:
			unit_list.insert_with_values(0, range(len(self.units)), [unit])
		
		return unit_list

	
	def _get_cursor_position(self):

		self.cursor_spin = Gtk.SpinButton(hexpand=True)
		self.cursor_spin.set_increments(1, 10)
		self.cursor_spin.set_range(0, 10000)
		self.cursor_spin.set_digits(2)
		self.cursor_spin.set_value(200.0)
		self.cursor_spin_changed_id = self.cursor_spin.connect("changed", self.on_cursor_spin_changed)

		self.cursor_combo = Gtk.ComboBox.new_with_model(self._get_unit_list())
		renderer_text = Gtk.CellRendererText()
		self.cursor_combo.pack_start(renderer_text, True)
		self.cursor_combo.add_attribute(renderer_text, "text", 0)
		self.cursor_combo.set_active(1)
		self.cursor_combo_changed_id = self.cursor_combo.connect("changed", self.on_combo_changed)

		cursor_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
		cursor_box.append(self.cursor_spin)
		cursor_box.append(self.cursor_combo)
		cursor_box.add_css_class("linked")
		
		frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		frame_label = Gtk.Box()
		frame_label.append(Gtk.Label(label=_("Cursor position:")))
		frame.append(frame_label)
		frame.append(cursor_box)

		frame.set_margin_top(3)
		frame.set_margin_bottom(3)

		return frame

	def _get_scale(self):
		self.scale_combo = Gtk.ComboBox.new_with_model_and_entry(self.scale_list)
		# self.scale_combo.set_events(Gdk.EventMask.FOCUS_CHANGE_MASK)
		self.scale_combo.get_child().connect("activate", self.on_scale_combo_activate)

		focus_event_controller = Gtk.EventControllerFocus()
		focus_event_controller.connect('leave', self.on_scale_combo_focusout)

		self.scale_combo.get_child().add_controller(focus_event_controller)
		self.scale_combo.get_child().set_width_chars(6)
		self.scale_combo.set_entry_text_column(0)
		self.scale_combo.get_child().set_text("5.0")

		self.scale_unit_combo = Gtk.ComboBox.new_with_model(self._get_unit_list())
		renderer_text = Gtk.CellRendererText()
		self.scale_unit_combo.pack_start(renderer_text, True)
		self.scale_unit_combo.add_attribute(renderer_text, "text", 0)
		self.scale_unit_combo.set_active(1)
		self.scale_unit_combo_changed_id = self.scale_unit_combo.connect("changed", self.on_combo_changed)
		
		scale_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		scale_box.append(self.scale_combo)
		scale_box.append(self.scale_unit_combo)
		scale_box.add_css_class("linked")

		frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		frame_label = Gtk.Box()
		frame_label.append(Gtk.Label(label=_("Scale (px):")))
		frame.append(frame_label)
		frame.append(scale_box)

		frame.set_margin_top(3)
		frame.set_margin_bottom(3)

		return frame
		
	def _get_range(self):
		# From
		from_label = Gtk.Box()
		from_label.append(Gtk.Label(label=_("From")))

		from_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
		inner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)

		self.from_spin = Gtk.SpinButton(hexpand=True)
		self.from_spin.set_increments(1, 10)
		self.from_spin.set_range(0, 10000)
		self.from_spin.set_digits(2)
		self.from_spin.set_value(0)
		self.from_spin_changed_id = self.from_spin.connect("changed", self.on_from_time_changed)

		self.from_combo = Gtk.ComboBox.new_with_model(self._get_unit_list())
		renderer_text = Gtk.CellRendererText()
		self.from_combo.pack_start(renderer_text, True)
		self.from_combo.add_attribute(renderer_text, "text", 0)
		self.from_combo.set_active(1)
		self.from_combo_changed_id = self.from_combo.connect("changed", self.on_combo_changed)

		inner_box.append(self.from_spin)
		inner_box.append(self.from_combo)
		inner_box.add_css_class("linked")
		inner_box.set_margin_end(3)
		
		from_box.append(from_label)
		from_box.append(inner_box)

		# To
		to_label = Gtk.Box()
		to_label.append(Gtk.Label(label=_("To")))
		to_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
		inner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)

		self.to_spin = Gtk.SpinButton(hexpand=True)
		self.to_spin.set_increments(1, 10)
		self.to_spin.set_range(0, 10000)
		self.to_spin.set_digits(2)
		self.to_spin.set_value(200.0)
		self.to_spin_changed_id = self.to_spin.connect("changed", self.on_to_time_changed)

		self.to_combo = Gtk.ComboBox.new_with_model(self._get_unit_list())
		renderer_text = Gtk.CellRendererText()
		self.to_combo.pack_start(renderer_text, True)
		self.to_combo.add_attribute(renderer_text, "text", 0)
		self.to_combo.set_active(1)
		self.to_combo_changed_id = self.to_combo.connect("changed", self.on_combo_changed)

		inner_box.append(self.to_spin)
		inner_box.append(self.to_combo)
		inner_box.add_css_class("linked")
		inner_box.set_margin_start(3)
		
		to_box.append(to_label)
		to_box.append(inner_box)

		# Container		
		frame = Gtk.Frame(label=_("Range:"))

		range_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		range_box.append(from_box)
		range_box.append(to_box)
		range_box.set_margin_end(3)
		range_box.set_margin_start(3)
		range_box.set_margin_bottom(3)

		frame.set_child(range_box)

		frame.set_margin_top(3)
		frame.set_margin_bottom(3)

		return frame


	def check_scale_format(self):
		try:
			scale = float(self.scale_combo.get_child().get_text())
			if scale == int(scale):
				self.scale_combo.get_child().set_text(str(int(scale)) + ".0")
		except ValueError:
			scale = 5.0
			self.scale_combo.get_child().set_text("5.0")
			
		self.on_redraw()

	def on_scale_combo_activate(self, *widget):
		self.check_scale_format()

	def on_scale_combo_focusout(self, *args):
		self.check_scale_format()

	def expand_time(self, time, unit):
		if unit == 0:
			return time / 1000000000
		elif unit == 1:
			return time / 1000000
		else:
			return time / 1000

	def on_diagram_area_current_time_changed(self, diagram_area, time):
		unit = self.cursor_combo.get_active()
		if unit == 0:
			self.cursor_spin.set_value(time * 1000000000)
		elif unit == 1:
			self.cursor_spin.set_value(time * 1000000)
		else:
			self.cursor_spin.set_value(time * 1000)

	def on_from_time_changed(self, widget):
		from_time = self.from_spin.get_value()
		to_time = self.to_spin.get_value()
		if from_time > to_time:
			self.to_spin.disconnect(self.to_spin_changed_id)
			self.to_spin.set_value(from_time)
			self.to_spin_changed_id = self.to_spin.connect("changed", self.on_to_time_changed)
			self.on_redraw()


	def on_to_time_changed(self, widget):
		from_time = self.from_spin.get_value()
		to_time = self.to_spin.get_value()
		if from_time > to_time:
			self.from_spin.disconnect(self.from_spin_changed_id)
			self.from_spin.set_value(to_time)
			self.from_spin_changed_id = self.from_spin.connect("changed", self.on_from_time_changed)
			self.on_redraw()


	def on_cursor_spin_changed(self, widget):
		self.diagram_area.set_time(self.expand_time(self.cursor_spin.get_value(), self.cursor_combo.get_active()))
		self.on_redraw()

	def on_combo_changed(self, widget):
		self.scale_unit_combo.disconnect(self.scale_unit_combo_changed_id)
		self.from_combo.disconnect(self.from_combo_changed_id)
		self.to_combo.disconnect(self.to_combo_changed_id)
		self.cursor_combo.disconnect(self.cursor_combo_changed_id)
		self.scale_unit_combo.set_active(widget.get_active())
		self.from_combo.set_active(widget.get_active())
		self.to_combo.set_active(widget.get_active())
		self.cursor_combo.set_active(widget.get_active())
		self.scale_unit_combo_changed_id = self.scale_unit_combo.connect("changed", self.on_combo_changed)
		self.from_combo_changed_id = self.from_combo.connect("changed", self.on_combo_changed)
		self.to_combo_changed_id = self.to_combo.connect("changed", self.on_combo_changed)
		self.cursor_combo_changed_id = self.cursor_combo.connect("changed", self.on_combo_changed)
		self.diagram_area.set_time(self.expand_time(self.cursor_spin.get_value(), self.cursor_combo.get_active()))
		self.on_redraw()

	def on_redraw(self, *args):
		if self.scale_unit_combo.get_active() == 0:
			new_scale = float(self.scale_combo.get_child().get_text()) * 1000000000
		elif self.scale_unit_combo.get_active() == 1:
			new_scale = float(self.scale_combo.get_child().get_text()) * 1000000
		else:
			new_scale = float(self.scale_combo.get_child().get_text()) * 1000

		new_diagram_unit = self.scale_unit_combo.get_active()
		new_start_time = self.expand_time(self.from_spin.get_value(), self.from_combo.get_active())
		new_end_time = self.expand_time(self.to_spin.get_value(), self.to_combo.get_active())

		diagram_width = int((new_end_time - new_start_time) * new_scale)

		if diagram_width > 5000:
			dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.ERROR, button_type=Gtk.ButtonsType.OK)
			dialog.set_modal(True)
			dialog.set_markup(_("Can't create timing diagram!"))
			dialog.get_message_area().append(Gtk.Label(label=_("The width of the timing diagram will be too wide. (> 5000)")))
			dialog.present()

		else:
			self.diagram_area.scale = new_scale
			self.diagram_area.diagram_unit = new_diagram_unit
			self.diagram_area.start_time = new_start_time
			self.diagram_area.end_time = new_end_time
			self.diagram_area.createDiagram()

	def on_save_image_clicked(self, widget):
		save_timing_diagram_as_image(self.diagram_area, self)
