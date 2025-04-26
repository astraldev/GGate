import math
import cairo
from ggate import Preference
from ggate.Utils import cairo_draw_text, cairo_paths
from ggate.const import definitions
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from gettext import gettext as _

class NOT(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("NOT")
    self.comp_rect = [10, -40, 90, 0]
    self.input_pins = [(10, -20)]
    self.output_pins = [(90, -20)]

    self.input_pins_dir = [definitions.direction_E]
    self.output_pins_dir = [definitions.direction_W]

    self.input_level = [False]
    self.output_level = [True]

    self.tp_hl = 0.0
    self.tp_lh = 0.0

    self.prop_names = ["tphl", "tplh"]

    self.properties.append((_("Propagation delay:"), None, ""))
    self.properties.append((_("tPHL:"), (definitions.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)
    self.properties.append((_("tPLH:"), (definitions.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)

  def propertyChanged(self, prop):
    self.tp_hl = prop[0] * 0.000001
    self.tp_lh = prop[1] * 0.000001
    return False

  def drawComponent(self, cr: cairo.Context, layout):
    if Preference.symbol_type == 0:
      cairo_paths(cr, (30, -35), (30, -5), (60, -20))

    elif Preference.symbol_type == 1:
      cr.rectangle(30, -40, 30, 40)

    cr.close_path()
    cr.stroke()
    cr.arc(66, - 20, 6, 0, 2 * math.pi)
    cr.stroke()

    if Preference.symbol_type == 1:
      cairo_draw_text(cr, layout, "1", 45, -40, 0.5, 0.0)
      cr.fill()
    

  def drawComponentEditOverlap(self, cr: cairo.Context, layout):
    cairo_paths(cr, (10, -20), (30, -20))
    cairo_paths(cr, (72, -20), (90, -20))
    cr.stroke()

  def drawComponentRunOverlap(self, cr: cairo.Context, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -20), (30, -20))
    cr.stroke()
    if self.output_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (72, -20), (90, -20))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 87 and self.pos_y - 37 <= y <= self.pos_y - 3:
      return True
    return False

  def calculate(self, input_datas, time):
    new_output = not input_datas[0]
    if new_output != self.output_level[0]:
      if self.output_level[0]:
        self.output_stack = [[[time + self.tp_hl, new_output]]]
      else:
        self.output_stack = [[[time + self.tp_lh, new_output]]]
    else:
      self.output_stack = [[]]
