# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import math
import copy
import cairo
from glogic import const
from glogic.Utils import *
from glogic.Components import comp_dict
from glogic import Preference
from gi.repository import Gtk, Gdk, GdkPixbuf, PangoCairo


class DrawArea(Gtk.ScrolledWindow):
    def __init__(self, parent):
        Gtk.ScrolledWindow.__init__(self)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.width = 1920
        self.height = 1080
        self.vadj = self.get_vadjustment()
        self.hadj = self.get_hadjustment()
        self.netstarted = False
        self.drawingarea = Gtk.DrawingArea()
        self.drawingarea.set_size_request(self.width, self.height)
        self.set_child(self.drawingarea)

        self.drawingarea.set_draw_func(self.on_draw)

        controller = Gtk.EventControllerMotion()
        controller.connect('leave', self.on_leave)
        self.drawingarea.add_controller(controller)

        controller = Gtk.EventControllerMotion()
        controller.connect('enter', self.on_enter)
        self.drawingarea.add_controller(controller)

        controller = Gtk.EventControllerMotion()
        controller.connect('motion', self.on_motion)
        self.drawingarea.add_controller(controller)

        controller = Gtk.GestureClick()
        controller.connect('pressed', self.on_button_press_primary)
        controller.set_button(Gdk.BUTTON_PRIMARY)
        self.drawingarea.add_controller(controller)

        controller = Gtk.GestureClick()
        controller.connect('pressed', self.on_button_press_middle)
        controller.set_button(Gdk.BUTTON_MIDDLE)
        self.drawingarea.add_controller(controller)

        controller = Gtk.GestureClick()
        controller.set_button(Gdk.BUTTON_SECONDARY)
        controller.connect('released', self.on_button_release_secondary)
        self.drawingarea.add_controller(controller)

        controller = Gtk.GestureClick()
        controller.set_button(Gdk.BUTTON_PRIMARY)
        controller.connect('released', self.on_button_release_primary)
        self.drawingarea.add_controller(controller)

        controller = Gtk.GestureClick()
        controller.set_button(Gdk.BUTTON_MIDDLE)
        controller.connect('released', self.on_button_release_middle)
        self.drawingarea.add_controller(controller)

        controller = Gtk.EventControllerKey()
        controller.connect('key-pressed', self.on_key_press)
        parent.add_controller(controller)

        controller = Gtk.EventControllerKey()
        controller.connect('key-released', self.on_key_release)
        parent.add_controller(controller)

        self.cursor_x = 0
        self.cursor_y = 0
        self.parent = parent
        self.added = False
        self.preadd = False
        self.drag_enabled = False
        self.preselected_component = None
        self.component_dragged = False
        self.cursor_over = False
        self.nearest_component = None
        self.rect_select_enabled = False
        self.middle_move_enabled = False
        self.mouse_down = False
        self.mbitmap = None
        self.circuit = None
        self.redraw = True
        self.netstarted = False
        self.mpixbuf = cairo.ImageSurface(
            cairo.FORMAT_RGB24, self.width, self.height)
        self._pasted_components = None
        self._pushed_component_name = const.component_none
        self._pushed_component = comp_dict[const.component_none]

    def queue_draw(self, *args):
        self.show()
        super().queue_draw(*args)
        self.drawingarea.show()
        self.drawingarea.queue_draw()

    def on_draw(self, widget, cr, width, height, *args):

        if self.redraw:

            mcr = cairo.Context(self.mpixbuf)
            if self.parent.running_mode:
                mcr.set_source(Preference.bg_color_running)
            else:
                mcr.set_source(Preference.bg_color)

            mcr.rectangle(0, 0, self.width, self.height)
            mcr.fill()

            mcr.translate(0.5, 0.5)
            matrix = mcr.get_matrix()
            mcr.set_line_width(1.0)
            layout = PangoCairo.create_layout(mcr)
            layout.set_font_description(Preference.drawing_font)

            if not self.parent.running_mode:
                # Draw grids
                mcr.set_source(Preference.grid_color)
                for x in range(0, self.width, 10):
                    cairo_paths(mcr, (x, 0), (x, self.height))
                for y in range(0, self.height, 10):
                    cairo_paths(mcr, (0, y), (self.width, y))
                mcr.stroke()

            # Draw component
            for c in self.circuit.components:
                if c[0] != const.component_net:
                    if not c in self.circuit.selected_components:
                        mcr.translate(c[1].pos_x, c[1].pos_y)
                        m = cairo.Matrix(
                            xx=c[1].matrix[0], xy=c[1].matrix[1], yx=c[1].matrix[2], yy=c[1].matrix[3])
                        mcr.set_matrix(m.multiply(mcr.get_matrix()))
                        if self.parent.running_mode:
                            mcr.set_source(Preference.component_color_running)
                            c[1].drawComponent(mcr, layout)
                        else:
                            mcr.set_source(Preference.component_color)
                            c[1].drawComponent(mcr, layout)
                            mcr.set_source(Preference.component_color)
                            c[1].drawComponentEditOverlap(mcr, layout)
                        mcr.set_matrix(matrix)

            if not self.parent.running_mode:
                # Draw net
                for c in self.circuit.components:
                    if c[0] == const.component_net:
                        if not c in self.circuit.selected_components:
                            mcr.set_source(Preference.net_color)
                            cairo_paths(mcr, (c[1], c[2]), (c[3], c[4]))
                            mcr.stroke()

                # Draw terminal of components
                mcr.set_source(Preference.terminal_color)
                for c in self.circuit.components:
                    if c[0] != const.component_net:
                        if not c in self.circuit.selected_components:
                            for p in c[1].rot_input_pins + c[1].rot_output_pins:
                                mcr.rectangle(c[1].pos_x+p[0]-1.5, c[1].pos_y+p[1]-1.5, 3, 3)
                mcr.fill()

                # Draw terminal of nets
                mcr.set_source(Preference.terminal_color)
                for c in self.circuit.components:
                    if c[0] == const.component_net:
                        if not c in self.circuit.selected_components:
                            mcr.rectangle(c[1]-1.5, c[2]-1.5, 3, 3)
                            mcr.rectangle(c[3]-1.5, c[4]-1.5, 3, 3)
                mcr.fill()

                # Draw selected components
                if not self.component_dragged:
                    mcr.set_source(Preference.selected_color)
                    for c in self.circuit.selected_components:
                        if c[0] == const.component_net:
                            cairo_paths(mcr, (c[1], c[2]), (c[3], c[4]))
                    mcr.stroke()

                    for c in self.circuit.selected_components:
                        if c[0] != const.component_net:
                            mcr.translate(c[1].pos_x, c[1].pos_y)
                            m = cairo.Matrix(
                                xx=c[1].matrix[0], xy=c[1].matrix[1], yx=c[1].matrix[2], yy=c[1].matrix[3])
                            mcr.set_matrix(m.multiply(mcr.get_matrix()))
                            c[1].drawComponent(mcr, layout)
                            c[1].drawComponentEditOverlap(mcr, layout)
                            mcr.set_matrix(matrix)

                    for c in self.circuit.selected_components:
                        if c[0] != const.component_net:
                            for p in c[1].rot_input_pins + c[1].rot_output_pins:
                                mcr.rectangle(
                                    c[1].pos_x+p[0]-1.5, c[1].pos_y+p[1]-1.5, 3, 3)

                    for c in self.circuit.selected_components:
                        if c[0] == const.component_net:
                            mcr.rectangle(c[1]-1.5, c[2]-1.5, 3, 3)
                            mcr.rectangle(c[3]-1.5, c[4]-1.5, 3, 3)

                    mcr.fill()

            self.redraw = False

        cr.set_source_surface(self.mpixbuf, 0, 0)
        cr.paint()

        cr.translate(0.5, 0.5)
        matrix = cr.get_matrix()
        cr.set_line_width(1.0)
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(Preference.drawing_font)

        if self.rect_select_enabled:
            cr.set_source_rgba(1, 0.75, 0, 0.25)
            cr.rectangle(self.select_start_x-0.5, self.select_start_y-0.5, self.cursor_smooth_x -
                         self.select_start_x, self.cursor_smooth_y - self.select_start_y)
            cr.fill()
            cr.set_source_rgb(1, 0.75, 0)
            cr.set_line_width(1.0)
            cr.rectangle(self.select_start_x-0.5, self.select_start_y-0.5, self.cursor_smooth_x -
                         self.select_start_x, self.cursor_smooth_y - self.select_start_y)
            cr.stroke()
            cr.set_line_width(1.0)

        if not self.parent.running_mode and not self.added and self.cursor_over and (self._pushed_component_name != const.component_none or self._pasted_components):
            if self._pushed_component_name == const.component_net:
                # Draw cursor
                cr.set_source(Preference.cursor_color)
                cr.arc(self.cursor_x, self.cursor_y, 3, 0, 2 * math.pi)
                cr.stroke()

                if self.netstarted:
                    # Draw net
                    cr.set_source(Preference.net_color)
                    if self.net_right and self.netstart_x < self.cursor_x or self.net_left and self.cursor_x < self.netstart_x:
                        cairo_paths(cr, (self.netstart_x, self.netstart_y),
                                    (self.cursor_x, self.netstart_y))
                        if self.netstart_y != self.cursor_y:
                            cairo_paths(
                                cr, (self.cursor_x, self.netstart_y), (self.cursor_x, self.cursor_y))
                        cr.stroke()

                        cr.set_source(Preference.terminal_color)
                        cr.rectangle(self.cursor_x-1.5,
                                     self.netstart_y-1.5, 3, 3)
                        cr.fill()

                    else:
                        if self.netstart_y != self.cursor_y:
                            cairo_paths(
                                cr, (self.netstart_x, self.netstart_y), (self.netstart_x, self.cursor_y))
                        if self.netstart_x != self.cursor_x:
                            cairo_paths(
                                cr, (self.netstart_x, self.cursor_y), (self.cursor_x, self.cursor_y))
                        cr.stroke()

                        cr.set_source(Preference.terminal_color)
                        cr.rectangle(self.netstart_x-1.5,
                                     self.cursor_y-1.5, 3, 3)
                        cr.fill()

                    cr.rectangle(self.netstart_x-1.5,
                                 self.netstart_y-1.5, 3, 3)
                    cr.fill()

            elif self._pasted_components:
                # Draw pasted component
                if self.preadd:
                    cr.set_source(Preference.preadd_color)
                else:
                    cr.set_source(Preference.picked_color)

                for c in self._pasted_components:
                    cr.translate(self.cursor_x - self._paste_center_x,
                                 self.cursor_y - self._paste_center_y)
                    if c[0] != const.component_net:
                        cr.translate(c[1].pos_x, c[1].pos_y)
                        m = cairo.Matrix(
                            xx=c[1].matrix[0], xy=c[1].matrix[1], yx=c[1].matrix[2], yy=c[1].matrix[3])
                        cr.set_matrix(m.multiply(cr.get_matrix()))
                        c[1].drawComponent(cr, layout)
                        c[1].drawComponentEditOverlap(cr, layout)
                    else:
                        cairo_paths(cr, (c[1], c[2]), (c[3], c[4]))
                        cr.stroke()
                        cr.rectangle(c[1]-1.5, c[2]-1.5, 3, 3)
                        cr.rectangle(c[3]-1.5, c[4]-1.5, 3, 3)
                        cr.fill()
                    cr.set_matrix(matrix)

            else:
                # Draw picked component
                if self.preadd:
                    cr.set_source(Preference.preadd_color)
                else:
                    cr.set_source(Preference.picked_color)

                logicand = self._pushed_component

                cr.translate(self.cursor_x, self.cursor_y)
                m = cairo.Matrix(
                    xx=logicand.matrix[0], xy=logicand.matrix[1], yx=logicand.matrix[2], yy=logicand.matrix[3])
                cr.set_matrix(m.multiply(cr.get_matrix()))
                logicand.drawComponent(cr, layout)
                logicand.drawComponentEditOverlap(cr, layout)
                cr.set_matrix(matrix)

        if self.parent.running_mode:
            # Draw net of components
            cr.set_source(Preference.component_color_running)
            for c in self.circuit.components:
                if c[0] != const.component_net:
                    if not c in self.circuit.selected_components:
                        cr.translate(c[1].pos_x, c[1].pos_y)
                        m = cairo.Matrix(
                            xx=c[1].matrix[0], xy=c[1].matrix[1], yx=c[1].matrix[2], yy=c[1].matrix[3])
                        cr.set_matrix(m.multiply(cr.get_matrix()))
                        cr.set_source(Preference.component_color_running)
                        c[1].drawComponentRunOverlap(cr, layout)
                        cr.set_matrix(matrix)

            # Draw net
            for c in self.circuit.components:
                if c[0] == const.component_net:
                    if not c in self.circuit.selected_components:
                        for i, net in enumerate(self.circuit.net_connections):
                            if (c[1], c[2]) in net:
                                if self.circuit.net_levels[i] == 1:
                                    cr.set_source(Preference.highlevel_color)
                                elif self.circuit.net_levels[i] == 0:
                                    cr.set_source(Preference.lowlevel_color)
                                else:
                                    cr.set_source(Preference.net_color_running)

                        cairo_paths(cr, (c[1], c[2]), (c[3], c[4]))
                        cr.stroke()

            # Draw terminal of nets
            cr.set_source(Preference.terminal_color_running)
            for c in self.circuit.components:
                if c[0] == const.component_net:
                    if not c in self.circuit.selected_components:
                        if not (c[1], c[2]) in self.circuit.net_no_dot:
                            cr.rectangle(c[1]-1.5, c[2]-1.5, 3, 3)
                        elif not (c[3], c[4]) in self.circuit.net_no_dot:
                            cr.rectangle(c[3]-1.5, c[4]-1.5, 3, 3)
            cr.fill()

        else:
            # Draw selected components
            if self.component_dragged:
                cr.set_source(Preference.selected_color)
                for c in self.circuit.selected_components:
                    if c[0] == const.component_net:
                        cairo_paths(cr, (c[1], c[2]), (c[3], c[4]))
                        cr.stroke()

                for c in self.circuit.selected_components:
                    if c[0] != const.component_net:
                        cr.translate(c[1].pos_x, c[1].pos_y)
                        m = cairo.Matrix(
                            xx=c[1].matrix[0], xy=c[1].matrix[1], yx=c[1].matrix[2], yy=c[1].matrix[3])
                        cr.set_matrix(m.multiply(cr.get_matrix()))
                        c[1].drawComponent(cr, layout)
                        c[1].drawComponentEditOverlap(cr, layout)
                        cr.set_matrix(matrix)

                for c in self.circuit.selected_components:
                    if c[0] != const.component_net:
                        for p in c[1].rot_input_pins + c[1].rot_output_pins:
                            cr.rectangle(c[1].pos_x+p[0]-1.5,
                                         c[1].pos_y+p[1]-1.5, 3, 3)

                for c in self.circuit.selected_components:
                    if c[0] == const.component_net:
                        cr.rectangle(c[1]-1.5, c[2]-1.5, 3, 3)
                        cr.rectangle(c[3]-1.5, c[4]-1.5, 3, 3)

                cr.fill()

        # Highlight component
        if self.nearest_component is not None and self._pushed_component_name == const.component_none:
            if not self.nearest_component in self.circuit.selected_components and self.cursor_over and not self.parent.running_mode:
                c = self.nearest_component
                if c[0] == const.component_net:
                    cr.set_source(Preference.net_high_color)
                    cairo_paths(cr, (c[1], c[2]), (c[3], c[4]))
                    cr.stroke()
                else:
                    cr.set_source(Preference.component_high_color)
                    cr.translate(c[1].pos_x, c[1].pos_y)
                    m = cairo.Matrix(
                        xx=c[1].matrix[0], xy=c[1].matrix[1], yx=c[1].matrix[2], yy=c[1].matrix[3])
                    cr.set_matrix(m.multiply(cr.get_matrix()))
                    c[1].drawComponent(cr, layout)
                    c[1].drawComponentEditOverlap(cr, layout)
                    cr.set_matrix(matrix)

        self.added = False

    def on_leave(self, *args):
        self.cursor_over = False
        if not self.parent.running_mode:
            self.queue_draw()

    def on_enter(self, *args):
        self.cursor_over = True
        if not self.parent.running_mode:
            self.queue_draw()

    def set_cursor_to_nearest_terminal(self, min_dist):
        for c in self.circuit.components:
            if c[0] == const.component_net:
                if min_dist > (self.cursor_smooth_x - c[1]) ** 2 + (self.cursor_smooth_y - c[2]) ** 2:
                    min_dist = (self.cursor_smooth_x -
                                c[1]) ** 2 + (self.cursor_smooth_y - c[2]) ** 2
                    self.cursor_x = c[1]
                    self.cursor_y = c[2]
                if min_dist > (self.cursor_smooth_x - c[3]) ** 2 + (self.cursor_smooth_y - c[4]) ** 2:
                    min_dist = (self.cursor_smooth_x -
                                c[3]) ** 2 + (self.cursor_smooth_y - c[4]) ** 2
                    self.cursor_x = c[3]
                    self.cursor_y = c[4]
                if c[1] == c[3]:
                    if c[2] < self.cursor_smooth_y < c[4] or c[4] < self.cursor_smooth_y < c[2]:
                        if min_dist > (self.cursor_smooth_x - c[1]) ** 2:
                            min_dist = (self.cursor_smooth_x - c[1]) ** 2
                            self.cursor_x = c[1] - c[1] % 10
                            self.cursor_y = int(
                                self.cursor_smooth_y - self.cursor_smooth_y % 10)
                if c[2] == c[4]:
                    if c[1] < self.cursor_smooth_x < c[3] or c[3] < self.cursor_smooth_x < c[1]:
                        if min_dist > (self.cursor_smooth_y - c[2]) ** 2:
                            min_dist = (self.cursor_smooth_y - c[2]) ** 2
                            self.cursor_x = int(
                                self.cursor_smooth_x - self.cursor_smooth_x % 10)
                            self.cursor_y = c[2] - c[2] % 10

            else:
                for p in c[1].rot_input_pins + c[1].rot_output_pins:

                    if min_dist > (self.cursor_smooth_x - c[1].pos_x - p[0]) ** 2 + (self.cursor_smooth_y - c[1].pos_y - p[1]) ** 2:
                        min_dist = (self.cursor_smooth_x - c[1].pos_x - p[0]) ** 2 + (
                            self.cursor_smooth_y - c[1].pos_y - p[1]) ** 2
                        self.cursor_x = c[1].pos_x + p[0]
                        self.cursor_y = c[1].pos_y + p[1]

        return min_dist

    def on_key_release(self, widget, key_val, *args):
        if self.parent.running_mode:
            return
        if self.cursor_over:
            
            if key_val == Gdk.KEY_Delete:
                self.parent.on_action_delete_pressed()

            if self._pushed_component_name == const.component_net:
                if key_val == Gdk.KEY_Control_L or key_val == Gdk.KEY_Control_R:
                    oldcursor_x = self.cursor_x
                    oldcursor_y = self.cursor_y

                    # snap cursor to terminals
                    min_dist = self.set_cursor_to_nearest_terminal(225)

                    if min_dist == 225:
                        self.cursor_x = int(
                            self.cursor_smooth_x - self.cursor_smooth_x % 10)
                        self.cursor_y = int(
                            self.cursor_smooth_y - self.cursor_smooth_y % 10)
                    if oldcursor_x != self.cursor_x or oldcursor_y != self.cursor_y:
                        self.queue_draw()

    def on_key_press(self, *args):
        if self.parent.running_mode:
            return
        if self.cursor_over:
            if self._pushed_component_name != const.component_none:
                if args[1] == Gdk.KEY_Control_L or args[1] == Gdk.KEY_Control_R:
                    oldcursor_x = self.cursor_x
                    oldcursor_y = self.cursor_y

                    self.cursor_x = int(
                        self.cursor_smooth_x - self.cursor_smooth_x % 10)
                    self.cursor_y = int(
                        self.cursor_smooth_y - self.cursor_smooth_y % 10)

                    if oldcursor_x != self.cursor_x or oldcursor_y != self.cursor_y:
                        self.queue_draw()

    def on_motion(self,  *args):

        x_axis, y_axis = args[1], args[2]

        self.cursor_smooth_x = x_axis
        self.cursor_smooth_y = y_axis

        if self.middle_move_enabled:
            delta_x = self.move_start_x - x_axis
            delta_y = self.move_start_y - y_axis
            if -1 < delta_x < 1 and -1 < delta_y < 1:
                return
            self.hadj.set_value(self.hadj.get_value() + delta_x)
            self.vadj.set_value(self.vadj.get_value() + delta_y)

        if self.parent.running_mode:
            return

        oldcursor_x = self.cursor_x
        oldcursor_y = self.cursor_y

        self.cursor_smooth_x = max(
            (0, min((self.width, self.cursor_smooth_x))))
        self.cursor_smooth_y = max(
            (0, min((self.height, self.cursor_smooth_y))))

        if self._pushed_component_name == const.component_net:
            # snap cursor to terminals
            min_dist = 225
            if Gdk.ModifierType.CONTROL_MASK:
                min_dist = self.set_cursor_to_nearest_terminal(min_dist)

            if min_dist == 225:
                self.cursor_x = int(self.cursor_smooth_x -
                                    self.cursor_smooth_x % 10)
                self.cursor_y = int(self.cursor_smooth_y -
                                    self.cursor_smooth_y % 10)
            if oldcursor_x != self.cursor_x or oldcursor_y != self.cursor_y:
                self.queue_draw()

        else:
            self.cursor_x = int(self.cursor_smooth_x -
                                self.cursor_smooth_x % 10)
            self.cursor_y = int(self.cursor_smooth_y -
                                self.cursor_smooth_y % 10)
            if self._pushed_component_name != const.component_none or self._pasted_components:
                if oldcursor_x != self.cursor_x or oldcursor_y != self.cursor_y:
                    self.queue_draw()

            if self.mouse_down and self.drag_enabled:
                # Move components
                ddx = self.cursor_smooth_x - self.select_start_x
                ddy = self.cursor_smooth_y - self.select_start_y
                old_delta_x = self.drag_delta_x
                old_delta_y = self.drag_delta_y
                if ddx >= 0:
                    self.drag_delta_x = ddx - ddx % 10
                else:
                    self.drag_delta_x = ddx + (-ddx % 10)
                if ddy >= 0:
                    self.drag_delta_y = ddy - ddy % 10
                else:
                    self.drag_delta_y = ddy + (-ddy % 10)
                if old_delta_x != self.drag_delta_x or old_delta_y != self.drag_delta_y:

                    fix_delta_x = 0
                    fix_delta_y = 0

                    self.comps_rect[0] += self.drag_delta_x - old_delta_x
                    self.comps_rect[1] += self.drag_delta_y - old_delta_y
                    self.comps_rect[2] += self.drag_delta_x - old_delta_x
                    self.comps_rect[3] += self.drag_delta_y - old_delta_y

                    if self.comps_rect[0] < 0:
                        fix_delta_x = -self.comps_rect[0]
                    if self.comps_rect[1] < 0:
                        fix_delta_y = -self.comps_rect[1]
                    if fix_delta_x == 0:
                        if self.comps_rect[2] > self.width:
                            fix_delta_x = self.width - self.comps_rect[2]
                    if fix_delta_y == 0:
                        if self.comps_rect[3] > self.height:
                            fix_delta_y = self.height - self.comps_rect[3]

                    for c in self.circuit.selected_components:
                        if c[0] == const.component_net:
                            c[1] += self.drag_delta_x - old_delta_x
                            c[2] += self.drag_delta_y - old_delta_y
                            c[3] += self.drag_delta_x - old_delta_x
                            c[4] += self.drag_delta_y - old_delta_y
                        else:
                            c[1].pos_x += self.drag_delta_x - old_delta_x
                            c[1].pos_y += self.drag_delta_y - old_delta_y
                            if old_delta_x == 0 and old_delta_y == 0:
                                for p in c[1].rot_input_pins + c[1].rot_output_pins:
                                    self.circuit.connect_nets(c[1].pos_x - (self.drag_delta_x - old_delta_x) + p[0], c[1].pos_y - (
                                        self.drag_delta_y - old_delta_y) + p[1], lock_selected=True)

                    if fix_delta_x != 0 or fix_delta_y != 0:
                        self.comps_rect[0] += fix_delta_x
                        self.comps_rect[1] += fix_delta_y
                        self.comps_rect[2] += fix_delta_x
                        self.comps_rect[3] += fix_delta_y
                        for c in self.circuit.selected_components:
                            if c[0] == const.component_net:
                                c[1] += fix_delta_x
                                c[2] += fix_delta_y
                                c[3] += fix_delta_x
                                c[4] += fix_delta_y
                            else:
                                c[1].pos_x += fix_delta_x
                                c[1].pos_y += fix_delta_y

                    for c in self.circuit.selected_components:
                        if c[0] == const.component_net:
                            if old_delta_x == 0 and old_delta_y == 0:
                                self.circuit.connect_nets(c[1] - (self.drag_delta_x - old_delta_x), c[2] - (
                                    self.drag_delta_y - old_delta_y), lock_selected=True)
                                self.circuit.connect_nets(c[3] - (self.drag_delta_x - old_delta_x), c[4] - (
                                    self.drag_delta_y - old_delta_y), lock_selected=True)

                    if not self.component_dragged:
                        self.redraw = True

                    self.component_dragged = True
                    self.queue_draw()

            else:
                if self.rect_select_enabled:
                    self.queue_draw()
                else:
                    # Highlight component
                    old_nearest_component = self.nearest_component
                    self.nearest_component = None
                    for c in self.circuit.components:
                        if c[0] == const.component_net:
                            if (c[1] - 3 <= self.cursor_smooth_x <= c[3] + 3 or c[3] - 3 <= self.cursor_smooth_x <= c[1] + 3) and (c[2] - 3 <= self.cursor_smooth_y <= c[4] + 3 or c[4] - 3 <= self.cursor_smooth_y <= c[2] + 3):
                                if ((c[4] - c[2]) * (self.cursor_smooth_x - c[1]) + (c[3] - c[1]) * (self.cursor_smooth_y - c[2])) ** 2 / ((c[3] - c[1]) ** 2 + (c[4] - c[2]) ** 2) <= 9:
                                    self.nearest_component = c
                                    break
                        else:
                            im = inv_matrix(c[1].matrix)
                            if c[1].isMouseOvered(im[0] * (self.cursor_smooth_x - c[1].pos_x) + im[1] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_x,
                                                  im[2] * (self.cursor_smooth_x - c[1].pos_x) + im[3] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_y):
                                self.nearest_component = c
                                break

                    if old_nearest_component is not self.nearest_component:
                        self.queue_draw()

    def on_button_press_primary(self, *args):

        state = args[0].get_current_event_state()
        self.cursor_smooth_x = args[2]
        self.cursor_smooth_y = args[3]

        if args[1] == Gdk.BUTTON_PRIMARY:

            if not self.parent.running_mode:
                if self._pushed_component_name == const.component_none and not self._pasted_components:
                    # Check selected area
                    self.rect_select_enabled = True
                    for c in self.circuit.components:
                        if c[0] == const.component_net:
                            if (c[1] - 3 <= self.cursor_smooth_x <= c[3] + 3 or c[3] - 3 <= self.cursor_smooth_x <= c[1] + 3) and (c[2] - 3 <= self.cursor_smooth_y <= c[4] + 3 or c[4] - 3 <= self.cursor_smooth_y <= c[2] + 3):
                                if ((c[4] - c[2]) * (self.cursor_smooth_x - c[1]) + (c[3] - c[1]) * (self.cursor_smooth_y - c[2])) ** 2 / ((c[3] - c[1]) ** 2 + (c[4] - c[2]) ** 2) <= 9:
                                    if c in self.circuit.selected_components:
                                        self.drag_delta_x = 0
                                        self.drag_delta_y = 0
                                        self.drag_enabled = True

                                    self.preselected_component = c
                                    self.rect_select_enabled = False
                                    break
                        else:
                            im = inv_matrix(c[1].matrix)
                            if c[1].isMouseOvered(im[0] * (self.cursor_smooth_x - c[1].pos_x) + im[1] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_x,
                                                  im[2] * (self.cursor_smooth_x - c[1].pos_x) + im[3] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_y):
                                if c in self.circuit.selected_components:
                                    self.drag_delta_x = 0
                                    self.drag_delta_y = 0
                                    self.drag_enabled = True

                                self.preselected_component = c
                                self.rect_select_enabled = False
                                break

                    self.select_start_x = self.cursor_smooth_x
                    self.select_start_y = self.cursor_smooth_y

                    if self.drag_enabled:
                        self.comps_rect = get_components_rect(
                            self.circuit.selected_components)

                else:
                    self.preadd = True

                self.queue_draw()

            else:
                for c in self.circuit.components:
                    if c[0] != const.component_net:
                        im = inv_matrix(c[1].matrix)
                        c[1].mouse_down(im[0] * (self.cursor_smooth_x - c[1].pos_x) + im[1] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_x,
                                        im[2] * (self.cursor_smooth_x - c[1].pos_x) + im[3] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_y)

            self.mouse_down = True

    def on_button_press_middle(self, *args):
        if args[2] == Gdk.BUTTON_MIDDLE:
            self.middle_move_enabled = True
            self.move_start_x = self.cursor_smooth_x
            self.move_start_y = self.cursor_smooth_y

    def refresh_nets(self):
        tmp_components = self.circuit.components[:]
        for c in tmp_components:
            if c[0] == const.component_net:
                self.circuit.split_nets(c[1], c[2])
                self.circuit.split_nets(c[3], c[4])
            else:
                for p in c[1].rot_input_pins + c[1].rot_output_pins:
                    self.circuit.split_nets(
                        c[1].pos_x + p[0], c[1].pos_y + p[1])

        tmp_components = self.circuit.components[:]
        for c in tmp_components:
            if c[0] == const.component_net:
                self.circuit.connect_nets(c[1], c[2])
                self.circuit.connect_nets(c[3], c[4])

    # Left Click
    def on_button_release_primary(self, *args):
        state = args[0].get_current_event_state()
        if args[1] == Gdk.BUTTON_PRIMARY:  # Left button released

            if not self.parent.running_mode:
                self.drag_enabled = False
                if self.component_dragged:
                    self.component_dragged = False
                    tmp_components = self.circuit.components[:]
                    for c in tmp_components:
                        if c[0] == const.component_net:
                            self.circuit.split_nets(c[1], c[2])
                            self.circuit.split_nets(c[3], c[4])
                        else:
                            for p in c[1].rot_input_pins + c[1].rot_output_pins:
                                self.circuit.split_nets(
                                    c[1].pos_x + p[0], c[1].pos_y + p[1])

                    tmp_components = self.circuit.components[:]
                    for c in tmp_components:
                        if c[0] == const.component_net:
                            self.circuit.connect_nets(c[1], c[2])
                            self.circuit.connect_nets(c[3], c[4])

                    self.preselected_component = None
                    self.circuit.push_history()
                    # self.parent.action_undo.set_sensitive(True)
                    # self.parent.action_redo.set_sensitive(False)
                    self.redraw = True

                elif self._pushed_component_name == const.component_none and not self._pasted_components:
                    # Select component
                    selected = False
                    if self.preselected_component is not None:
                        c = self.preselected_component
                        if c[0] == const.component_net:
                            if (c[1] - 3 <= self.cursor_smooth_x <= c[3] + 3 or c[3] - 3 <= self.cursor_smooth_x <= c[1] + 3) and (c[2] - 3 <= self.cursor_smooth_y <= c[4] + 3 or c[4] - 3 <= self.cursor_smooth_y <= c[2] + 3):
                                if ((c[4] - c[2]) * (self.cursor_smooth_x - c[1]) + (c[3] - c[1]) * (self.cursor_smooth_y - c[2])) ** 2 / ((c[3] - c[1]) ** 2 + (c[4] - c[2]) ** 2) <= 9:
                                    if state & Gdk.ModifierType.CONTROL_MASK:
                                        if not c in self.circuit.selected_components:
                                            self.circuit.selected_components.append(
                                                c)
                                        else:
                                            self.circuit.selected_components.remove(
                                                c)
                                    else:
                                        self.circuit.selected_components = [c]
                                    selected = True

                        else:
                            im = inv_matrix(c[1].matrix)
                            if c[1].isMouseOvered(im[0] * (self.cursor_smooth_x - c[1].pos_x) + im[1] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_x,
                                                  im[2] * (self.cursor_smooth_x - c[1].pos_x) + im[3] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_y):
                                if state & Gdk.ModifierType.CONTROL_MASK:
                                    if not c in self.circuit.selected_components:
                                        self.circuit.selected_components.append(
                                            c)
                                    else:
                                        self.circuit.selected_components.remove(
                                            c)
                                else:
                                    self.circuit.selected_components = [c]
                                selected = True

                        self.preselected_component = None

                    elif self.rect_select_enabled:
                        self.rect_select_enabled = False
                        rectselected_components = []
                        if self.select_start_x < self.cursor_smooth_x:
                            rect_left = self.select_start_x
                            rect_right = self.cursor_smooth_x
                        else:
                            rect_left = self.cursor_smooth_x
                            rect_right = self.select_start_x
                        if self.select_start_y < self.cursor_smooth_y:
                            rect_top = self.select_start_y
                            rect_bottom = self.cursor_smooth_y
                        else:
                            rect_top = self.cursor_smooth_y
                            rect_bottom = self.select_start_y

                        for c in self.circuit.components:
                            if c[0] == const.component_net:
                                if rect_left <= c[1] <= rect_right and rect_left <= c[3] <= rect_right and rect_top <= c[2] <= rect_bottom and rect_top <= c[4] <= rect_bottom:
                                    rectselected_components.append(c)
                                    selected = True
                            elif rect_left <= c[1].pos_x + c[1].rot_comp_rect[0] + 3 and rect_top <= c[1].pos_y + c[1].rot_comp_rect[1] + 3 and c[1].pos_x + c[1].rot_comp_rect[2] - 3 <= rect_right and c[1].pos_y + c[1].rot_comp_rect[3] - 3 <= rect_bottom:
                                rectselected_components.append(c)
                                selected = True

                        if state & Gdk.ModifierType.CONTROL_MASK:
                            for c in rectselected_components:
                                if not c in self.circuit.selected_components:
                                    self.circuit.selected_components.append(c)

                        else:
                            self.circuit.selected_components = rectselected_components

                    if not selected and not state & Gdk.ModifierType.CONTROL_MASK:
                        self.circuit.selected_components = []
                        
                    self.set_selected_component_to_prop_window()
                    
                    if len(self.circuit.selected_components) == 0:
                        self.parent.disable_edit_actions()
                        
                    else:
                        self.parent.action_rotleft.set_sensitive(True)
                        self.parent.action_rotright.set_sensitive(True)
                        self.parent.action_fliphori.set_sensitive(True)
                        self.parent.action_flipvert.set_sensitive(True)

                    self.redraw = True

                elif self._pushed_component_name == const.component_net:
                    if self.netstarted:
                        # Add net
                        if self.net_right and self.netstart_x < self.cursor_x or self.net_left and self.cursor_x < self.netstart_x:
                            component_data = [
                                const.component_net, self.netstart_x, self.netstart_y, self.cursor_x, self.netstart_y]
                            component_data2 = [
                                const.component_net, self.cursor_x, self.netstart_y, self.netstart_x, self.netstart_y]
                            if not component_data in self.circuit.components and not component_data2 in self.circuit.components:
                                self.circuit.components.append(component_data)

                            if self.netstart_y != self.cursor_y:
                                component_data = [
                                    const.component_net, self.cursor_x, self.netstart_y, self.cursor_x, self.cursor_y]
                                component_data2 = [
                                    const.component_net, self.cursor_x, self.cursor_y, self.cursor_x, self.netstart_y]
                                if not component_data in self.circuit.components and not component_data2 in self.circuit.components:
                                    self.circuit.components.append(
                                        component_data)

                        else:
                            if self.netstart_y != self.cursor_y:
                                component_data = [
                                    const.component_net, self.netstart_x, self.netstart_y, self.netstart_x, self.cursor_y]
                                component_data2 = [
                                    const.component_net, self.netstart_x, self.cursor_y, self.netstart_x, self.netstart_y]
                                if not component_data in self.circuit.components and not component_data2 in self.circuit.components:
                                    self.circuit.components.append(
                                        component_data)

                            if self.netstart_x != self.cursor_x:
                                component_data = [
                                    const.component_net, self.netstart_x, self.cursor_y, self.cursor_x, self.cursor_y]
                                component_data2 = [
                                    const.component_net, self.cursor_x, self.cursor_y, self.netstart_x, self.cursor_y]
                                if not component_data in self.circuit.components and not component_data2 in self.circuit.components:
                                    self.circuit.components.append(
                                        component_data)

                        self.refresh_nets()

                        self.circuit.push_history()

                        # self.parent.action_undo.set_sensitive(True)
                        # self.parent.action_redo.set_sensitive(False)

                    # Begin to create net
                    self.netstart_x = self.cursor_x
                    self.netstart_y = self.cursor_y
                    self.netstarted = True
                    self.net_left = True
                    self.net_right = True
                    for c in self.circuit.components:
                        if c[0] == const.component_net:
                            if c[2] == c[4] == self.netstart_y:
                                if c[1] <= self.netstart_x <= c[3]:
                                    if c[1] != self.netstart_x:
                                        self.net_left = False
                                    if c[3] != self.netstart_x:
                                        self.net_right = False
                                elif c[3] <= self.netstart_x <= c[1]:
                                    if c[3] != self.netstart_x:
                                        self.net_left = False
                                    if c[1] != self.netstart_x:
                                        self.net_right = False

                            if self.net_left == self.net_right == False:
                                break

                        else:
                            pins = c[1].rot_input_pins + c[1].rot_output_pins
                            dirs = c[1].rot_input_pins_dir + \
                                c[1].rot_output_pins_dir

                            for i, p in enumerate(pins):
                                if c[1].pos_x + p[0] == self.netstart_x and c[1].pos_y + p[1] == self.netstart_y:
                                    if dirs[i] == const.direction_E:
                                        self.net_right = False
                                        break
                                    elif dirs[i] == const.direction_W:
                                        self.net_left = False
                                        break

                            if self.net_left == self.net_right == False:
                                break

                    self.redraw = True

                else:
                    # Add component
                    if self._pasted_components:
                        left = self._pasted_rect[0] + \
                            self.cursor_x - self._paste_center_x
                        top = self._pasted_rect[1] + \
                            self.cursor_y - self._paste_center_y
                        right = self._pasted_rect[2] + \
                            self.cursor_x - self._paste_center_x
                        bottom = self._pasted_rect[3] + \
                            self.cursor_y - self._paste_center_y
                        if left >= 0 and top >= 0 and right <= 1980 and bottom <= 1080:
                            for cadd in self._pasted_components:
                                if cadd[0] == const.component_net:
                                    cadd[1] += self.cursor_x - \
                                        self._paste_center_x
                                    cadd[2] += self.cursor_y - \
                                        self._paste_center_y
                                    cadd[3] += self.cursor_x - \
                                        self._paste_center_x
                                    cadd[4] += self.cursor_y - \
                                        self._paste_center_y

                                else:
                                    comp_x = self.cursor_x - \
                                        self._paste_center_x + cadd[1].pos_x
                                    comp_y = self.cursor_y - \
                                        self._paste_center_y + cadd[1].pos_y
                                    exist = False
                                    for c in self.circuit.components:
                                        if c[0] == cadd[0]:
                                            if c[1].pos_x == comp_x and c[1].pos_y == comp_y:
                                                exist = True
                                                break

                                    if not exist:
                                        cadd[1].pos_x = comp_x
                                        cadd[1].pos_y = comp_y
                                        for p in cadd[1].rot_input_pins + cadd[1].rot_output_pins:
                                            self.circuit.split_nets(
                                                p[0] + comp_x, p[1] + comp_y)

                                self.circuit.components.append(cadd)

                            self.refresh_nets()
                            self._pasted_components = None
                            self.circuit.push_history()
                            # self.parent.action_undo.set_sensitive(True)
                            # self.parent.action_redo.set_sensitive(False)
                            self.added = True
                            self.redraw = True
                    else:
                        exist = False
                        for c in self.circuit.components:
                            if c[0] != const.component_net:
                                if c[1].pos_x == self.cursor_x and c[1].pos_y == self.cursor_y:
                                    exist = True
                                    break

                        if not exist:
                            component_data = [
                                self._pushed_component_name, copy.deepcopy(self._pushed_component)]
                            component_data[1].pos_x = self.cursor_x
                            component_data[1].pos_y = self.cursor_y

                            if 0 <= component_data[1].pos_x + component_data[1].rot_comp_rect[0] + 3 and 0 <= component_data[1].pos_y + component_data[1].rot_comp_rect[1] + 3 and component_data[1].pos_x + component_data[1].rot_comp_rect[2] - 3 <= 1920 and component_data[1].pos_y + component_data[1].rot_comp_rect[3] - 3 <= 1080:
                                for p in component_data[1].rot_input_pins + component_data[1].rot_output_pins:
                                    self.circuit.split_nets(
                                        p[0] + self.cursor_x, p[1] + self.cursor_y)

                                self.circuit.components.append(component_data)
                                self.circuit.push_history()
                                # self.parent.action_undo.set_sensitive(True)
                                # self.parent.action_redo.set_sensitive(False)
                                self.added = True
                                self.redraw = True

                self.preadd = False
                self.mouse_down = False
                self.queue_draw()

            else:
                for c in self.circuit.components:
                    if c[0] != const.component_net:
                        im = inv_matrix(c[1].matrix)
                        if c[1].mouse_up(im[0] * (self.cursor_smooth_x - c[1].pos_x) + im[1] * (self.cursor_smooth_y - c[1].pos_y) + c[1].pos_x,
                                         im[2] * (self.cursor_smooth_x - c[1].pos_x) + im[3] * (
                                             self.cursor_smooth_y - c[1].pos_y) + c[1].pos_y,
                                         self.circuit.current_time):
                            if self.parent.pause_running_mode:
                                self.parent.clicked_on_pause = True
                            elif not self.circuit.analyze_logic():
                                self.parent.diagram_window.diagramarea.createDiagram()
                            self.queue_draw()
                            break

    # Middle Click
    def on_button_release_middle(self, *args):
        if args[1] == Gdk.BUTTON_MIDDLE:
            self.middle_move_enabled = False

    # Right Click
    def on_button_release_secondary(self, *args):
        if not self.parent.running_mode:
            if self._pasted_components:
                self._pasted_components = None
            elif self._pushed_component_name == const.component_none:
                self.set_selected_component_to_prop_window()
                self.parent.prop_window.present()
                # self.parent.action_property.set_active(True)
            elif not self.netstarted:
                self.parent.action_net.set_active(False)
                self.set_component(const.component_none)
            else:
                # Finish creating net
                self.netstarted = False

        self.queue_draw()

    def set_selected_component_to_prop_window(self):
        
        if len(self.circuit.selected_components) == 1:
            if self.circuit.selected_components[0][0] != const.component_net:
                self.parent.prop_window.setComponent(
                    self.circuit.selected_components[0][1])
            else:
                self.parent.prop_window.setComponent(None)
        else:
            self.parent.prop_window.setComponent(None)

    def set_component(self, comp_name):
        self._pasted_components = None
        self._pushed_component_name = comp_name
        self._pushed_component = copy.deepcopy(comp_dict[comp_name])

    def set_pasted_components(self, components):
        self._pasted_components = components
        for c in self._pasted_components:
            if c[0] != const.component_net:
                c[1].set_rot_props()
        self._pasted_rect = get_components_rect(components)
        self._paste_center_x = round(
            (self._pasted_rect[0] + self._pasted_rect[2]) / 2, -1)
        self._paste_center_y = round(
            (self._pasted_rect[1] + self._pasted_rect[3]) / 2, -1)
        self.drag_enabled = False
        self.rect_select_enabled = False
        self.queue_draw()

    def get_component(self):
        return self._pushed_component_name

    def rotate_left_picked_components(self):
        self._pushed_component.matrix = multiply_matrix(
            (0, 1, -1, 0), self._pushed_component.matrix)
        self._pushed_component.set_rot_props()

    def rotate_right_picked_components(self):
        self._pushed_component.matrix = multiply_matrix(
            (0, -1, 1, 0), self._pushed_component.matrix)
        self._pushed_component.set_rot_props()

    def flip_hori_picked_components(self):
        self._pushed_component.matrix = multiply_matrix(
            (-1, 0, 0, 1), self._pushed_component.matrix)
        self._pushed_component.set_rot_props()

    def flip_vert_picked_components(self):
        self._pushed_component.matrix = multiply_matrix(
            (1, 0, 0, -1), self._pushed_component.matrix)
        self._pushed_component.set_rot_props()
