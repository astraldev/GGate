from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_paths
from ggate.const import definitions
from gettext import gettext as _
import math


class LED(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("LED")
    self.comp_rect = [10, -40, 70, 0]
    self.input_pins = [(10, -20)]
    self.output_pins = []
    self.input_pins_dir = [definitions.direction_E]
    self.output_pins_dir = []
    self.input_level = [False]
    self.output_level = []

    self.prop_names = ['_red', '_blue', '_green', '_yellow']
    self.properties.append((_("Color of LED :"), None, ''))
    self.properties.append((_("Color :"), (definitions.property_select, _('Red'), _('Blue'), _('Green'), _('Yellow')), ''))
    self.values.append(2)

  def drawComponent(self, cr, layout):
    cr.arc(50, -20, 8, 0, 2 * math.pi)
    cr.rectangle(30, -40, 40, 40)
    cr.stroke()


  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (10, -20), (30, -20))
    cr.stroke()


  def drawComponentRunOverlap(self, cr, layout):
    color = self.prop_names[self.values[0]]
    high_color = Preference[color] if self.prop_names[self.values[0]] is not None else Preference['_green']

    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
      cairo_paths(cr, (10, -20), (30, -20))
      cr.stroke()
      cr.set_source(high_color)
      cr.arc(50, -20, 8, 0, 2 * math.pi)

    else:
      cr.set_source(Preference.lowlevel_color)
      cairo_paths(cr, (10, -20), (30, -20))
      cr.stroke()
      cr.set_source_rgb(0.0, 0.25, 0.0)
      cr.arc(50, -20, 8, 0, 2 * math.pi)

    cr.fill()


  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 67 and self.pos_y - 37 <= y <= self.pos_y - 3:
      return True
    return False