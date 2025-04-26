from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_paths, const
from ggate.const import definitions as const


from gettext import gettext as _


class OSC(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("Oscillator")
    self.comp_rect = [10, -40, 70, 0]
    self.input_pins = []
    self.output_pins = [(70, -20)]
    self.input_pins_dir = []
    self.output_pins_dir = [const.direction_W]
    self.input_level = []
    self.output_level = [False]
    self.prop_names = ["period", "shift", "duration", "initstate"]
    self.properties.append((_("Period:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(2)
    self.properties.append((_("Shift:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)
    self.properties.append((_("Duration:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(20)
    self.properties.append((_("Initial state:"), (const.property_select, _("Low level"), _("High level")), ""))
    self.values.append(0)
    self.h_period = 0.000001
    self.shift = 0.0
    self.dulation = 0.00002
    self.end_time = self.dulation + self.shift - self.h_period
    self.store = [0.0]

  def propertyChanged(self, prop):
    self.h_period = prop[0] * 0.0000005
    self.shift = prop[1] * 0.000001
    self.dulation = prop[2] * 0.000001
    self.end_time = self.dulation + self.shift - self.h_period
    return False

  def drawComponent(self, cr, layout):
    cairo_paths(cr, (15, -10), (20, -10), (20, -30), (25, -30), (25, -10), (30, -10), (30, -30), (35, -30), (35, -10), (40, -10), (40, -30), (45, -30))
    cr.stroke()
    cr.rectangle(10, -40, 40, 40)
    cr.stroke()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (50, -20), (70, -20))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
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
    if self.shift == 0.0:
      self.output_stack = [[[0.0, not self.values[3]]]]
    else:
      self.output_stack = [[[0.0, self.values[3]], [self.shift, not self.values[3]]]]
    self.store[0] = self.shift + self.h_period
    self.output_stack[0].append([self.store[0], self.values[3]])

  def calculate(self, input_datas, time):
    if time == self.store[0] and time <= self.end_time:
      self.store[0] = time + self.h_period
      self.output_stack = [[[self.store[0], not self.output_level[0]]]]