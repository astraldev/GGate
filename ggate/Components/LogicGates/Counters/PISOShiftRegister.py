from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths, const, stack_with_tphl_lh
from ggate.const import definitions as const


import math
from gettext import gettext as _


class PISOShiftRegister(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("PISO shift register")
    self.comp_rect = [10, -140, 120, 0]
    self.input_pins = [(10, -110), (10, -90), (10, -70), (10, -50), (10, -30), (10, -10)]
    self.output_pins = [(120, -70), (120, -50)]
    self.input_pins_dir = [const.direction_E, const.direction_E, const.direction_E, const.direction_E, const.direction_E, const.direction_E]
    self.output_pins_dir = [const.direction_W, const.direction_W]
    self.input_level = [False, False, False, False, False, False]
    self.output_level = [False, True]
    self.tp_hl = 0.0
    self.tp_lh = 0.0
    self.inpin_t = -90
    self.inpin_b = -30
    self.prop_names = ["bits", "trig", "tphl", "tplh"]
    self.properties.append((_("Number of bits:"), (const.property_int, 1, 8, 100), ""))
    self.values.append(4)
    self.properties.append((_("Trigger type:"), (const.property_select, _("Positive edge"), _("Negative edge")), ""))
    self.values.append(0)
    self.properties.append((_("Propagation delay:"), None, ""))
    self.properties.append((_("tPHL:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)
    self.properties.append((_("tPLH:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)

  def propertyChanged(self, prop):
    self.inpin_t = -60 - (prop[0] - 1) * 10
    self.inpin_b = -60 + (prop[0] - 1) * 10
    self.comp_rect = [10, min((self.inpin_t - 50, -90)), 120, max((self.inpin_b + 30, -30))]
    self.input_pins = [(10, y) for y in range(self.inpin_t - 20, self.inpin_b + 21, 20)]
    self.input_pins_dir = [const.direction_E for i in range(prop[0] + 2)]
    self.input_level = [False for i in range(prop[0] + 2)]
    self.tp_hl = prop[2] * 0.000001
    self.tp_lh = prop[3] * 0.000001
    return False

  def drawComponent(self, cr, layout):
    cr.rectangle(30, self.comp_rect[1], 70, self.comp_rect[3] - self.comp_rect[1])
    if self.values[1] == 1:
      cr.arc(25, self.inpin_b + 20, 5, 0, 2 * math.pi)
    cairo_paths(cr, (30, self.inpin_b + 15), (40, self.inpin_b + 20), (30, self.inpin_b + 25))
    cr.stroke()
    cairo_draw_text(cr, layout, "PISO", 65, self.comp_rect[1] + 10, 0.5, 0.5)
    for i, y in enumerate(range(self.inpin_t, self.inpin_b + 1, 20)):
      cairo_draw_text(cr, layout, "D%d" % i, 45, y, 0.0, 0.5)
    cairo_draw_text(cr, layout, "W/S", 45, self.inpin_t - 20, 0.0, 0.5)
    cairo_draw_text(cr, layout, "CK", 45, self.inpin_b + 20, 0.0, 0.5)
    cairo_draw_text(cr, layout, "Q", 95, -70, 1.0, 0.5)
    cairo_draw_text(cr, layout, "~Q", 95, -50, 1.0, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (10, self.inpin_t - 20), (30, self.inpin_t - 20))
    if self.values[1] == 0:
      cairo_paths(cr, (10, self.inpin_b + 20), (30, self.inpin_b + 20))
    else:
      cairo_paths(cr, (10, self.inpin_b + 20), (20, self.inpin_b + 20))
    for i, y in enumerate(range(self.inpin_t, self.inpin_b + 1, 20)):
      cairo_paths(cr, (10, y), (30, y))
    cairo_paths(cr, (100, -70), (120, -70))
    cairo_paths(cr, (100, -50), (120, -50))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    for i, y in enumerate(range(self.inpin_t - 20, self.inpin_b + 1, 20)):
      if self.input_level[i]:
        cr.set_source(Preference.highlevel_color)
      else:
        cr.set_source(Preference.lowlevel_color)
      cairo_paths(cr, (10, y), (30, y))
      cr.stroke()
    if self.input_level[-1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if self.values[1] == 0:
      cairo_paths(cr, (10, self.inpin_b + 20), (30, self.inpin_b + 20))
    else:
      cairo_paths(cr, (10, self.inpin_b + 20), (20, self.inpin_b + 20))
    cr.stroke()
    if self.output_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (100, -70), (120, -70))
    cr.stroke()
    if self.output_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (100, -50), (120, -50))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + self.comp_rect[0] + 3 <= x <= self.pos_x + self.comp_rect[2] - 3 and self.pos_y + self.comp_rect[1] + 3 <= y <= self.pos_y + self.comp_rect[3] - 3:
      return True
    return False

  def initialize(self):
    self.store = [False for i in range(self.values[0])]
    self.output_stack = [[[0.0, False]], [[0.0, True]]]

  def calculate(self, input_datas, time):
    if (self.values[1] == 0 and not self.input_level[-1] and input_datas[-1]) or (self.values[1] == 1 and self.input_level[-1] and not input_datas[-1]): # trigger
      if input_datas[0] == 0:
        self.store = input_datas[1:-2]
        output_data = [input_datas[-2], not input_datas[-2]]
      elif self.store:
        output = self.store.pop()
        output_data = [output, not output]
      else:
        return
      stack_with_tphl_lh(time, self.output_level, self.output_stack, output_data, self.tp_hl, self.tp_lh)
    else:
      return