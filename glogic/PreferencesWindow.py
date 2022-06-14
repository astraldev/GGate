# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from glogic import const, Preference
from gi.repository import Gtk, Gdk
from gettext import gettext as _

class PreferencesWindow(Gtk.Dialog):
	def __init__(self, parent):

		Gtk.Dialog.__init__(self, title=_("Preferences"), transient_for=parent)
		self.set_resizable(False)
		self.set_modal(True)
		self.set_destroy_with_parent(True)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		pref = Gtk.Box(spacing=5)

		pref.append(Gtk.Label(label=_("Font:")))
		self.drawing_font_btn = Gtk.FontButton()
		pref.append(self.drawing_font_btn)
		vbox.append(pref)

		table = Gtk.Grid()
		table.set_column_spacing(5)

		prefset = (("net_color", _("Net:")),                    ("net_high_color", _("Net (highlighted):")),             ("net_color_running", _("Net (running):")),
		           ("highlevel_color", _("Net (high level):")), ("lowlevel_color", _("Net (low level):")),               None,
		           ("component_color", _("Component:")),        ("component_high_color", _("Component (highlighted):")), ("component_color_running", _("Component (running):")),
		           ("picked_color", _("Component (picked):")),  ("preadd_color", _("Component (pre added):")),           ("selected_color", _("Component (selected):")),
		           ("terminal_color", _("Terminal:")),          ("terminal_color_running", _("Terminal (running):")),    ("cursor_color", _("Cursor:")),
		           ("bg_color", _("Background:")),              ("bg_color_running", _("Background (running):")),        ("grid_color", _("Grid:")),
		          )

		self.color_buttons = {}
		for i, prefpair in enumerate(prefset):
			if prefpair is None:
				continue
			caption = Gtk.Label(label=prefpair[1])
			caption.set_margin_start(2)
			caption.set_margin_top(1)
			table.attach(caption, i % 3 * 2, i % 3 * 2 + 1, 1, 1)
			colorbutton = Gtk.ColorButton()
			self.color_buttons[prefpair[0]] = colorbutton
			table.attach(colorbutton, i % 3 * 2 + 1, i % 3 * 2 + 2, 1 ,1)

		vbox.append(table)
		table.set_vexpand(True)
		table.set_hexpand(True)

		pref = Gtk.Box(spacing=5)
		pref.append(Gtk.Label(label=_("Symbol type:")))
		self.symbol_type_combo = Gtk.ComboBoxText()
		self.symbol_type_combo.set_entry_text_column(0)
		self.symbol_type_combo.append_text(_("MIL/ANSI"))
		self.symbol_type_combo.append_text(_("IEC"))
		pref.append(self.symbol_type_combo)

		vbox.append(pref)
		pref.set_vexpand(True)
		pref.set_hexpand(True)

		pref = Gtk.Box(spacing=5)
		pref.append(Gtk.Label(label=_("Max calc iters:")))
		self.calc_iter_spin = Gtk.SpinButton()
		self.calc_iter_spin.set_increments(1, 10)
		self.calc_iter_spin.set_range(10, 1000000)
		pref.append(self.calc_iter_spin)
		pref.append(Gtk.Label(label=_("Max calc duration [µs]:")))
		self.calc_duration_spin = Gtk.SpinButton()
		self.calc_duration_spin.set_increments(1, 10)
		self.calc_duration_spin.set_range(0, 100000)
		self.calc_duration_spin.set_digits(3)
		pref.append(self.calc_duration_spin)
		vbox.append(pref)
		pref.set_vexpand(True)
		pref.set_hexpand(True)

		box = self.get_content_area()
		box.append(vbox)

		box.show()

	def update_dialog(self):
		self.drawing_font_btn.set_font_name(Preference.drawing_font.to_string())

		for key in self.color_buttons:
			rgba = Preference.__getattr__(key).get_rgba()
			self.color_buttons[key].set_color(Gdk.Color(rgba[0]*65535, rgba[1]*65535, rgba[2]*65535))

		self.symbol_type_combo.set_active(Preference.symbol_type)
		self.calc_iter_spin.set_value(Preference.max_calc_iters)
		self.calc_duration_spin.set_value(Preference.max_calc_duration * 1000000)

	def apply_settings(self):
		Preference.drawing_font = self.drawing_font_btn.get_font_name()

		for key in self.color_buttons:
			color = self.color_buttons[key].get_color()
			Preference.__setattr__(key, "%f,%f,%f" % (color.red / 65536, color.green / 65536, color.blue / 65536))

		Preference.symbol_type = self.symbol_type_combo.get_active()
		Preference.max_calc_iters = self.calc_iter_spin.get_value()
		Preference.max_calc_duration = self.calc_duration_spin.get_value() * 0.000001
