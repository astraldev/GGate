from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths, const, stack_with_tphl_lh
from ggate.const import definitions as const


import math
from gettext import gettext as _


class SIPOShiftRegister(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("SIPO shift register")
    self.comp_rect = [10, -100, 120, 0]
    self.input_pins = [(10, -60), (10, -40), (10, -20)]
    self.output_pins = [(120, -70), (120, -50), (120, -30), (120, -10)]
    self.input_pins_dir = [const.direction_E, const.direction_E, const.direction_E]
    self.output_pins_dir = [const.direction_W, const.direction_W, const.direction_W, const.direction_W]
    self.input_level = [False, False, False]
    self.output_level = [False, False, False, False]
    self.tp_hl = 0.0
    self.tp_lh = 0.0
    self.outpin_t = -70
    self.outpin_b = -10
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
    self.store = [False, False, False, False]

  def propertyChanged(self, prop):
    self.outpin_t = -40 - (prop[0] - 1) * 10
    self.outpin_b = -40 + (prop[0] - 1) * 10
    self.comp_rect = [10, min((self.outpin_t - 30, -90)), 120, max((self.outpin_b + 10, -10))]
    self.output_pins = [(120, y) for y in range(self.outpin_t, self.outpin_b + 1, 20)]
    self.output_pins_dir = [const.direction_W for i in range(prop[0])]
    self.output_level = [False for i in range(prop[0])]
    self.tp_hl = prop[2] * 0.000001
    self.tp_lh = prop[3] * 0.000001
    self.store = [False for i in range(prop[0])]
    return False

  def drawComponent(self, cr, layout):
    cr.rectangle(30, self.comp_rect[1], 70, self.comp_rect[3] - self.comp_rect[1])
    if self.values[1] == 1:
      cr.arc(25, -40, 5, 0, 2 * math.pi)
    cairo_paths(cr, (30, -45), (40, -40), (30, -35))
    cr.stroke()
    cairo_draw_text(cr, layout, "SIPO", 65, self.comp_rect[1] + 10, 0.5, 0.5)
    cairo_draw_text(cr, layout, "D", 45, -60, 0.0, 0.5)
    cairo_draw_text(cr, layout, "CK", 45, -40, 0.0, 0.5)
    cairo_draw_text(cr, layout, "RST", 45, -20, 0.0, 0.5)
    for i, y in enumerate(range(self.outpin_t, self.outpin_b + 1, 20)):
      cairo_draw_text(cr, layout, "Q%d" % i, 95, y, 1.0, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (10, -60), (30, -60))
    if self.values[1] == 0:
      cairo_paths(cr, (10, -40), (30, -40))
    else:
      cairo_paths(cr, (10, -40), (20, -40))
    cairo_paths(cr, (10, -20), (30, -20))
    for i, y in enumerate(range(self.outpin_t, self.outpin_b + 1, 20)):
      cairo_paths(cr, (100, y), (120, y))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -60), (30, -60))
    cr.stroke()
    if self.input_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if self.values[1] == 0:
      cairo_paths(cr, (10, -40), (30, -40))
    else:
      cairo_paths(cr, (10, -40), (20, -40))
    cr.stroke()
    if self.input_level[2]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -20), (30, -20))
    cr.stroke()
    for i, y in enumerate(range(self.outpin_t, self.outpin_b + 1, 20)):
      if self.output_level[i]:
        cr.set_source(Preference.highlevel_color)
      else:
        cr.set_source(Preference.lowlevel_color)
      cairo_paths(cr, (100, y), (120, y))
      cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + self.comp_rect[0] + 3 <= x <= self.pos_x + self.comp_rect[2] - 3 and self.pos_y + self.comp_rect[1] + 3 <= y <= self.pos_y + self.comp_rect[3] - 3:
      return True
    return False

  def initialize(self):
    self.store = [False for i in range(self.values[0])]
    self.output_stack = [[[0.0, False]] for i in range(self.values[0])]

  def calculate(self, input_datas, time):
    if input_datas[2]:
      self.store = [False for i in range(self.values[0])]
    elif (self.values[1] == 0 and not self.input_level[1] and input_datas[1]) or (self.values[1] == 1 and self.input_level[1] and not input_datas[1]): # trigger
      self.store.insert(0, input_datas[0])
      self.store.pop()
    else:
      return
    stack_with_tphl_lh(time, self.output_level, self.output_stack, self.store, self.tp_hl, self.tp_lh)