from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_paths
from ggate.const import definitions


import math
from gettext import gettext as _


class TSB(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("TriStateBuffer")
    self.comp_rect = [10, -40, 90, 0]

    self.input_pins = [(10, -20), (40, -60)]
    self.output_pins = [(80, -20)]
    self.input_pins_dir = [definitions.direction_E, definitions.direction_N]
    self.output_pins_dir = [definitions.direction_W]
    self.input_level = [False, False]
    self.output_level = [False]

    self.inverted = False
    self.active_high = True

    self.prop_names = ['active', 'inverted']
    self.properties.append((_("Active :"), (definitions.property_select, _("Low"), _("High")), ""))
    self.values.append(1)
    self.properties.append((_("Inverted :"), (definitions.property_select, _("True"), _("False")), ""))
    self.values.append(1)

  def propertyChanged(self, prop):

    self.inverted = True if prop[1] == 0 else False
    self.active_high = True if prop[0] == 1 else False
    return False

  def drawComponent(self, cr, layout):
    if Preference.symbol_type == 0:
      cairo_paths(cr, (30, -35), (30, -5), (60, -20))

    cr.close_path()
    cr.stroke()

    if not self.active_high:
      cr.arc(40, -35, 4, 0, 2 * math.pi)

    cr.stroke()

    if self.inverted:
      cr.arc(64, -20, 4, 0, 2 * math.pi)

    cr.stroke()

  def drawComponentEditOverlap(self, cr, layout):
    cairo_paths(cr, (10, -20), (30, -20))

    if self.inverted:
      cairo_paths(cr, (68, -20), (80, -20))
    else:
      cairo_paths(cr, (58, -20), (80, -20))

    cr.stroke()

    if not self.active_high:
      cairo_paths(cr, (40, -60), (40, -38))
    else:
      cairo_paths(cr, (40, -60), (40, -30))

    cr.stroke()


  def drawComponentRunOverlap(self, cr, layout):
    # Proper state for tribuff
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (10, -20), (30, -20))
    cr.stroke()

    if self.input_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if not self.active_high:
      cairo_paths(cr, (40, -60), (40, -38))
    else:
      cairo_paths(cr, (40, -60), (40, -30))
    cr.stroke()

    if self.output_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if self.inverted:
      cairo_paths(cr, (68, -20), (80, -20))
    else:
      cairo_paths(cr, (58, -20), (80, -20))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 87 and self.pos_y - 37 <= y <= self.pos_y - 3:
      return True
    return False

  def calculate(self, input_datas, time):

    new_output = False

    if input_datas[0] and input_datas[1] and self.active_high and (not self.inverted):
      new_output = True

    if (not input_datas[0]) and input_datas[1] and (self.active_high and self.inverted):
      new_output = True

    if input_datas[0] and (not input_datas[1]) and (not self.active_high) and (not self.inverted):
      new_output = True

    if not input_datas[1] and not input_datas[1] and (not self.active_high) and self.inverted:
      new_output = True

    if new_output != self.output_level[0]:
      if self.output_level[0]:
        self.output_stack = [[[time, new_output]]]
      else:
        self.output_stack = [[[time, new_output]]]
    else:
      self.output_stack = [[]]