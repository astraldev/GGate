# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import cairo
import math
from decimal import Decimal
from ggate.const import definitions as const
from ggate.Utils import *
from ggate import Preference
from gi.repository import Gtk, Gdk, PangoCairo
from gettext import gettext as _

class TimingDiagramArea(Gtk.Box):
    def __init__(self, circuit, drawarea):
        Gtk.Box.__init__(self)

        self.circuit = circuit
        self.drawarea = drawarea
        self.scale = 5_000_000  # pix/sec
        self.start_time = 0.0
        self.end_time = 0.0002
        self.diagram_unit = 1  # 0: ns, 1: µs, 2: ms

        self.gra_pix = 120

        self.name_width = 150
        self.img_height = 0

        self.diagram_scroll = Gtk.ScrolledWindow()
        self.diagram_scroll.set_hexpand(True)
        self.diagram_scroll.set_vexpand(True)
        self.diagram_area = Gtk.DrawingArea()
        self.diagram_scroll.set_child(self.diagram_area)
        self.diagram_scroll_hadj = self.diagram_scroll.get_hadjustment()
        self.diagram_scroll_vadj = self.diagram_scroll.get_vadjustment()

        self.name_scroll = Gtk.ScrolledWindow(
            vadjustment=self.diagram_scroll.get_vadjustment())
        self.name_scroll.set_size_request(150, -1)
        self.namearea = Gtk.DrawingArea()
        self.name_scroll.set_child(self.namearea)
        self.name_scroll_hadj = self.name_scroll.get_hadjustment()
        self.name_scroll_vadj = self.name_scroll.get_vadjustment()

        self.append(self.name_scroll)
        self.append(self.diagram_scroll)

        self.cursor_x = 0
        self.cursor_y = 0
        self.show_cursor = False
        self.mouse_down = False
        self.middle_move_enabled = False

        self.name_pixbuf = None
        self.diagram_pixbuf = None

        self.namearea.set_draw_func(self.on_namearea_draw)
        self.diagram_area.set_draw_func(self.on_diagram_area_draw)

        controller = Gtk.EventControllerMotion()
        controller.connect('leave', self.on_diagram_area_leave)
        self.diagram_area.add_controller(controller)

        controller = Gtk.EventControllerMotion()
        controller.connect('motion', self.on_diagram_area_motion)
        self.diagram_area.add_controller(controller)

        self.diagram_area.set_draw_func(self.on_diagram_area_draw)

        controller = Gtk.GestureClick()
        # Primary Button
        controller.set_button(Gdk.BUTTON_PRIMARY)
        controller.connect('pressed', self.on_diagram_area_button_press_primary)
        self.diagram_area.add_controller(controller)

        controller = Gtk.GestureClick()
        # Secondary click (right click)
        controller.set_button(Gdk.BUTTON_SECONDARY)
        controller.connect('pressed', self.on_diagram_area_button_press_secondary)
        self.diagram_area.add_controller(controller)

        controller = Gtk.GestureClick()
        # Left click release
        controller.set_button(Gdk.BUTTON_PRIMARY)
        controller.connect('released', self.on_diagram_area_button_release_primary)
        self.diagram_area.add_controller(controller)

        controller = Gtk.GestureClick()
        # Right click release
        controller.set_button(Gdk.BUTTON_SECONDARY)
        controller.connect('released', self.on_diagram_area_button_release_secondary)
        self.diagram_area.add_controller(controller)

        controller = Gtk.GestureClick()
        controller.set_button(Gdk.BUTTON_SECONDARY)
        controller.connect('pressed', self.on_namearea_button_press)
        self.namearea.add_controller(controller)

        controller = Gtk.GestureClick()
        controller.set_button(Gdk.BUTTON_SECONDARY)
        controller.connect('released', self.on_namearea_button_release)
        self.namearea.add_controller(controller)

        controller = Gtk.EventControllerMotion()
        controller.connect('motion', self.on_namearea_motion)
        self.namearea.add_controller(controller)

    def on_namearea_button_press(self, widget, *event):
        self.middle_move_enabled = True
        self.move_start_x = event[1]
        self.move_start_y = event[2]

    def on_namearea_button_release(self, widget, *event):
        self.middle_move_enabled = False

    def on_namearea_motion(self, widget, *event):

        x_axis, y_axis = event[0], event[1]

        if self.middle_move_enabled:
            delta_x = self.move_start_x - x_axis
            delta_y = self.move_start_y - y_axis
            if -1 < delta_x < 1 and -1 < delta_y < 1:
                return
            self.name_scroll_hadj.set_value(
                self.name_scroll_hadj.get_value() + delta_x)
            self.name_scroll_vadj.set_value(
                self.name_scroll_vadj.get_value() + delta_y)

    def on_diagram_area_button_press_primary(self, widget, *event):
        event_button, x_axis, y_axis = event

        if event_button == Gdk.BUTTON_PRIMARY:
            self.cursor_x = x_axis

            if self.cursor_x < 0.0:
                self.cursor_x = 0.0
            if self.diagram_width < self.cursor_x:
                self.cursor_x = self.diagram_width
            self.cursor_y = y_axis
            if 39 <= self.cursor_y < self.img_height:
                self.mouse_down = True
                self.queue_draw()

    def on_diagram_area_button_press_secondary(self, controller, *events):
        event_button, x_axis, y_axis = events
        if event_button == Gdk.BUTTON_SECONDARY:
            self.middle_move_enabled = True
            self.move_start_x = x_axis
            self.move_start_y = y_axis

    def on_diagram_area_button_release_primary(self, widget, *event):
        if event[0] == Gdk.BUTTON_PRIMARY:
            self.mouse_down = False
            if 39 <= self.cursor_y < self.img_height:
                self.circuit.current_time = self.cursor_x / self.scale + self.start_time
                self.circuit.revert_state()
                self.drawarea.redraw = True
                self.drawarea.queue_draw()

    def on_diagram_area_button_release_secondary(self, controller, *event):
        self.middle_move_enabled = False

    def on_diagram_area_motion(self, controller, x_axis, y_axis, *args):
        widget = controller.get_widget()

        if self.middle_move_enabled:
            delta_x = self.move_start_x - x_axis
            delta_y = self.move_start_y - y_axis
            if -1 < delta_x < 1 and -1 < delta_y < 1:
                return
            self.diagram_scroll_hadj.set_value(
                self.diagram_scroll_hadj.get_value() + delta_x)
            self.diagram_scroll_vadj.set_value(
                self.diagram_scroll_vadj.get_value() + delta_y)

        self.cursor_x_old = self.cursor_x
        self.cursor_y_old = self.cursor_y
        self.cursor_x = x_axis
        try:
            self.diagram_width
        except:
            return
        if self.cursor_x < 0.0:
            self.cursor_x = 0.0
        if self.diagram_width < self.cursor_x:
            self.cursor_x = self.diagram_width
        self.cursor_y = y_axis
        if 39 <= self.cursor_y < self.img_height:
            int(min((self.cursor_x_old, self.cursor_x)) - 1)
            int(abs(self.cursor_x_old - self.cursor_x) + 4)
            if self.show_cursor:
                widget.queue_draw() # _area(left, 0, width, self.img_height)
            else:
                widget.queue_draw()
                self.show_cursor = True
        elif self.show_cursor:
            self.show_cursor = False
            widget.queue_draw()

    def set_time(self, time):
        old_x = (self.circuit.current_time - self.start_time) * self.scale
        self.circuit.current_time = time
        new_x = (self.circuit.current_time - self.start_time) * self.scale

        # TODO: Figure out what this is used for
        int(min((old_x, new_x)) - 1)
        int(abs(old_x - new_x) + 4)
        self.diagram_area.queue_draw()

    def on_diagram_area_leave(self, controller, *event):

        widget = controller.get_widget()

        self.show_cursor = False
        widget.queue_draw() #int(self.cursor_x - 1), 0, 3, self.img_height)

    def on_namearea_draw(self, widget, cr, *args):
        if self.name_pixbuf is not None:
            cr.set_source_surface(self.name_pixbuf, 0, 0)
            cr.paint()

    def on_diagram_area_draw(self, widget, cr, *args):
        if self.diagram_pixbuf is not None:
            cr.set_source_surface(self.diagram_pixbuf, 0, 0)
            cr.paint()
            cr.set_line_width(1.0)
            if self.show_cursor:
                if self.mouse_down:
                    cr.set_source_rgba(0.0, 1.0, 0.0, 0.8)
                else:
                    cr.set_source_rgba(0.0, 0.0, 1.0, 0.8)
                cairo_paths(cr, (self.cursor_x, 39),
                            (self.cursor_x, self.img_height))
                cr.stroke()
            if not self.mouse_down or not self.show_cursor:
                cr.set_source_rgba(1.0, 0.0, 0.0, 0.8)
                current_time_x = (self.circuit.current_time -
                                  self.start_time) * self.scale
                cairo_paths(cr, (current_time_x, 39),
                            (current_time_x, self.img_height))
                cr.stroke()

    def draw_names(self, cr):
        name_layout = PangoCairo.create_layout(cr)
        name_layout.set_font_description(Preference.drawing_font)
        # draw borders
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(1, 1, self.name_width-1, 38)
        cr.fill()
        cr.set_source_rgb(0.875, 0.875, 0.875)
        cr.rectangle(1, 40, self.name_width - 1, self.img_height - 41)
        cr.fill()
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(0.5, 0.5, self.name_width - 1, self.img_height - 1)
        i = 0
        for c in self.circuit.components:
            if c[0] == const.component_probe:
                cairo_paths(cr, (1, i * 40 + 39.5),
                            (self.name_width - 1, i * 40 + 39.5))
                i += 1
        cr.stroke()

        # draw probe names
        cr.set_source_rgb(0.0, 0.0, 0.0)
        i = 0
        for c in self.circuit.components:
            if c[0] == const.component_probe:
                cairo_draw_text(cr, name_layout,
                                c[1].values[0], 10, i * 40 + 60, 0, 0.5)
                i += 1
        cr.fill()

        if self.diagram_unit == 0:
            cairo_draw_text(cr, name_layout, "%s [ns]" % _(
                "Time"), 130, 35, 1.0, 1.0)
        elif self.diagram_unit == 1:
            cairo_draw_text(cr, name_layout, "%s [µs]" % _(
                "Time"), 130, 35, 1.0, 1.0)
        else:
            cairo_draw_text(cr, name_layout, "%s [ms]" % _(
                "Time"), 130, 35, 1.0, 1.0)

        cr.fill()

    def draw_diagrams(self, cr):
        diagram_layout = PangoCairo.create_layout(cr)
        diagram_layout.set_font_description(Preference.drawing_font)

        # draw borders
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 1, self.diagram_width - 1, self.img_height - 2)
        cr.fill()
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cairo_paths(cr, (0, 0.5), (self.diagram_width, 0.5))
        cairo_paths(cr, (self.diagram_width - 0.5, 1),
                    (self.diagram_width - 0.5, self.img_height - 1))
        cairo_paths(cr, (0, self.img_height - 0.5),
                    (self.diagram_width, self.img_height - 0.5))
        i = 0
        for c in self.circuit.components:
            if c[0] == const.component_probe:
                cairo_paths(cr, (0, i * 40 + 39.5),
                            (self.diagram_width - 1, i * 40 + 39.5))
                i += 1
        cr.stroke()

        # draw graduaton
        gra_p = Decimal(self.gra_pix) / Decimal(self.scale)
        order = 10 ** Decimal(int(math.log10(gra_p)))
        grasec_top = gra_p / order
        if 0.15 <= grasec_top < 0.35:
            gra_p = order * Decimal("0.2")
        elif 0.35 <= grasec_top <= 0.75:
            gra_p = order * Decimal("0.5")
        else:
            gra_p = order * Decimal("0.1")
        cr.set_source_rgb(0.0, 0.0, 0.0)

        if self.diagram_unit == 0:
            u_start_time = self.start_time * 1000000000
            u_end_time = self.end_time * 1000000000
            u_gra_p = gra_p * 1000000000
        elif self.diagram_unit == 1:
            u_start_time = self.start_time * 1000000
            u_end_time = self.end_time * 1000000
            u_gra_p = gra_p * 1000000
        else:
            u_start_time = self.start_time * 1000
            u_end_time = self.end_time * 1000
            u_gra_p = gra_p * 1000

        cairo_draw_text(cr, diagram_layout, str(
            Decimal(u_start_time).quantize(Decimal(".00"))), 5, 35, 0.0, 1.0)
        cairo_draw_text(cr, diagram_layout, str(Decimal(u_end_time).quantize(
            Decimal(".00"))), self.diagram_width - 5, 35, 1.0, 1.0)
        cr.fill()

        u_gra_sec = u_gra_p
        gra_sec = gra_p
        while True:
            if u_gra_sec + u_gra_p / 4 >= u_end_time:
                break
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cairo_paths(cr, (int(float(gra_sec) * self.scale) + 0.5, 39),
                        (int(float(gra_sec) * self.scale) + 0.5, self.img_height - 1))
            cr.stroke()
            cr.set_source_rgb(0.0, 0.0, 0.0)
            cairo_draw_text(cr, diagram_layout, str(Decimal(u_gra_sec).quantize(
                Decimal(".00"))), float(gra_sec) * self.scale, 35, 0.5, 1.0)
            u_gra_sec += u_gra_p
            gra_sec += gra_p
            cr.fill()

        # plot graphs
        history = self.circuit.probe_levels_history
        for i, probe_lebels in enumerate(history[:-1]):
            if history[i + 1][0] <= self.start_time or self.end_time < probe_lebels[0]:
                continue
            for j, data in enumerate(probe_lebels[1:]):
                if data is True:
                    cairo_paths(cr, (round((probe_lebels[0] - self.start_time) * self.scale), j * 40 + 55.5), (round(
                        (history[i + 1][0] - self.start_time) * self.scale) + 1, j * 40 + 55.5))
                else:
                    cairo_paths(cr, (round((probe_lebels[0] - self.start_time) * self.scale), j * 40 + 65.5), (round(
                        (history[i + 1][0] - self.start_time) * self.scale) + 1, j * 40 + 65.5))
                if data != history[i + 1][j + 1]:
                    cairo_paths(cr, (round((history[i + 1][0] - self.start_time) * self.scale) + 0.5, j * 40 + 56), (round(
                        (history[i + 1][0] - self.start_time) * self.scale) + 0.5, j * 40 + 65))

        if history[-1][0] < self.end_time:
            for j, data in enumerate(history[-1][1:]):
                if data is True:
                    cairo_paths(cr, (round(
                        (history[-1][0] - self.start_time) * self.scale), j * 40 + 55.5), (self.diagram_width, j * 40 + 55.5))
                else:
                    cairo_paths(cr, (round(
                        (history[-1][0] - self.start_time) * self.scale), j * 40 + 65.5), (self.diagram_width, j * 40 + 65.5))

        cr.stroke()

    def createDiagram(self):
        i = 0
        for c in self.circuit.components:
            if c[0] == const.component_probe:
                i += 1
        self.img_height = 40 * i + 40

        self.diagram_width = int(
            (self.end_time - self.start_time) * self.scale)
        if self.diagram_width == 0:
            self.diagram_width = 1

        self.name_pixbuf = cairo.ImageSurface(
            cairo.FORMAT_RGB24, self.name_width, self.img_height)
        self.namearea.set_size_request(self.name_width, self.img_height)
        ncr = cairo.Context(self.name_pixbuf)
        ncr.set_line_width(1.0)
        self.draw_names(ncr)

        self.diagram_pixbuf = cairo.ImageSurface(
            cairo.FORMAT_RGB24, self.diagram_width, self.img_height)
        self.diagram_area.set_size_request(self.diagram_width, self.img_height)
        ccr = cairo.Context(self.diagram_pixbuf)
        ccr.set_line_width(1.0)
        self.draw_diagrams(ccr)
        self.queue_draw()

        