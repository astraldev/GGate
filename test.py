import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
import math

class CatWindow(Adw.ApplicationWindow):
    def __init__(self, application=None):
        super().__init__(title="Cute Cat with Cairo", application=application)
        self.set_default_size(300, 300)

        drawing_area = Gtk.DrawingArea()
        drawing_area.set_draw_func(self.on_draw)
        self.set_content(drawing_area)
        self.present()

    def on_draw(self, area, ctx, width, height):
        # Center and scale
        ctx.translate(width / 2, height / 2 + 20)
        scale = min(width, height) / 200.0
        ctx.scale(scale, scale)

        # Draw head (circle)
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.arc(0, -40, 40, 0, 2 * math.pi)
        ctx.fill()

        # Draw ears
        ctx.move_to(-30, -70); ctx.line_to(-60, -110); ctx.line_to(-10, -80)
        ctx.move_to(30, -70); ctx.line_to(60, -110); ctx.line_to(10, -80)
        ctx.fill()

        # Draw body
        ctx.arc(0, 40, 60, 0, math.pi)
        ctx.fill()

        # Draw tail
        ctx.set_line_width(12)
        ctx.move_to(60, 20)
        ctx.curve_to(110, 0, 110, 80, 60, 60)
        ctx.stroke()

        # Draw eyes
        ctx.set_source_rgb(1, 1, 1)
        for x in (-15, 15):
            ctx.arc(x, -50, 8, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgb(0, 0, 0)
            ctx.arc(x, -48, 3, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgb(1, 1, 1)  # reset for next eye

class CatApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.CatApp")

    def do_activate(self):
        win = CatWindow(application=self)
        win.present()

if __name__ == "__main__":
    app = CatApp()
    app.run()
