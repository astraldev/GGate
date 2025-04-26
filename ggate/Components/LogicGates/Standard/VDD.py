from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths
from ggate.const import definitions
from gettext import gettext as _

class VDD(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("Vdd rail")
    self.comp_rect = [10, -40, 30, 0]
    self.input_pins = []
    self.output_pins = [(20, 0)]
    self.input_pins_dir = []
    self.output_pins_dir = [definitions.direction_N]
    self.input_level = []
    self.output_level = [True]
    self.output_stack = [[]]

  def drawComponent(self, cr, layout):
    cairo_paths(cr, (10, -20), (30, -20))
    cr.rectangle(19, -21, 2, 2)
    cr.stroke()
    cairo_draw_text(cr, layout, "Vdd", 20, -30, 0.5, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (20, -20), (20, 0))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    cr.set_source(Preference.highlevel_color)
    cairo_paths(cr, (20, -20), (20, 0))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 27 and self.pos_y - 37 <= y <= self.pos_y - 3:
      return True
    return False