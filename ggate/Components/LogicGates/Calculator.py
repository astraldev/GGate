# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from gettext import gettext as _
from ggate import Preference
from ggate.const import definitions as const
from ggate.Utils import cairo_draw_text, cairo_paths, stack_with_tphl_lh
from .SystemComponents import BaseComponent

class Adder(BaseComponent):
  def __init__(self, *args, **kwds):
    BaseComponent.__init__(self, *args, **kwds)
    self.description = _("Adder")
    self.comp_rect = [10, -60, 100, 0]
    self.input_pins = [(10, -50), (10, -30), (10, -10)]
    self.output_pins = [(100, -50), (100, -10)]
    self.input_pins_dir = [const.direction_E, const.direction_E, const.direction_E]
    self.output_pins_dir = [const.direction_W, const.direction_W]
    self.input_level = [False, False, False]
    self.output_level = [False, False]
    self.output_stack = [[], []]
    self.tp_hl = 0.0
    self.tp_lh = 0.0
    self.prop_names = ["halffull", "tphl", "tplh"]
    self.properties.append((_("Half/Full:"), (const.property_select, _("Half adder"), _("Full adder")), ""))
    self.values.append(1)
    self.properties.append((_("Propagation delay:"), None, ""))
    self.properties.append((_("tPHL:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)
    self.properties.append((_("tPLH:"), (const.property_float, 0, 1000, 3, 100), "µs"))
    self.values.append(0)

  def propertyChanged(self, prop):
    self.tp_hl = prop[1] * 0.000001
    self.tp_lh = prop[2] * 0.000001
    if prop[0] == 0:
      self.comp_rect = [10, -40, 100, 0]
      self.input_pins = [(10, -30), (10, -10)]
      self.output_pins = [(100, -30), (100, -10)]
      self.input_pins_dir = [const.direction_E, const.direction_E]
      self.input_level = [False, False]
    else:
      self.comp_rect = [10, -60, 100, 0]
      self.input_pins = [(10, -50), (10, -30), (10, -10)]
      self.output_pins = [(100, -50), (100, -10)]
      self.input_pins_dir = [const.direction_E, const.direction_E, const.direction_E]
      self.input_level = [False, False, False]
    return False

  def drawComponent(self, cr, layout):
    if self.values[0] == 0:
      cr.rectangle(30, -40, 50, 40)
      cr.stroke()
      cairo_draw_text(cr, layout, "X", 35, -30, 0.0, 0.5)
      cairo_draw_text(cr, layout, "Y", 35, -10, 0.0, 0.5)
      cairo_draw_text(cr, layout, "C", 75, -30, 1.0, 0.5)
    else:
      cr.rectangle(30, -60, 50, 60)
      cr.stroke()
      cairo_draw_text(cr, layout, "X", 35, -50, 0.0, 0.5)
      cairo_draw_text(cr, layout, "Y", 35, -30, 0.0, 0.5)
      cairo_draw_text(cr, layout, "Z", 35, -10, 0.0, 0.5)
      cairo_draw_text(cr, layout, "C", 75, -50, 1.0, 0.5)
    cairo_draw_text(cr, layout, "S", 75, -10, 1.0, 0.5)
    cr.fill()

  def drawComponentEditOverlap(self, cr, layout):
    if self.values[0] == 0:
      cairo_paths(cr, (10, -30), (30, -30))
      cairo_paths(cr, (80, -30), (100, -30))
    else:
      cairo_paths(cr, (10, -50), (30, -50))
      cairo_paths(cr, (10, -30), (30, -30))
      cairo_paths(cr, (80, -50), (100, -50))
    cairo_paths(cr, (10, -10), (30, -10))
    cairo_paths(cr, (80, -10), (100, -10))
    cr.stroke()

  def drawComponentRunOverlap(self, cr, layout):
    if self.input_level[0]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if self.values[0] == 0:
      cairo_paths(cr, (10, -30), (30, -30))
    else:
      cairo_paths(cr, (10, -50), (30, -50))
    cr.stroke()
    if self.input_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    if self.values[0] == 0:
      cairo_paths(cr, (10, -10), (30, -10))
    else:
      cairo_paths(cr, (10, -30), (30, -30))
    cr.stroke()
    if self.values[0] == 1:
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
    if self.values[0] == 0:
      cairo_paths(cr, (80, -30), (100, -30))
    else:
      cairo_paths(cr, (80, -50), (100, -50))
    cr.stroke()
    if self.output_level[1]:
      cr.set_source(Preference.highlevel_color)
    else:
      cr.set_source(Preference.lowlevel_color)
    cairo_paths(cr, (80, -10), (100, -10))
    cr.stroke()

  def isMouseOvered(self, x, y):
    if self.values[0] == 0:
      if self.pos_x + 13 <= x <= self.pos_x + 97 and self.pos_y - 37 <= y <= self.pos_y - 3:
        return True
    else:
      if self.pos_x + 13 <= x <= self.pos_x + 97 and self.pos_y - 57 <= y <= self.pos_y - 3:
        return True
    return False

  def calculate(self, input_datas, time):
    r = 1 if input_datas[0] else 0
    r += 1 if input_datas[1] else 0
    if self.values[0] == 1:
      r += 1 if input_datas[2] else 0
    if r == 0:
      output_data = [False, False]
    elif r == 1:
      output_data = [False, True]
    elif r == 2:
      output_data = [True, False]
    else:
      output_data = [True, True]
    stack_with_tphl_lh(time, self.output_level, self.output_stack, output_data, self.tp_hl, self.tp_lh)

