from decimal import Decimal
import math
from typing import TYPE_CHECKING

import cairo

from ggate import Preference
from ggate.Utils import cairo_draw_text, cairo_paths, number_in_range
from ggate.const import Definitions

if TYPE_CHECKING:
    from ggate.MainFrame import MainFrame

from gi.repository import Gtk, Gdk, PangoCairo, Pango


class TimingGraphDiagram(Gtk.ScrolledWindow):
    def __get_timing(self):
        return self.timing_units[self.timing_unit]

    def __get_probes(self):
        return [
            cmp
            for cmp in self._circuit.components
            if cmp[0] == Definitions.component_probe
        ]
    
    def __queue_draw(self):
        self.name_area.queue_draw()
        self.chart_area.queue_draw()

    def __init__(self, parent: MainFrame):
        Gtk.ScrolledWindow.__init__(self)

        self.layout_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self._circuit = parent.circuit
        self._parent_drawarea = parent.drawarea

        self.name_area = Gtk.DrawingArea()
        self.chart_area = Gtk.DrawingArea()

        self.name_area_surface: cairo.ImageSurface = None
        self.chart_area_surface: cairo.ImageSurface = None

        # Seperate scrolling box so the name part is floating
        self.timing_scroll_window = Gtk.ScrolledWindow()
        self.timing_scroll_window.set_vexpand(True)
        self.timing_scroll_window.set_hexpand(True)
        self.timing_scroll_window.set_child(self.chart_area)

        self.scroll_hadj = self.timing_scroll_window.get_hadjustment()
        self.scroll_vadj = self.timing_scroll_window.get_vadjustment()

        self.layout_box.append(self.name_area)
        self.layout_box.append(self.timing_scroll_window)
        self.set_child(self.layout_box)

        controller = Gtk.EventControllerMotion()
        controller.connect("motion", self.on_timing_diagram_motion)
        self.chart_area.add_controller(controller)

        controller = Gtk.GestureClick()
        controller.set_button(Gdk.BUTTON_PRIMARY)
        controller.connect("pressed", self.on_timing_diagram_click)
        self.chart_area.add_controller(controller)

        # Sizings
        self._section_height = 45
        self._name_area_width = 100

        # Timing
        self.start_time = 0
        self.end_time = 0.1

        # x and y padding
        self._paddings = { "x": 10, "y": 15 }

        # Timing units
        self.timing_unit = 2
        self.timing_units = [
            { "unit": "ms", "scale": 10 ** 3 },
            { "unit": "µs", "scale": 10 ** 6 },
            { "unit": "ns", "scale": 10 ** 9 },
        ]

        # Graduations
        self.gra_pix = 150
        self.scale = 5_000_000 # px/sec

        # Cursor
        self.visible_cursor = {
            "x": 0,
            "y": 0,
            "oldX": 0,
            "oldY": 0,
        }

        # Layout sizing
        self.diagram_area_size = { "width": 0, "height": 0 }

    def name_area_draw_fn(self, widget, cr: cairo.Context, *args):
        if self.name_area_surface is None: return  # noqa: E701
        cr.set_source_surface(self.name_area_surface)
        cr.paint()
    
    def chart_area_draw_fn(self, widget, cr: cairo.Context, *args):
        if self.chart_area_surface is None: return # noqa: E701
        cr.set_source_surface(self.chart_area_surface)
        cr.paint()
        self._draw_cursor(cr)

    def on_timing_diagram_click(self, _, event, *args):
        if event[0] != Gdk.BUTTON_PRIMARY: return # noqa: E701
        if not number_in_range(
            self.visible_cursor["y"],
            self._section_height,
            self.diagram_area_size["height"]
        ): return # noqa: E701
        
        current_time = self.visible_cursor["x"] / self.scale + self.start_time
        self._circuit.current_time = current_time
        self._circuit.revert_state()
        self.__queue_draw()

    def on_timing_diagram_motion(self, controller, x_axis, y_axis, *args):
        self.visible_cursor["oldX"] = self.visible_cursor["x"]
        self.visible_cursor["oldY"] = self.visible_cursor["y"]

        self.visible_cursor["x"] = x_axis
        self.visible_cursor["y"] = x_axis

    def _draw_cursor(self, cr: cairo.Context):
        start = (self.visible_cursor["x"], self._section_height)
        end = (self.visible_cursor["x"], self.diagram_area_size["height"])
        # TODO: set color for stroke path
        cairo_paths(cr, start, end)
        cr.stroke()
        pass

    def _draw_names(self, cr: cairo.Context):
        name_layout = PangoCairo.create_layout(cr)
        name_layout.set_font_description(Preference.drawing_font)
        timing_unit = self.__get_timing()["unit"]
        probes = self.__get_probes()

        current_height = 0

        # TODO: Fill the border at the right side of the name area
        # cr.set_source_rgba()

        # Create a 1px border on the right side of the name area
        cr.rectangle(self._name_area_width, 0, 1, self.name_area.get_allocated_height())
        cr.fill()

        # Draw heading top
        cairo_draw_text(
            cr, name_layout,
            f"Probes / Time ({timing_unit})",
            self._paddings["x"],
            self._paddings["y"],
        )

        # Draw the headings bottom border
        current_height += self._section_height
        cairo_paths(
            cr, (0, current_height),
            (self._name_area_width, current_height)
        )

        # TODO: Stroke the divisions the border color
        # cr.set_source_rgba()

        # Draw divisions
        for probe in probes:
            current_height += self._section_height
            cairo_paths(cr, (0, current_height), (self._name_area_width, current_height))
        cr.stroke()

        # TODO: Set the color for the text
        # cr.set_source_rgba()

        # Draw the names of the probes
        for probe in probes:
            probe_name = probe[1].values[0]
            cairo_draw_text(
                cr, name_layout, probe_name,
                self._paddings["x"],
                current_height + self._paddings["y"],
            )
            current_height += self._section_height
        cr.fill()

    def _draw_graduations(self, cr: cairo.Context, layout: Pango.Layout):
        # Graduation interval calculation (same as before)
        gra_interval = Decimal(self.gra_pix) / Decimal(self.scale)
        order = 10 ** Decimal(int(math.log10(gra_interval)))
        normalized = gra_interval / order
        unit_scale = self.__get_timing()["scale"]

        if 0.15 <= normalized < 0.35:
            gra_interval = order * Decimal("0.2")
        elif 0.35 <= normalized <= 0.75:
            gra_interval = order * Decimal("0.5")
        else:
            gra_interval = order * Decimal("0.1")

        u_end_time = self.end_time * unit_scale
        u_gra_interval = gra_interval * unit_scale

        # TODO: Set color --- Start drawing ticks
        # cr.set_source_rgb(0.0, 0.0, 0.0)

        tick_time = Decimal(0)
        u_tick_time = Decimal(0)

        while u_tick_time <= Decimal(u_end_time):
            tick_x = float(tick_time) * self.scale + 0.5

            if tick_x >= 0 and tick_x <= self.diagram_width:
                # Draw vertical graduation line
                cr.set_source_rgb(0.5, 0.5, 0.5)
                cairo_paths(cr, (int(tick_x), 39), (int(tick_x), self.img_height - 1))
                cr.stroke()

                # Draw label
                cr.set_source_rgb(0.0, 0.0, 0.0)
                label = str(Decimal(u_tick_time).quantize(Decimal(".00")))
                cairo_draw_text(cr, layout, label, tick_x, 35, 0.5, 1.0)
                cr.fill()

            # Advance
            tick_time += gra_interval
            u_tick_time += u_gra_interval


    def _draw_graph(self, cr: cairo.Context):
        diagram_layout = PangoCairo.create_layout(cr)
        diagram_layout.set_font_description(Preference.drawing_font)
        self._draw_graduations(cr, diagram_layout)

        # vertical space between signals
        signal_spacing = self._section_height

        # height between high and low state
        signal_height = self._section_height - self._paddings["y"] * 2

        # subpixel offset for crisp rendering
        line_offset = 0.5

        # to avoid overlapping transition with horizontal lines
        transition_padding = 0.5

        history = self._circuit.probe_levels_history
        for i, current_frame in enumerate(history[:-1]):
            next_frame = history[i + 1]
            t0, t1 = current_frame[0], next_frame[0]

            # Skip if this frame is entirely outside the visible time window
            if t1 <= self.start_time or self.end_time < t0:
                continue

            signal_start_x = round((t0 - self.start_time) * self.scale)
            signal_end_x = round((t1 - self.start_time) * self.scale) + 1
            transition_x = round((t1 - self.start_time) * self.scale) + line_offset

            for j, level in enumerate(current_frame[1:]):
                base_y = j * signal_spacing
                y_high = base_y + line_offset
                y_low = base_y + signal_height + line_offset

                y = y_high if level else y_low
                cairo_paths(cr, (signal_start_x, y), (signal_end_x, y))

                # Draw vertical line at transition point if level changes
                if level != next_frame[j + 1]:
                    cairo_paths(
                        cr,
                        (transition_x, y_high + transition_padding),
                        (transition_x, y_low - transition_padding)
                    )
        
        # removed logic for drawing to end of draw area
        cr.stroke()

    def draw(self):
        probe_amount = len(self.__get_probes())
        # Calculate the draw height and add a little space
        draw_height = (self._section_height * probe_amount) + (self._section_height * 2.5)
        draw_width = max(1, (self.end_time - self.start_time) * self.scale)

        # Create the image surface
        name_surface = cairo.ImageSurface(cairo.FORMAT_RGB24, self._name_area_width, draw_height)
        chart_surface = cairo.ImageSurface(cairo.FORMAT_RGB24, draw_width, draw_height)

        # Create image ctx
        name_cr_ctx = cairo.Context(name_surface)
        chart_cr_ctx = cairo.Context(chart_surface)

        # Set the line width
        name_cr_ctx.set_line_width(1.0)
        chart_cr_ctx.set_line_width(1.0)

        # Set the size request of the name & timing diagram area
        self.name_area.set_size_request(self._name_area_width, draw_height)
        self.chart_area.set_size_request(draw_width, draw_height)

        # Save the context
        self.name_area_surface = name_surface
        self.chart_area_surface = chart_surface
        self.diagram_area_size = {
            "width": draw_width,
            "height": draw_height
        }

        # Start drawings
        self._draw_names(name_cr_ctx)
        self._draw_graph(chart_cr_ctx)

        self.queue_draw()








