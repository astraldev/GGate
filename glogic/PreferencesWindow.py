# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from glogic import const, Preference
from gi.repository import Gtk, Gdk
from gettext import gettext as _


class PreferencesWindow(Gtk.Dialog):
    def __init__(self, parent):

        Gtk.Dialog.__init__(self, title=_("Preferences"), use_header_bar=True, transient_for=parent)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_destroy_with_parent(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        pref = Gtk.Box(spacing=5)

        font_label = Gtk.Label(label=_("Font:"))
        font_label.set_margin_start(5)
        pref.append(font_label)
        self.drawing_font_btn = Gtk.FontButton()
        self.drawing_font_btn.set_halign(Gtk.Align.END)
        pref.append(self.drawing_font_btn)
        vbox.append(pref)

        table = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        table.set_margin_top(5)
        table.set_margin_bottom(5)

        prefset = {
            'net colors: ': [
                    ("net_color", _("Net:")),
                    ("net_high_color", _("Net (highlighted):")),
                    ("net_color_running", _("Net (running):")),
                    ("highlevel_color", _("Net (high level):")), 
                    ("lowlevel_color", _("Net (low level):"))
                   ],
            'component colors': [
                ("component_color", _("Component:")),        
                ("component_high_color", _("Component (highlighted):")), 
                ("component_color_running", _("Component (running):")),
                ("picked_color", _("Component (picked):")),  
                ("preadd_color", _("Component (pre added):")),           
                ("selected_color", _("Component (selected):"))
            ],
            'terminals color': [
                ("terminal_color", _("Terminal:")),          
                ("terminal_color_running", _("Terminal (running):")),    
                ("cursor_color", _("Cursor:")),
                ("bg_color", _("Background:")),              
                ("bg_color_running", _("Background (running):")),        
                ("grid_color", _("Grid:"))
            ],
        }

        self.color_buttons = {}

        for key in prefset.keys():
            frame = Gtk.Frame()
            listBox = Gtk.ListBox()
            listBox.set_selection_mode(Gtk.SelectionMode.NONE)
            listBox.add_css_class("rich-list")
            listBox.add_css_class("view")

            section_row = Gtk.ListBoxRow()
            section_row.set_activatable(False)
            _label = Gtk.Label()
            _box = Gtk.Box()

            _label.set_markup(f'<b>{key.capitalize()}</b>')

            _box.append(_label)
            _box.set_size_request(-1, 35)
            section_row.set_selectable(False)

            section_row.set_child(_box)
            listBox.append(section_row)

            for prefpair in prefset[key]:
                caption_label = Gtk.Label()
                caption = Gtk.Box()

                caption_label.set_text(prefpair[1])
                caption.set_size_request(180, -1)
                caption.set_halign(Gtk.Align.START)
                caption.set_hexpand(True)
                
                caption.append(caption_label)
                caption.set_margin_start(7)
                
                color_button = Gtk.ColorButton()
                self.color_buttons[prefpair[0]] = color_button

                box = Gtk.Box()
                box.append(caption)
                box.append(color_button)

                row = Gtk.ListBoxRow()
                row.set_activatable(False)
                row.set_child(box)

                listBox.append(row)
            
            table.append(frame)
            frame.set_child(listBox)
            frame.set_margin_start(2)
            frame.set_margin_end(2)

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

        # vbox.append(pref)
        # pref.set_vexpand(True)
        # pref.set_hexpand(True)

        # pref = Gtk.Box(spacing=5)

        pref.append(Gtk.Label(label=_("Max calc iters:")))
        self.calc_iter_spin = Gtk.SpinButton()
        self.calc_iter_spin.set_hexpand(True)
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

        vbox.set_margin_start(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_end(10)

        pref.set_vexpand(True)
        pref.set_hexpand(True)

        box = self.get_content_area()
        box.append(vbox)

        box.show()


        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        apply_button = self.add_button("Apply", Gtk.ResponseType.APPLY)
        apply_button.add_css_class("suggested-action")

    def update_dialog(self):

        self.drawing_font_btn.set_use_font(True)
        self.drawing_font_btn.set_font(Preference.drawing_font.to_string())

        for key in self.color_buttons:
            rgba = Preference.__getattr__(key).get_rgba()
            color = Gdk.RGBA()
            color.red = round(rgba[0], 2)
            color.green = round(rgba[1], 2)
            color.blue = round(rgba[2], 2)
            color.alpha = 1.0

            self.color_buttons[key].set_rgba(color)

        self.symbol_type_combo.set_active(Preference.symbol_type)
        self.calc_iter_spin.set_value(Preference.max_calc_iters)
        self.calc_duration_spin.set_value(Preference.max_calc_duration * 1000000)

    def apply_settings(self):
        Preference.drawing_font = self.drawing_font_btn.get_font()

        for key in self.color_buttons:
            color = self.color_buttons[key].get_rgba()
            Preference.__setattr__(key, "%f,%f,%f" % (color.red , color.green , color.blue ))

        Preference.symbol_type = self.symbol_type_combo.get_active()
        Preference.max_calc_iters = self.calc_iter_spin.get_value()
        Preference.max_calc_duration = self.calc_duration_spin.get_value() * 0.000001