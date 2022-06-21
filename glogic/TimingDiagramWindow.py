# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import gettext
from glogic import config, const
from glogic.DiagramArea import DiagramArea
from glogic.Exporter import save_timingdiagram_as_image
from gi.repository import Gtk, Gdk
from gettext import gettext as _

class TimingDiagramWindow(Gtk.Window):
	def __init__(self, parent):
		Gtk.Window.__init__(self, title=_("Timimg diagram"))
		self.set_default_size(640, 200)
		self.parent = parent
		#self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
		self.set_transient_for(parent)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		# Create option buttons
		hbox1 = Gtk.Box()

		scale_list = Gtk.ListStore(str)
		scales = ["500.0", "200.0", "100.0", "50.0", "20.0", "10.0", "5.0", "2.0", "1.0"]
		for scale in scales:
			scale_list.insert_with_values(0, range(len(scales)), [scale])

		unit_list = Gtk.ListStore(str)
		units = ["ns", "µs", "ms"]
		for unit in units:
			unit_list.insert_with_values(0, range(len(units)), [unit])

		scalebox = Gtk.Box()


		self.scale_combo = Gtk.ComboBox.new_with_model_and_entry(scale_list)
		# self.scale_combo.set_events(Gdk.EventMask.FOCUS_CHANGE_MASK)
		self.scale_combo.get_child().connect("activate", self.on_scale_combo_activate)

		focus_event_controller = Gtk.EventControllerFocus()
		focus_event_controller.connect('leave', self.on_scale_combo_focusout)
		self.scale_combo.get_child().add_controller(focus_event_controller)
		
		self.scale_combo.get_child().set_width_chars(6)
		self.scale_combo.set_entry_text_column(0)
		self.scale_combo.get_child().set_text("5.0")

		scalebox.append(Gtk.Label(label=_("Scale:")))
		scalebox.append(self.scale_combo)
		scalebox.append(Gtk.Label(label="px/"))


		self.scale_unit_combo = Gtk.ComboBox.new_with_model(unit_list)
		renderer_text = Gtk.CellRendererText()
		self.scale_unit_combo.pack_start(renderer_text, True)
		self.scale_unit_combo.add_attribute(renderer_text, "text", 0)
		self.scale_unit_combo.set_active(1)
		self.scale_unit_combo_changed_id = self.scale_unit_combo.connect("changed", self.on_combo_changed)
		
		scalebox.append(self.scale_unit_combo)

		hbox1.append(scalebox)

		rangebox = Gtk.Box()

		rangebox.append(Gtk.Label(label=_("Range:")))

		self.from_spin = Gtk.SpinButton()
		self.from_spin.set_increments(1, 10)
		self.from_spin.set_range(0, 10000)
		self.from_spin.set_digits(2)
		self.from_spin.set_value(0)
		self.from_spin_changed_id = self.from_spin.connect("changed", self.on_from_time_changed)
		rangebox.append(self.from_spin)

		self.from_combo = Gtk.ComboBox.new_with_model(unit_list)
		renderer_text = Gtk.CellRendererText()
		self.from_combo.pack_start(renderer_text, True)
		self.from_combo.add_attribute(renderer_text, "text", 0)
		self.from_combo.set_active(1)
		self.from_combo_changed_id = self.from_combo.connect("changed", self.on_combo_changed)
		rangebox.append(self.from_combo)

		rangebox.append(Gtk.Label(label = "-"))

		self.to_spin = Gtk.SpinButton()
		self.to_spin.set_increments(1, 10)
		self.to_spin.set_range(0, 10000)
		self.to_spin.set_digits(2)
		self.to_spin.set_value(200.0)
		self.to_spin_changed_id = self.to_spin.connect("changed", self.on_to_time_changed)
		rangebox.append(self.to_spin)

		self.to_combo = Gtk.ComboBox.new_with_model(unit_list)
		renderer_text = Gtk.CellRendererText()
		self.to_combo.pack_start(renderer_text, True)
		self.to_combo.add_attribute(renderer_text, "text", 0)
		self.to_combo.set_active(1)
		self.to_combo_changed_id = self.to_combo.connect("changed", self.on_combo_changed)
		rangebox.append(self.to_combo)

		hbox1.append(rangebox)

		self.redraw_btn = Gtk.Button(label=_("_Redraw"))
		self.redraw_btn.set_use_underline(True)
		self.redraw_btn.connect("clicked", self.on_redraw_clicked)
		hbox1.append(self.redraw_btn)

		self.saveimage_btn = Gtk.Button(label=_("Save _diagram..."))
		self.saveimage_btn.set_use_underline(True)
		self.saveimage_btn.connect("clicked", self.on_saveimage_clicked)
		hbox1.append(self.saveimage_btn)

		vbox.append(hbox1)
		
		hbox2 = Gtk.Box()

		cursorbox = Gtk.Box()

		cursorbox.append(Gtk.Label(label=_("Cursor position:")))

		self.cursor_spin = Gtk.SpinButton()
		self.cursor_spin.set_increments(1, 10)
		self.cursor_spin.set_range(0, 10000)
		self.cursor_spin.set_digits(2)
		self.cursor_spin.set_value(200.0)
		self.cursor_spin_changed_id = self.cursor_spin.connect("changed", self.on_cursor_spin_changed)
		cursorbox.append(self.cursor_spin)

		self.cursor_combo = Gtk.ComboBox.new_with_model(unit_list)
		renderer_text = Gtk.CellRendererText()
		self.cursor_combo.pack_start(renderer_text, True)
		self.cursor_combo.add_attribute(renderer_text, "text", 0)
		self.cursor_combo.set_active(1)
		self.cursor_combo_changed_id = self.cursor_combo.connect("changed", self.on_combo_changed)
		cursorbox.append(self.cursor_combo)

		hbox2.append(cursorbox)

		vbox.append(hbox2)

		self.diagramarea = DiagramArea(self.parent.circuit, self.parent.drawarea)
		self.parent.circuit.connect("currenttime-changed", self.on_diagramarea_currtime_changed)
		vbox.append(self.diagramarea)

		self.set_child(vbox)

	def check_scale_format(self):
		try:
			scale = float(self.scale_combo.get_child().get_text())
			if scale == int(scale):
				self.scale_combo.get_child().set_text(str(int(scale)) + ".0")
		except ValueError:
			scale = 5.0
			self.scale_combo.get_child().set_text("5.0")

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

	def on_diagramarea_currtime_changed(self, diagramarea, time):
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

	def on_to_time_changed(self, widget):
		from_time = self.from_spin.get_value()
		to_time = self.to_spin.get_value()
		if from_time > to_time:
			self.from_spin.disconnect(self.from_spin_changed_id)
			self.from_spin.set_value(to_time)
			self.from_spin_changed_id = self.from_spin.connect("changed", self.on_from_time_changed)

	def on_cursor_spin_changed(self, widget):
		self.diagramarea.set_time(self.expand_time(self.cursor_spin.get_value(), self.cursor_combo.get_active()))

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
		self.diagramarea.set_time(self.expand_time(self.cursor_spin.get_value(), self.cursor_combo.get_active()))

	def on_redraw_clicked(self, widget):
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
			self.diagramarea.scale = new_scale
			self.diagramarea.diagram_unit = new_diagram_unit
			self.diagramarea.start_time = new_start_time
			self.diagramarea.end_time = new_end_time
			self.diagramarea.createDiagram()

	def on_saveimage_clicked(self, widget):
		save_timingdiagram_as_image(self.diagramarea, self)
