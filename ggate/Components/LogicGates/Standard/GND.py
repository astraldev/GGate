from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths, const
from ggate.const import definitions as const


from gettext import gettext as _


class GND(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("GND rail")
    self.comp_rect = [10, -50, 30, 0]
    self.input_pins = []
    self.output_pins = [(20, -50)]
    self.input_pins_dir = []
    self.output_pins_dir = [const.direction_S]
    self.input_level = []
    self.output_level = [False]
    self.output_stack = [[]]

  def drawComponent(self, cr, layout):
    cairo_paths(cr, (10, -30), (30, -30))
    cairo_paths(cr, (16, -30), (12, -20))
    cairo_paths(cr, (22, -30), (18, -20))
    cairo_paths(cr, (28, -30), (24, -20))
    cr.stroke()
    cairo_draw_text(cr, layout, "GND", 20, -10, 0.5, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (20, -50), (20, -30))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (20, -50), (20, -30))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 27 and self.pos_y - 47 <= y <= self.pos_y - 3:
      return True
    return False