# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame
  from ggate.CircuitManager import CircuitManager

import math
import copy
import cairo
from ggate.const import definitions as const
from ggate.MenuPopover import ContextMenu, RunningMenu
from ggate.Utils import cairo_paths, inv_matrix, multiply_matrix, create_component_matrix, get_components_rect, draw_rounded_rectangle, clamp
from ggate.Components.LogicGates import logic_gates
from ggate import Preference
from gi.repository import Gtk, Gdk, Pango, PangoCairo


class DrawArea(Gtk.ScrolledWindow):
    def __init__(self, parent: MainFrame):
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

        self.vadj.set_value(self.height / 2)
        self.hadj.set_value(self.width / 2)

        # Default : 10
        self.grid_step = Preference.grid_step
        self.min_grid_step = 10
        self.max_grid_step = 30

        self.actions = [
            'menu.flip_hori', 'menu.flip_verti', 
            'menu.rot_left', 'menu.rot_right', 
            'menu.properties'
        ]
        for action in self.actions:
            self.install_action(action, None, self.menu_activated)

        self.context_menu = ContextMenu(self)
        self.run_menu = RunningMenu(self)

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
        self.circuit: CircuitManager = None
        self.redraw = True
        self.netstarted = False
        self.mpixbuf = cairo.ImageSurface(cairo.FORMAT_RGB24, self.width, self.height)
        self._pasted_components = None
        self._pushed_component_name = const.component_none
        self._pushed_component = logic_gates[const.component_none]

    def queue_draw(self, *args):
        self.show()
        self.drawingarea.queue_draw()
        super().queue_draw(*args)
        self.drawingarea.show()
        self.drawingarea.queue_draw()
    
    def menu_activated(self, widget, action_name, *args):
        action = action_name.split('.')[-1]

        if action == 'rot_left':
            self.parent.on_action_rotate_left_90()

        elif action == 'rot_right':
            self.parent.on_action_rotate_right_90()

        elif action == 'flip_hori':
            self.parent.on_action_flip_horizontally()

        elif action == 'flip_verti':
            self.parent.on_action_flip_vertically()

        elif action == 'properties':
            self.set_selected_component_to_prop_window()
            self.parent.prop_window.present()
    
    def draw_net(self, net, mcr: cairo.Context):
        """
        This method draws all states of the net.

        TODO:
          - Make a curve for net joints.
          - Include optimizations for animations
        """

        if net[0] != const.component_net:
            return

        matrix = mcr.get_matrix()
        source = mcr.get_source()

        is_selected = net in self.circuit.selected_components
        is_hovered = net == self.nearest_component and self.cursor_over \
            and self._pushed_component_name == const.component_none

        # Get net level
        if self.parent.running_mode:
            # Draw net terminal
            mcr.set_source(Preference.terminal_color_running)
            if (net[1], net[2]) not in self.circuit.net_no_dot:
                mcr.rectangle(net[1]-1.5, net[2]-1.5, 3, 3)
            elif (net[3], net[4]) not in self.circuit.net_no_dot:
                mcr.rectangle(net[3]-1.5, net[4]-1.5, 3, 3)
            mcr.fill()

            # Get the color of the net
            net_level_color = Preference.net_color_running
            for i, connection in enumerate(self.circuit.net_connections):
                if (net[1], net[2]) in connection:
                    if self.circuit.net_levels[i] == 1:
                        net_level_color = Preference.highlevel_color
                    elif self.circuit.net_levels[i] == 0:
                        net_level_color = Preference.lowlevel_color
                    else:
                        net_level_color = Preference.net_color_running

            # Draw net
            mcr.set_source(net_level_color)
            cairo_paths(mcr, (net[1], net[2]), (net[3], net[4]))
            mcr.stroke()

        else:
            # Sets the net color
            mcr.set_source(Preference.net_color)
            if self.component_dragged and net in self.circuit.selected_components or is_selected:
                mcr.set_source(Preference.selected_color)
            elif is_hovered:
                mcr.set_source(Preference.net_high_color)

            # Draw net
            cairo_paths(mcr, (net[1], net[2]), (net[3], net[4]))
            mcr.stroke()

            # Draw net terminal
            mcr.set_source(Preference.terminal_color)
            mcr.rectangle(net[1]-1.5, net[2]-1.5, 3, 3)
            mcr.rectangle(net[3]-1.5, net[4]-1.5, 3, 3)

        mcr.fill()

        # Context resets
        mcr.set_source(source)
        mcr.set_matrix(matrix)
    
    def draw_component(self, cmp, mcr: cairo.Context, layout: Pango.Layout):
        if cmp[0] == const.component_net:
            self.draw_net(cmp, mcr)
            return

        matrix = mcr.get_matrix()
        source = mcr.get_source()
        is_selected = cmp in self.circuit.selected_components
        is_hovered = cmp == self.nearest_component and self.cursor_over \
            and self._pushed_component_name == const.component_none

        if is_selected:
            mcr.set_source(Preference.selected_color)
        else:
            mcr.set_source(Preference.terminal_color)

        # Draw component terminal
        if not self.parent.running_mode:
            for p in cmp[1].rot_input_pins + cmp[1].rot_output_pins:
                mcr.rectangle(cmp[1].pos_x+p[0]-1.5, cmp[1].pos_y+p[1]-1.5, 3, 3)
            mcr.fill()

        # Draw component
        mcr.translate(cmp[1].pos_x, cmp[1].pos_y)
        cmp_matrix = create_component_matrix(cmp)
        mcr.set_matrix(cmp_matrix.multiply(mcr.get_matrix()))

        if self.parent.running_mode:
            mcr.set_source(Preference.component_color_running)
            cmp[1].drawComponent(mcr, layout)
            cmp[1].drawComponentRunOverlap(mcr, layout)
        else:
            mcr.set_source(Preference.component_color)
            if cmp in self.circuit.selected_components:
                mcr.set_source(Preference.selected_color)
            elif is_hovered:
                mcr.set_source(Preference.component_high_color)

            cmp[1].drawComponent(mcr, layout)
            cmp[1].drawComponentEditOverlap(mcr, layout)

        mcr.fill()

        mcr.set_source(source)
        mcr.set_matrix(matrix)
    
    def draw_pushed_component(self, where, cmp, cr: cairo.Context, layout: Pango.Layout):
        name = self._pushed_component_name
        matrix = cr.get_matrix()
        source = cr.get_source()

        if name == const.component_net:
            # Draw net cursor
            cr.set_source(Preference.cursor_color)
            cr.arc(self.cursor_x, self.cursor_y, 3, 0, 2 * math.pi)
            cr.stroke()

            if self.netstarted:
                cr.set_source(Preference.net_color)
                moving_right = self.net_right and self.netstart_x < self.cursor_x
                moving_left = self.net_left and self.cursor_x < self.netstart_x

                if moving_right or moving_left:
                    cairo_paths(cr, (self.netstart_x, self.netstart_y), (self.cursor_x, self.netstart_y))
                    self.netstart_y != self.cursor_y and \
                        cairo_paths(cr, (self.cursor_x, self.netstart_y), (self.cursor_x, self.cursor_y))
                    
                    cr.stroke()
                    cr.set_source(Preference.terminal_color)
                    cr.rectangle(self.cursor_x-1.5, self.netstart_y-1.5, 3, 3)
                    cr.fill()
                else:
                    self.netstart_y != self.cursor_y and \
                        cairo_paths(cr, (self.netstart_x, self.netstart_y), (self.netstart_x, self.cursor_y))
                    self.netstart_x != self.cursor_x and \
                        cairo_paths(cr, (self.netstart_x, self.cursor_y), (self.cursor_x, self.cursor_y))
    
                    cr.stroke()
                    cr.set_source(Preference.terminal_color)
                    cr.rectangle(self.netstart_x-1.5, self.cursor_y-1.5, 3, 3)
                    cr.fill()
                
                cr.rectangle(self.netstart_x-1.5, self.netstart_y-1.5, 3, 3)
                cr.fill()
        else:
            if self.preadd:
                cr.set_source(Preference.preadd_color)
            else:
                cr.set_source(Preference.picked_color)

            if cmp[0] != const.component_net:
                cr.translate(where[0], where[1])
                cmp_matrix = create_component_matrix(cmp)
                cr.set_matrix(cmp_matrix.multiply(cr.get_matrix()))
                cmp[1].drawComponent(cr, layout)
                cmp[1].drawComponentEditOverlap(cr, layout)
            else:
                cairo_paths(cr, (cmp[1], cmp[2]), (cmp[3], cmp[4]))
                cr.stroke()
                cr.rectangle(cmp[1]-1.5, cmp[2]-1.5, 3, 3)
                cr.rectangle(cmp[3]-1.5, cmp[4]-1.5, 3, 3)
                cr.fill()

        cr.set_source(source)
        cr.set_matrix(matrix)

    def on_draw(self, widget, cr: cairo.Context, width, height, *args):
        # Rerender whole screen
        if self.redraw:
            mcr = cairo.Context(self.mpixbuf)
            if self.parent.running_mode:
                mcr.set_source(Preference.bg_color_running)
            else:
                mcr.set_source(Preference.bg_color)

            # Setup the background color
            mcr.rectangle(0, 0, self.width, self.height)
            mcr.fill()

            # Draw grids
            if not self.parent.running_mode:
                mcr.set_source(Preference.grid_color)
                for x in range(0, self.width, self.grid_step):
                    cairo_paths(mcr, (x, 0), (x, self.height))
                for y in range(0, self.height, self.grid_step):
                    cairo_paths(mcr, (0, y), (self.width, y))
                mcr.stroke()

            self.redraw = False

        cr.set_source_surface(self.mpixbuf, 0, 0)
        cr.paint()

        cr.translate(0.5, 0.5)
        cr.set_line_width(1.0)
        matrix = cr.get_matrix()
        source = cr.get_source()
    
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(Preference.drawing_font)
    
        [self.draw_component(cmp, cr, layout) for cmp in self.circuit.components]

        """
        Draw rectangle selection
        """
        if self.rect_select_enabled:
            x, y = self.select_start_x - 0.5, self.select_start_y - 0.5
            width = self.cursor_smooth_x - self.select_start_x
            height = self.cursor_smooth_y - self.select_start_y

            cr.set_source(Preference.selection_box)
            draw_rounded_rectangle(cr, x, y, width, height)
            cr.fill()

            cr.set_source(Preference.selection_box_border)
            draw_rounded_rectangle(cr, x, y, width, height)
            cr.stroke()

        cr.set_source(source)
        cr.set_matrix(matrix)

        """
        Draw picked or pasted components
        """
        if not self.parent.running_mode and \
            not self.added and self.cursor_over and \
            (self._pushed_component_name != const.component_none or self._pasted_components):

            if self._pasted_components:
                where = (
                    self.cursor_x - self._paste_center_x,
                    self.cursor_y - self._paste_center_y
                )
                [
                    self.draw_pushed_component(where, pasted, cr, layout) \
                    for pasted in self._pasted_components
                ]
            
            elif self._pushed_component_name:
                where = [self.cursor_x, self.cursor_y]
                self.draw_pushed_component(
                    where, [self._pushed_component_name, self._pushed_component],
                    cr, layout
                )
    
        self.added = False
        cr.set_source(source)
        cr.set_matrix(matrix)

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
                            self.cursor_x = c[1] - c[1] % self.grid_step
                            self.cursor_y = int(
                                self.cursor_smooth_y - self.cursor_smooth_y % self.grid_step)
                if c[2] == c[4]:
                    if c[1] < self.cursor_smooth_x < c[3] or c[3] < self.cursor_smooth_x < c[1]:
                        if min_dist > (self.cursor_smooth_y - c[2]) ** 2:
                            min_dist = (self.cursor_smooth_y - c[2]) ** 2
                            self.cursor_x = int(
                                self.cursor_smooth_x - self.cursor_smooth_x % self.grid_step)
                            self.cursor_y = c[2] - c[2] % self.grid_step

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

        modifier = args[1]

        # If Ctrl (+) is pressed, enlarge selected components
        if key_val == Gdk.KEY_plus and (modifier & Gdk.ModifierType.CONTROL_MASK):
            selected_components = [c for c in self.circuit.selected_components if c[0] != const.component_net]

            # Enlarge selected components
            if len(selected_components) > 0:
                for component in self.circuit.selected_components:
                    if component[0] == const.component_net: continue
                    component[1].enlarge()
                    self.queue_draw()

            # Enlarge grid size
            else:
                self.grid_step = clamp(self.grid_step + 1, self.min_grid_step, self.max_grid_step)
                self.redraw = True
                self.queue_draw()

        # Rotate Right => R | r
        if key_val == Gdk.KEY_R or key_val == Gdk.KEY_r:
            self.parent.on_action_rotate_right_90()

        # Rotate Left => L | l
        if key_val == Gdk.KEY_L or key_val == Gdk.KEY_l:
            self.parent.on_action_rotate_left_90()

        # Flip Horizontally => H | h
        if key_val == Gdk.KEY_H or key_val == Gdk.KEY_h:
            self.parent.on_action_flip_horizontally()

        # Flip Vertically => V | v
        if key_val == Gdk.KEY_V or key_val == Gdk.KEY_v:
            self.parent.on_action_flip_vertically()

        # Delete => Delete | Backspace
        if key_val == Gdk.KEY_Delete or key_val == Gdk.KEY_BackSpace:
            self.parent.on_action_delete_pressed()

    def on_key_press(self, *args):
        if self.parent.running_mode:
            return

        if self.cursor_over:
            if self._pushed_component_name != const.component_none:
                if args[1] == Gdk.KEY_Control_L or args[1] == Gdk.KEY_Control_R:

                    oldcursor_x = self.cursor_x
                    oldcursor_y = self.cursor_y

                    self.cursor_x = int(self.cursor_smooth_x - self.cursor_smooth_x % self.grid_step)
                    self.cursor_y = int(self.cursor_smooth_y - self.cursor_smooth_y % self.grid_step)

                    if oldcursor_x != self.cursor_x or oldcursor_y != self.cursor_y:
                        self.queue_draw()

    def on_motion(self,  *args):
        """TODO: Optimize this"""
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
            if not args[0].get_current_event_state() & Gdk.ModifierType.CONTROL_MASK:
                min_dist = self.set_cursor_to_nearest_terminal(min_dist)

            if min_dist == 225:
                self.cursor_x = int(self.cursor_smooth_x -
                                    self.cursor_smooth_x % self.grid_step)
                self.cursor_y = int(self.cursor_smooth_y -
                                    self.cursor_smooth_y % self.grid_step)
            if oldcursor_x != self.cursor_x or oldcursor_y != self.cursor_y:
                self.queue_draw()

        else:
            self.cursor_x = int(self.cursor_smooth_x -
                                self.cursor_smooth_x % self.grid_step)
            self.cursor_y = int(self.cursor_smooth_y -
                                self.cursor_smooth_y % self.grid_step)
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
                    self.drag_delta_x = ddx - ddx % self.grid_step
                else:
                    self.drag_delta_x = ddx + (-ddx % self.grid_step)
                if ddy >= 0:
                    self.drag_delta_y = ddy - ddy % self.grid_step
                else:
                    self.drag_delta_y = ddy + (-ddy % self.grid_step)
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
                        self.comps_rect = get_components_rect(self.circuit.selected_components)

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
                            if not self.parent.pause_running_mode and not self.circuit.analyze_logic():
                                self.parent.diagram_window.diagram_area.createDiagram()
                            self.queue_draw()
                            break

    # Middle Click
    def on_button_release_middle(self, *args):
        if args[1] == Gdk.BUTTON_MIDDLE:
            self.middle_move_enabled = False

    # Right Click
    def on_button_release_secondary(self, *args):

        if not self.parent.running_mode:

            if (not self.parent.action_net.get_active()) and (not self.netstarted) and (not self._pushed_component):
                self.context_menu.present(args[2], args[3], args)

            if self._pasted_components:
                self._pasted_components = None

            elif not self.netstarted:
                self.parent.action_net.set_active(False)
                self.set_component(const.component_none)
            else:
                # Finish creating net
                self.netstarted = False
        else:
            self.run_menu.present(args[2], args[3])

        self.queue_draw()

    def set_selected_component_to_prop_window(self):
        if len(self.circuit.selected_components) == 1:
            if self.circuit.selected_components[0][0] != const.component_net:
                self.parent.prop_window.set_component(
                    self.circuit.selected_components[0][1])
            else:
                self.parent.prop_window.set_component(None)
        else:
            self.parent.prop_window.set_component(None)

    def set_component(self, comp_name):
        self._pasted_components = None
        self._pushed_component_name = comp_name
        self._pushed_component = copy.deepcopy(logic_gates[comp_name])

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

    "Component rotations: -90deg, 90deg x180deg y180deg"
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
