from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent, PropertyError
from ggate.Utils import cairo_draw_text, cairo_paths
from ggate.const import definitions
from gi.repository import Pango
from gettext import gettext as _

import math


class Probe(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("Probe")
    self.comp_rect = [10, -20, 55, 0]
    self.input_pins = [(10, -10)]
    self.output_pins = []
    self.input_pins_dir = [definitions.direction_E]
    self.output_pins_dir = []
    self.input_level = [False]
    self.output_level = []
    self.prop_names = ["name"]
    self.properties.append((_("Name:"), (definitions.property_string, 20), ""))
    self.values.append("Probe")
    self.width = 12

  def propertyChanged(self, prop):
    return PropertyError("Name cannot be empty.", [0]) if prop[0] == "" else False

  def drawComponent(self, cr, layout):
    cr.arc(40, -10, 10, 0, 2 * math.pi)
    cr.stroke()
    cairo_draw_text(cr, layout, "V", 40, -10, 0.5, 0.5)
    cairo_draw_text(cr, layout, self.values[0], 55, -10, 0.0, 0.5)
    (w, h) = layout.get_size()
    self.width = w / Pango.SCALE
    if self.width < 12:
      self.width = 12
    self.comp_rect = [10, -20, 55 + self.width, 0]
    self.set_rot_props()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (10, -10), (30, -10))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -10), (30, -10))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 52 + self.width and self.pos_y - 17 <= y <= self.pos_y - 3:
      return True
    return False