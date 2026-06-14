from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ggate.MainFrame import MainFrame

import math
import cairo
from decimal import Decimal
from gettext import gettext as _
from ggate import Preference
from ggate.Utils import cairo_draw_text, cairo_paths
from ggate.const import Definitions
from gi.repository import Gtk, Gdk, PangoCairo

# Ruler strip height in pixels; each probe row is also _ROW_H px.
_ROW_H = 40

class TimingGraphDiagram(Gtk.Box):
    def __init__(self, parent: MainFrame):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        # expand to fill all space given by the ToolbarView content area
        self.set_hexpand(True)
        self.set_vexpand(True)

        self._circuit = parent.circuit
        self._parent_drawarea = parent.drawarea

        self.name_width = 150
        self.diagram_width = 1
        self.img_height = 1

        self.start_time = 0.0
        self.end_time = 0.0002
        self.scale = 5000000.0
        self.timing_unit = 1
        self.gra_pix = 150

        self.show_cursor = False
        self.cursor_x = 0
        self.mouse_down = False

        self.name_area = Gtk.DrawingArea()
        self.name_area.set_draw_func(self.name_area_draw_fn)

        self.chart_area = Gtk.DrawingArea()
        self.chart_area.set_draw_func(self.chart_area_draw_fn)
        self.chart_area.set_hexpand(True)  # fills viewport width before scrolling kicks in

        self.name_scroll = Gtk.ScrolledWindow()
        self.name_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.name_scroll.set_hexpand(False)
        self.name_scroll.set_vexpand(True)
        self.name_scroll.set_child(self.name_area)

        self.diagram_scroll = Gtk.ScrolledWindow()
        self.diagram_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.diagram_scroll.set_hexpand(True)
        self.diagram_scroll.set_vexpand(True)
        self.diagram_scroll.set_child(self.chart_area)

        # share diagram's vertical adjustment so both columns scroll in sync
        self.name_scroll.set_vadjustment(self.diagram_scroll.get_vadjustment())

        self.append(self.name_scroll)
        self.append(self.diagram_scroll)

        click_gesture = Gtk.GestureClick()
        click_gesture.set_button(Gdk.BUTTON_PRIMARY)
        click_gesture.connect("pressed", self.on_timing_diagram_click)
        click_gesture.connect("released", self.on_timing_diagram_release)
        self.chart_area.add_controller(click_gesture)

        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect("motion", self.on_timing_diagram_motion)
        motion_controller.connect("leave", self.on_timing_diagram_leave)
        self.chart_area.add_controller(motion_controller)

        self.update_layout_sizes()

    def __get_probes(self):
        return [
            cmp
            for cmp in self._circuit.components
            if cmp[0] == Definitions.component_probe
        ]

    def update_layout_sizes(self):
        n = len(self.__get_probes())
        self.img_height = _ROW_H + n * _ROW_H          # ruler row + one row per probe
        self.diagram_width = int(max(1, (self.end_time - self.start_time) * self.scale))
        # set_size_request only ever called here — never inside a draw callback (avoids layout loop)
        self.name_area.set_size_request(self.name_width, self.img_height)
        self.chart_area.set_size_request(self.diagram_width, self.img_height)

    def draw(self):
        self.update_layout_sizes()
        self.name_area.queue_draw()
        self.chart_area.queue_draw()

    # ── draw callbacks ────────────────────────────────────────────────────────

    def name_area_draw_fn(self, drawing_area, cr: cairo.Context, width, height, *args):
        self.draw_names(cr)

    def chart_area_draw_fn(self, drawing_area, cr: cairo.Context, width, height, *args):
        history = self._circuit.probe_levels_history
        if not history:
            cr.set_source(Preference.bg_color_running)
            cr.rectangle(0, 0, width, height)
            cr.fill()
            layout = PangoCairo.create_layout(cr)
            layout.set_font_description(Preference.drawing_font)
            msg = _("No simulation steps recorded. Operate inputs to advance simulation.")
            cr.set_source(Preference.component_color_running)
            cairo_draw_text(cr, layout, msg, width / 2, height / 2, 0.5, 0.5)
            cr.fill()
            return

        self.draw_diagrams(cr)

        current_time_x = (self._circuit.current_time - self.start_time) * self.scale
        if 0 <= current_time_x <= self.diagram_width:
            cr.set_source(Preference.terminal_color)
            cr.set_line_width(1.0)
            cairo_paths(cr, (current_time_x + 0.5, _ROW_H), (current_time_x + 0.5, self.img_height))  # +0.5 aligns 1px stroke to pixel grid
            cr.stroke()

        if self.show_cursor and 0 <= self.cursor_x <= self.diagram_width:
            cr.set_source(Preference.cursor_color)
            cr.set_line_width(1.0)
            cairo_paths(cr, (self.cursor_x + 0.5, _ROW_H), (self.cursor_x + 0.5, self.img_height))
            cr.stroke()

    # ── exporter-compatible public draw methods ───────────────────────────────

    def draw_names(self, cr: cairo.Context):
        probes = self.__get_probes()
        name_layout = PangoCairo.create_layout(cr)
        name_layout.set_font_description(Preference.drawing_font)

        # background
        cr.set_source(Preference.bg_color_running)
        cr.rectangle(0, 0, self.name_width, self.img_height)
        cr.fill()

        # outer border + row separators
        cr.set_source(Preference.grid_color)
        cr.set_line_width(1.0)
        cr.rectangle(0.5, 0.5, self.name_width - 1, self.img_height - 1)
        cr.stroke()

        # ruler / header bottom divider
        cairo_paths(cr, (0, _ROW_H - 0.5), (self.name_width, _ROW_H - 0.5))
        cr.stroke()

        # probe row separators
        for j in range(len(probes)):
            sep_y = _ROW_H + j * _ROW_H + _ROW_H - 0.5
            cairo_paths(cr, (0, sep_y), (self.name_width, sep_y))
        cr.stroke()

        # header label ("Time [µs]") right-aligned into the ruler strip
        unit_str = ["ns", "µs", "ms"][self.timing_unit]
        cr.set_source(Preference.component_color_running)
        cairo_draw_text(cr, name_layout, f"{_('Time')} [{unit_str}]", self.name_width - 6, _ROW_H // 2, 1.0, 0.5)
        cr.fill()

        # probe name labels, vertically centred in each row
        for j, probe in enumerate(probes):
            row_mid = _ROW_H + j * _ROW_H + _ROW_H // 2
            cairo_draw_text(cr, name_layout, probe[1].values[0], 8, row_mid, 0, 0.5)
        cr.fill()

    def draw_diagrams(self, cr: cairo.Context):
        probes = self.__get_probes()
        diagram_layout = PangoCairo.create_layout(cr)
        diagram_layout.set_font_description(Preference.drawing_font)

        # background
        cr.set_source(Preference.bg_color_running)
        cr.rectangle(0, 0, self.diagram_width, self.img_height)
        cr.fill()

        # outer border
        cr.set_source(Preference.grid_color)
        cr.set_line_width(1.0)
        cairo_paths(cr, (0, 0.5), (self.diagram_width, 0.5))
        cairo_paths(cr, (self.diagram_width - 0.5, 0), (self.diagram_width - 0.5, self.img_height))
        cairo_paths(cr, (0, self.img_height - 0.5), (self.diagram_width, self.img_height - 0.5))
        cr.stroke()

        # ruler bottom divider + row separators
        cairo_paths(cr, (0, _ROW_H - 0.5), (self.diagram_width, _ROW_H - 0.5))
        for j in range(len(probes)):
            sep_y = _ROW_H + j * _ROW_H + _ROW_H - 0.5
            cairo_paths(cr, (0, sep_y), (self.diagram_width, sep_y))
        cr.stroke()

        history = self._circuit.probe_levels_history
        if not history:
            return

        self._draw_graduations(cr, diagram_layout)
        self._draw_waveforms(cr, history, probes)

    def _draw_graduations(self, cr: cairo.Context, layout):
        if self.scale <= 0:
            return
        gra_p = Decimal(self.gra_pix) / Decimal(self.scale)
        if gra_p <= 0:
            return
        order = 10 ** Decimal(int(math.log10(gra_p)))
        grasec_top = gra_p / order
        # round to nearest "nice" step: 0.1, 0.2, or 0.5 × the leading power-of-10
        if 0.15 <= grasec_top < 0.35:
            gra_p = order * Decimal("0.2")
        elif 0.35 <= grasec_top <= 0.75:
            gra_p = order * Decimal("0.5")
        else:
            gra_p = order * Decimal("0.1")

        unit_multipliers = {0: 1000000000.0, 1: 1000000.0, 2: 1000.0}
        mult = unit_multipliers.get(self.timing_unit, 1000000.0)
        u_start = self.start_time * mult
        u_end = self.end_time * mult
        u_gra_p = float(gra_p) * mult

        ruler_mid = _ROW_H // 2

        # start / end boundary labels
        cr.set_source(Preference.component_color_running)
        cairo_draw_text(cr, layout, str(Decimal(u_start).quantize(Decimal(".00"))), 4, ruler_mid, 0.0, 0.5)
        cairo_draw_text(cr, layout, str(Decimal(u_end).quantize(Decimal(".00"))), self.diagram_width - 4, ruler_mid, 1.0, 0.5)
        cr.fill()

        u_gra_sec = Decimal(u_gra_p)
        gra_sec = Decimal(gra_p)
        u_gra_p_dec = Decimal(u_gra_p)
        u_end_dec = Decimal(u_end)

        while True:
            if u_gra_sec + u_gra_p_dec / 4 >= u_end_dec:
                break
            x = int(float(gra_sec) * self.scale) + 0.5
            cr.set_source(Preference.grid_color)
            cairo_paths(cr, (x, _ROW_H), (x, self.img_height - 1))
            cr.stroke()
            cr.set_source(Preference.component_color_running)
            cairo_draw_text(cr, layout, str(u_gra_sec.quantize(Decimal(".00"))), float(gra_sec) * self.scale, ruler_mid, 0.5, 0.5)
            cr.fill()
            u_gra_sec += u_gra_p_dec
            gra_sec += gra_p

    def _draw_waveforms(self, cr: cairo.Context, history, probes):
        cr.set_line_width(1.5)

        def _row_y(j, high):
            # each row spans _ROW_H px starting at _ROW_H offset; high at +10, low at +30
            base = _ROW_H + j * _ROW_H
            return (base + 10 + 0.5) if high else (base + 30 + 0.5)  # +0.5 aligns 1px stroke to pixel grid

        def _draw_segment(j, x0, x1, data, next_data=None):
            if data == -1:
                return  # open-circuit state: leave a gap, don't draw
            high = data is True or data == 1
            cr.set_source(Preference.highlevel_color if high else Preference.lowlevel_color)
            y = _row_y(j, high)
            cairo_paths(cr, (x0, y), (x1, y))
            cr.stroke()
            if next_data is not None and next_data != -1 and data != next_data:
                # vertical transition line between high and low
                cr.set_source(Preference.highlevel_color if high else Preference.lowlevel_color)
                tx = x1 - 0.5  # +0.5 aligns 1px stroke to pixel grid
                base = _ROW_H + j * _ROW_H
                cairo_paths(cr, (tx, base + 11), (tx, base + 29))
                cr.stroke()

        if len(history) > 1:
            for i, frame in enumerate(history[:-1]):
                t0, t1 = frame[0], history[i + 1][0]
                if t1 <= self.start_time or self.end_time < t0:
                    continue
                x0 = round((t0 - self.start_time) * self.scale)
                x1 = round((t1 - self.start_time) * self.scale) + 1
                for j, data in enumerate(frame[1:]):
                    _draw_segment(j, x0, x1, data, history[i + 1][j + 1])

            last = history[-1]
            if last[0] < self.end_time:
                x0 = round((last[0] - self.start_time) * self.scale)
                for j, data in enumerate(last[1:]):
                    _draw_segment(j, x0, self.diagram_width, data)
        else:
            last = history[0]
            x0 = round((last[0] - self.start_time) * self.scale)
            for j, data in enumerate(last[1:]):
                _draw_segment(j, x0, self.diagram_width, data)

    # ── time scrubbing ────────────────────────────────────────────────────────

    def update_current_time(self, x):
        if self.scale <= 0:
            return
        selected_time = max(self.start_time, min(x / self.scale + self.start_time, self.end_time))
        self._circuit.current_time = selected_time
        self._circuit.revert_state()
        self.chart_area.queue_draw()
        if self._parent_drawarea:
            self._parent_drawarea.queue_draw()

    def on_timing_diagram_click(self, gesture, n_press, x, y, *args):
        self.mouse_down = True
        self.update_current_time(x)

    def on_timing_diagram_release(self, gesture, n_press, x, y, *args):
        self.mouse_down = False
        self.chart_area.queue_draw()

    def on_timing_diagram_motion(self, controller, x, y, *args):
        self.cursor_x = x
        self.show_cursor = True
        if self.mouse_down:
            self.update_current_time(x)
        self.chart_area.queue_draw()

    def on_timing_diagram_leave(self, controller, *args):
        self.show_cursor = False
        self.chart_area.queue_draw()
