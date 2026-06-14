# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from ggate import Preference
from gi.repository import Gtk, Gdk, Adw, Pango
from gettext import gettext as _

class PreferencesWindow(Adw.PreferencesDialog):
    def __init__(self, parent):
        super().__init__()
        self.main_frame = parent
        self.color_buttons = {}

        self._build_ui()
        self._populate_values()
        self._connect_signals()

    def _build_ui(self):
        self.add(self._build_appearance_page())
        self.add(self._build_simulation_page())
        self.add(self._build_canvas_page())

    def _build_appearance_page(self):
        page = Adw.PreferencesPage()
        page.set_title(_("Appearance"))
        page.set_icon_name("preferences-desktop-wallpaper-symbolic")

        group_style = Adw.PreferencesGroup()
        group_style.set_title(_("Typography &amp; Style"))

        font_row = Adw.ActionRow()
        font_row.set_title(_("Font"))

        font_dialog = Gtk.FontDialog()
        monospace_filter = Gtk.CustomFilter.new(self._monospace_filter_func)
        font_dialog.set_filter(monospace_filter)

        self.drawing_font_btn = Gtk.FontDialogButton.new(font_dialog)
        self.drawing_font_btn.set_use_font(True)
        self.drawing_font_btn.set_use_size(True)
        self.drawing_font_btn.set_halign(Gtk.Align.END)
        self.drawing_font_btn.set_valign(Gtk.Align.CENTER)
        font_row.add_suffix(self.drawing_font_btn)
        group_style.add(font_row)

        self.symbol_type_row = Adw.ComboRow()
        self.symbol_type_row.set_title(_("Symbol style"))
        self.symbol_type_row.set_model(Gtk.StringList.new([_("MIL/ANSI"), _("IEC")]))
        group_style.add(self.symbol_type_row)

        page.add(group_style)

        group_canvas = Adw.PreferencesGroup()
        group_canvas.set_title(_("Canvas Colors"))
        group_canvas.add(self._create_color_row(_("Background (edit mode):"), "bg_color"))
        group_canvas.add(self._create_color_row(_("Background (running):"), "bg_color_running"))
        group_canvas.add(self._create_color_row(_("Grid:"), "grid_color"))
        group_canvas.add(self._create_color_row(_("Cursor:"), "cursor_color"))
        page.add(group_canvas)

        group_comp = Adw.PreferencesGroup()
        group_comp.set_title(_("Component Colors"))
        group_comp.add(self._create_color_row(_("Component (default):"), "component_color"))
        group_comp.add(self._create_color_row(_("Component (highlighted):"), "component_high_color"))
        group_comp.add(self._create_color_row(_("Component (running):"), "component_color_running"))
        group_comp.add(self._create_color_row(_("Component (picked):"), "picked_color"))
        group_comp.add(self._create_color_row(_("Component (pre-added):"), "preadd_color"))
        group_comp.add(self._create_color_row(_("Component (selected):"), "selected_color"))
        page.add(group_comp)

        group_net = Adw.PreferencesGroup()
        group_net.set_title(_("Net Colors"))
        group_net.add(self._create_color_row(_("Net (default):"), "net_color"))
        group_net.add(self._create_color_row(_("Net (highlighted):"), "net_high_color"))
        group_net.add(self._create_color_row(_("Net (running):"), "net_color_running"))
        group_net.add(self._create_color_row(_("Net (high level):"), "highlevel_color"))
        group_net.add(self._create_color_row(_("Net (low level):"), "lowlevel_color"))
        page.add(group_net)

        group_term = Adw.PreferencesGroup()
        group_term.set_title(_("Terminals"))
        group_term.add(self._create_color_row(_("Terminal (edit):"), "terminal_color"))
        group_term.add(self._create_color_row(_("Terminal (running):"), "terminal_color_running"))
        page.add(group_term)

        return page

    def _build_simulation_page(self):
        page = Adw.PreferencesPage()
        page.set_title(_("Simulation"))
        page.set_icon_name("media-playback-start-symbolic")

        group = Adw.PreferencesGroup()
        group.set_title(_("Performance &amp; Constraints"))

        self.calc_iter_row = Adw.SpinRow()
        self.calc_iter_row.set_title(_("Max calculation iterations"))
        group.add(self.calc_iter_row)

        self.calc_duration_row = Adw.SpinRow()
        self.calc_duration_row.set_title(_("Max calculation duration (µs)"))
        group.add(self.calc_duration_row)

        page.add(group)
        return page

    def _build_canvas_page(self):
        page = Adw.PreferencesPage()
        page.set_title(_("Canvas"))
        page.set_icon_name("input-mouse-symbolic")

        group = Adw.PreferencesGroup()
        group.set_title(_("Layout &amp; Grid"))

        self.autocenter_row = Adw.SwitchRow()
        self.autocenter_row.set_title(_("Auto-center content on resize"))
        group.add(self.autocenter_row)

        page.add(group)
        return page

    def _create_color_row(self, title, key):
        row = Adw.ActionRow()
        row.set_title(title)

        color_dialog = Gtk.ColorDialog()
        btn = Gtk.ColorDialogButton.new(color_dialog)
        btn.set_halign(Gtk.Align.END)
        btn.set_valign(Gtk.Align.CENTER)

        self.color_buttons[key] = btn
        row.add_suffix(btn)
        return row

    def _monospace_filter_func(self, item, user_data=None):
        if isinstance(item, Pango.FontFace):
            family = item.get_family()
        elif isinstance(item, Pango.FontFamily):
            family = item
        else:
            return False
        return family.is_monospace()

    def _populate_values(self):
        self.drawing_font_btn.set_font_desc(Preference.drawing_font)
        self.symbol_type_row.set_selected(Preference.symbol_type)

        for key, btn in self.color_buttons.items():
            pattern = Preference.__getattr__(key)
            r, g, b, _ = pattern.get_rgba()
            rgba = Gdk.RGBA()
            rgba.red = r
            rgba.green = g
            rgba.blue = b
            rgba.alpha = 1.0
            btn.set_rgba(rgba)

        adj_iter = Gtk.Adjustment.new(float(Preference.max_calc_iters), 10.0, 1000000.0, 1.0, 10.0, 0.0)
        self.calc_iter_row.set_adjustment(adj_iter)
        self.calc_iter_row.set_digits(0)

        adj_dur = Gtk.Adjustment.new(Preference.max_calc_duration * 1000000.0, 0.0, 100000.0, 1.0, 10.0, 0.0)
        self.calc_duration_row.set_adjustment(adj_dur)
        self.calc_duration_row.set_digits(3)

        self.autocenter_row.set_active(bool(Preference.autocenter_resize))

    def _connect_signals(self):
        self.drawing_font_btn.connect("notify::font-desc", self._on_font_changed)
        self.symbol_type_row.connect("notify::selected", self._on_symbol_type_changed)

        for key, btn in self.color_buttons.items():
            btn.connect("notify::rgba", self._on_color_changed, key)

        self.calc_iter_row.connect("notify::value", self._on_calc_iters_changed)
        self.calc_duration_row.connect("notify::value", self._on_calc_duration_changed)
        self.autocenter_row.connect("notify::active", self._on_autocenter_changed)

    def _on_font_changed(self, button, pspec):
        font_desc = button.get_font_desc()
        if font_desc:
            Preference.drawing_font = font_desc.to_string()
            Preference.save_settings()
            self._trigger_canvas_redraw()

    def _on_symbol_type_changed(self, row, pspec):
        Preference.symbol_type = row.get_selected()
        Preference.save_settings()
        self._trigger_canvas_redraw()

    def _on_color_changed(self, button, pspec, key):
        rgba = button.get_rgba()
        if rgba:
            Preference.__setattr__(key, f"{rgba.red},{rgba.green},{rgba.blue}")
            Preference.save_settings()
            self._trigger_canvas_redraw()

    def _on_calc_iters_changed(self, row, pspec):
        Preference.max_calc_iters = int(row.get_value())
        Preference.save_settings()
        self._trigger_canvas_redraw()

    def _on_calc_duration_changed(self, row, pspec):
        Preference.max_calc_duration = row.get_value() * 0.000001
        Preference.save_settings()
        self._trigger_canvas_redraw()

    def _on_autocenter_changed(self, row, pspec):
        Preference.autocenter_resize = int(row.get_active())
        Preference.save_settings()
        self._trigger_canvas_redraw()

    def _trigger_canvas_redraw(self):
        if self.main_frame and hasattr(self.main_frame, "drawarea"):
            self.main_frame.drawarea.redraw = True
            self.main_frame.drawarea.queue_draw()
