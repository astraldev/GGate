from ggate import Preference
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Utils import cairo_bezier, cairo_draw_text, cairo_paths, const
from ggate.const import definitions as const


from gettext import gettext as _


class XOR(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("XOR")
    self.comp_rect = [10, -40, 100, 0]
    self.input_pins = [(10, -30), (10, -10)]
    self.output_pins = [(100, -20)]
    self.input_pins_dir = [const.direction_E, const.direction_E]
    self.output_pins_dir = [const.direction_W]
    self.input_level = [False, False]
    self.output_level = [False]
    self.tp_hl = 0.0
    self.tp_lh = 0.0
    self.prop_names = ["inputs", "tphl", "tplh"]
    self.properties.append((_("Input pins:"), (const.property_float, 2, 3, 0, 100), ""))
    self.values.append(2)
    self.properties.append((_("Propagation delay:"), None, ""))
    self.properties.append((_("tPHL:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)
    self.properties.append((_("tPLH:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)

  def propertyChanged(self, prop):
    self.input_pins_dir = [const.direction_E, const.direction_E]
    self.input_level = [False, False]
    self.input_pins = [(10, -30), (10, -10)]
    if prop[0] == 3:
      self.input_pins_dir.append(const.direction_E)
      self.input_level.append(False)
      self.input_pins.append((10, -20))
    self.tp_hl = prop[1] * 0.000001
    self.tp_lh = prop[2] * 0.000001
    return False

  def drawComponent(self, cr, layout):
    if Preference.symbol_type == 0:
      cairo_bezier(cr, 30, -40, 40, -30, 40, -10, 30, 0)
      cairo_bezier(cr, 25, -40, 35, -30, 35, -10, 25, 0)
      cairo_bezier(cr, 30, -40, 50, -40, 65, -40, 80, -20)
      cairo_bezier(cr, 30, 0, 50, 0, 65, 0, 80, -20)
    elif Preference.symbol_type == 1:
      cr.rectangle(30, -40, 50, 40)
      cr.stroke()
      cairo_draw_text(cr, layout, "=1", 55, -40, 0.5, 0.0)
      cr.fill()
    cr.stroke()

  def drawComponentEditOverlap(self, cr, layout):
    if Preference.symbol_type == 0:
      cairo_paths(cr, (10, -30), (36, -30))
      if self.values[0] == 3:
        cairo_paths(cr, (10, -20), (37, -20))
      cairo_paths(cr, (10, -10), (36, -10))
    elif Preference.symbol_type == 1:
      cairo_paths(cr, (10, -30), (30, -30))
      if self.values[0] == 3:
        cairo_paths(cr, (10, -20), (30, -20))
      cairo_paths(cr, (10, -10), (30, -10))
    cairo_paths(cr, (80, -20), (100, -20))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if Preference.symbol_type == 0:
      cairo_paths(cr, (10, -30), (36, -30))
    elif Preference.symbol_type == 1:
      cairo_paths(cr, (10, -30), (30, -30))
    cr.stroke()
    if self.input_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if Preference.symbol_type == 0:
      cairo_paths(cr, (10, -10), (36, -10))
    elif Preference.symbol_type == 1:
      cairo_paths(cr, (10, -10), (30, -10))
    cr.stroke()
    if self.values[0] == 3:
      if self.input_level[2]:
        cr.set_source(Preference.highlevel_color)
      else:
        cr.set_source(Preference.lowlevel_color)
      if Preference.symbol_type == 0:
        cairo_paths(cr, (10, -20), (37, -20))
      elif Preference.symbol_type == 1:
        cairo_paths(cr, (10, -20), (30, -20))
      cr.stroke()
    if self.output_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (80, -20), (100, -20))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.pos_x + 13 <= x <= self.pos_x + 97 and self.pos_y - 37 <= y <= self.pos_y - 3:
      return True
    return False

  def calculate(self, input_datas, time):
    print(input_datas)
    new_output = (input_datas[0] + input_datas[1]) % 2 if self.values[0] == 2 else (input_datas[0] + input_datas[1] + input_datas[2]) % 2
    if new_output != self.output_level[0]:
      if self.output_level[0]:
        self.output_stack = [[[time + self.tp_hl, new_output]]]
      else:
        self.output_stack = [[[time + self.tp_lh, new_output]]]
    else:
      self.output_stack = [[]]