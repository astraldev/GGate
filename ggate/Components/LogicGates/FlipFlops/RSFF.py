from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths, stack_with_tphl_lh
from ggate.const import definitions
from gettext import gettext as _


class RSFF(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("RS flip-flop")
    self.comp_rect = [10, -40, 100, 0]
    self.input_pins = [(10, -30), (10, -10)]
    self.output_pins = [(100, -30), (100, -10)]
    self.input_pins_dir = [definitions.direction_E, definitions.direction_E]
    self.output_pins_dir = [definitions.direction_W, definitions.direction_W]
    self.input_level = [False, False]
    self.output_level = [False, True]
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

  def drawComponent(self, cr, layout):
    cr.rectangle(30, -40, 50, 40)
    cr.stroke()
    cairo_draw_text(cr, layout, "S", 35, -30, 0.0, 0.5)
    cairo_draw_text(cr, layout, "R", 35, -10, 0.0, 0.5)
    cairo_draw_text(cr, layout, "Q", 75, -30, 1.0, 0.5)
    cairo_draw_text(cr, layout, "~Q", 75, -10, 1.0, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (10, -30), (30, -30))
    cairo_paths(cr, (10, -10), (30, -10))
    cairo_paths(cr, (80, -30), (100, -30))
    cairo_paths(cr, (80, -10), (100, -10))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -30), (30, -30))
    cr.stroke()
    if self.input_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -10), (30, -10))
    cr.stroke()
    if self.output_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (80, -30), (100, -30))
    cr.stroke()
    if self.output_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (80, -10), (100, -10))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 97 and self.pos_y - 37 <= y <= self.pos_y - 3:
      return True
    return False

  def initialize(self):
    self.output_stack = [[[0.0, False]], [[0.0, True]]]

  def calculate(self, input_datas, time):
    if input_datas[0] and not input_datas[1]:
      output_data = [True, False]
    elif not input_datas[0] and input_datas[1]:
      output_data = [False, True]
    elif input_datas[0] and input_datas[1]:
      output_data = [False, False]
    elif not self.output_level[0] and not self.output_level[1]:
      output_data = [True, False]
    else:
      return
    stack_with_tphl_lh(time, self.output_level, self.output_stack, output_data, self.tp_hl, self.tp_lh)