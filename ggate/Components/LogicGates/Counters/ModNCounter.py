from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_draw_text, cairo_paths, const, stack_with_tphl_lh
from ggate.const import definitions as const

import math
from gettext import gettext as _


class ModNCounter(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("Mod-N counter")
    self.comp_rect = [10, -80, 120, 0]
    self.input_pins = [(10, -50), (10, -30)]
    self.output_pins = [(120, -70), (120, -50), (120, -30), (120, -10)]
    self.input_pins_dir = [const.direction_E, const.direction_E]
    self.output_pins_dir = [const.direction_W, const.direction_W, const.direction_W, const.direction_W]
    self.input_level = [False, False]
    self.output_level = [False, False, False, False]
    self.tp_hl = 0.0
    self.tp_lh = 0.0
    self.outpin_t = -70
    self.outpin_b = -10
    self.prop_names = ["n", "bits", "trig", "tphl", "tplh"]
    self.properties.append((_("N:"), (const.property_int, 2, 256, 100), ""))
    self.values.append(16)
    self.properties.append((_("Number of bits:"), (const.property_int, 1, 8, 100), ""))
    self.values.append(4)
    self.properties.append((_("Trigger type:"), (const.property_select, _("Positive edge"), _("Negative edge")), ""))
    self.values.append(0)
    self.properties.append((_("Propagation delay:"), None, ""))
    self.properties.append((_("tPHL:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)
    self.properties.append((_("tPLH:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)
    self.store = [0]

  def propertyChanged(self, prop):
    if prop[0] > 2 ** prop[1]:
      return True
    self.outpin_t = -40 - (prop[1] - 1) * 10
    self.outpin_b = -40 + (prop[1] - 1) * 10
    self.comp_rect = [10, min((self.outpin_t - 10, -60)), 120, max((self.outpin_b + 10, -20))]
    self.output_pins = [(120, y) for y in range(self.outpin_t, self.outpin_b + 1, 20)]
    self.output_pins_dir = [const.direction_W for i in range(prop[1])]
    self.output_level = [False for i in range(prop[1])]
    self.tp_hl = prop[3] * 0.000001
    self.tp_lh = prop[4] * 0.000001
    return False

  def drawComponent(self, cr, layout):
    cr.rectangle(30, self.comp_rect[1], 70, self.comp_rect[3] - self.comp_rect[1])
    if self.values[2] == 1:
      cr.arc(25, -50, 5, 0, 2 * math.pi)
    cairo_paths(cr, (30, -55), (40, -50), (30, -45))
    cr.stroke()
    cairo_draw_text(cr, layout, "CK", 45, -50, 0.0, 0.5)
    cairo_draw_text(cr, layout, "RST", 45, -30, 0.0, 0.5)
    for i, y in enumerate(range(self.outpin_t, self.outpin_b + 1, 20)):
      cairo_draw_text(cr, layout, "Q%d" % i, 95, y, 1.0, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    if self.values[2] == 0:
      cairo_paths(cr, (10, -50), (30, -50))
    else:
      cairo_paths(cr, (10, -50), (20, -50))
    cairo_paths(cr, (10, -30), (30, -30))
    for i, y in enumerate(range(self.outpin_t, self.outpin_b + 1, 20)):
      cairo_paths(cr, (100, y), (120, y))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if self.values[2] == 0:
      cairo_paths(cr, (10, -50), (30, -50))
    else:
      cairo_paths(cr, (10, -50), (20, -50))
    cr.stroke()
    if self.input_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -30), (30, -30))
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
    self.store[0] = 0
    self.output_stack = [[[0.0, False]] for i in range(self.values[1])]

  def calculate(self, input_datas, time):
    if input_datas[1]:
      output_data = [False for i in range(self.values[1])]
      self.store[0] = 0
    elif (self.values[2] == 0 and not self.input_level[0] and input_datas[0]) or (self.values[2] == 1 and self.input_level[0] and not input_datas[0]): # trigger
      self.store[0] += 1
      if self.store[0] == self.values[0]:
        self.store[0] = 0
      output_data = [self.store[0] >> i & 0x01 for i in reversed(range(self.values[1]))]
    else:
      return
    stack_with_tphl_lh(time, self.output_level, self.output_stack, output_data, self.tp_hl, self.tp_lh)