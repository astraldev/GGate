from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths, const
from ggate.const import definitions as const


from gettext import gettext as _


class SW(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("Switch")
    self.comp_rect = [10, -40, 70, 0]
    self.input_pins = []
    self.output_pins = [(70, -20)]
    self.input_pins_dir = []
    self.output_pins_dir = [const.direction_W]
    self.output_stack = [[]]
    self.input_level = []
    self.output_level = [False]
    self.output_store = [[]]
    self.prop_names = ["initstate"]
    self.properties.append((_("Initial state:"), (const.property_select, _("Low level"), _("High level")), ""))
    self.values.append(0)
    self.store = [False]

  def drawComponent(self, cr, layout):
    cr.rectangle(10, -40, 40, 40)
    cr.rectangle(15, -30, 30, 10)
    cr.stroke()
    cairo_draw_text(cr, layout, "L", 20, -10, 0.5, 0.5)
    cairo_draw_text(cr, layout, "H", 40, -10, 0.5, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (50, -20), (70, -20))
    cr.rectangle(17, -28, 12, 6)
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    if self.store[0]:
      cr.rectangle(30.5, -28.5, 13, 7)
    else:
      cr.rectangle(16.5, -28.5, 13, 7)
    cr.fill()
    if self.output_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (50, -20), (70, -20))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 67 and self.pos_y - 37 <= y <= self.pos_y - 3:
      return True
    return False

  def initialize(self):
    self.clicked_time = 0.0
    self.store[0] = self.values[0]

  def click(self, x, y, time):
    self.store[0] = not self.store[0]
    self.clicked_time = time
    return True

  def calculate(self, input_datas, time):
    self.output_stack = [[[self.clicked_time, self.store[0]]]]