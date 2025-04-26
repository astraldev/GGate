from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths, stack_with_tphl_lh
from ggate.const import definitions


import math
from gettext import gettext as _


class JKFF(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("JK flip-flop")
    self.comp_rect = [10, -60, 110, 0]
    self.input_pins = [(10, -50), (10, -30), (10, -10)]
    self.output_pins = [(110, -50), (110, -10)]
    self.input_pins_dir = [definitions.direction_E, definitions.direction_E, definitions.direction_E]
    self.output_pins_dir = [definitions.direction_W, definitions.direction_W]
    self.input_level = [False, False, False]
    self.output_level = [False, True]
    self.tp_hl = 0.0
    self.tp_lh = 0.0
    self.prop_names = ["trig", "tphl", "tplh"]
    self.properties.append((_("Trigger type:"), (definitions.property_select, _("Positive edge"), _("Negative edge")), ""))
    self.values.append(0)
    self.properties.append((_("Propagation delay:"), None, ""))
    self.properties.append((_("tPHL:"), (definitions.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)
    self.properties.append((_("tPLH:"), (definitions.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)

  def propertyChanged(self, prop):
    self.tp_hl = prop[1] * 0.000001
    self.tp_lh = prop[2] * 0.000001
    return False

  def drawComponent(self, cr, layout):
    cr.rectangle(30, -60, 60, 60)
    if self.values[0] == 1:
      cr.arc(25, -30, 5, 0, 2 * math.pi)
    cairo_paths(cr, (30, -35), (40, -30), (30, -25))
    cr.stroke()
    cairo_draw_text(cr, layout, "J", 45, -50, 0.0, 0.5)
    cairo_draw_text(cr, layout, "CK", 45, -30, 0.0, 0.5)
    cairo_draw_text(cr, layout, "K", 45, -10, 0.0, 0.5)
    cairo_draw_text(cr, layout, "Q", 85, -50, 1.0, 0.5)
    cairo_draw_text(cr, layout, "~Q",85, -10, 1.0, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (10, -50), (30, -50))
    if self.values[0] == 0:
      cairo_paths(cr, (10, -30), (30, -30))
    else:
      cairo_paths(cr, (10, -30), (20, -30))
    cairo_paths(cr, (10, -10), (30, -10))
    cairo_paths(cr, (90, -50), (110, -50))
    cairo_paths(cr, (90, -10), (110, -10))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -50), (30, -50))
    cr.stroke()
    if self.input_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if self.values[0] == 0:
      cairo_paths(cr, (10, -30), (30, -30))
    else:
      cairo_paths(cr, (10, -30), (20, -30))
    cr.stroke()
    if self.input_level[2]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -10), (30, -10))
    cr.stroke()
    if self.output_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (90, -50), (110, -50))
    cr.stroke()
    if self.output_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (90, -10), (110, -10))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 107 and self.pos_y - 57 <= y <= self.pos_y - 3:
      return True
    return False

  def initialize(self):
    self.output_stack = [[[0.0, False]], [[0.0, True]]]

  def calculate(self, input_datas, time):
    if (self.values[0] == 0 and not self.input_level[1] and input_datas[1]) or (self.values[0] == 1 and self.input_level[1] and not input_datas[1]): # trigger
      if self.input_level[0] and not self.input_level[2]:
        output_data = [True, False]
      elif not self.input_level[0] and self.input_level[2]:
        output_data = [False, True]
      elif self.input_level[0] and self.input_level[2]:
        output_data = [self.output_level[1], self.output_level[0]]
      else:
        return
      stack_with_tphl_lh(time, self.output_level, self.output_stack, output_data, self.tp_hl, self.tp_lh)