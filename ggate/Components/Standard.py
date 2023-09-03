# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import math
from gettext import gettext as _
from ggate import const
from ggate.Components.SystemComponents import BaseComponent
from ggate import Preference
from ggate.Utils import *

class NOT(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("NOT")
		self.comp_rect = [10, -40, 90, 0]
		self.input_pins = [(10, -20)]
		self.output_pins = [(90, -20)]
		self.input_pins_dir = [const.direction_E]
		self.output_pins_dir = [const.direction_W]
		self.input_level = [False]
		self.output_level = [True]
		self.tp_hl = 0.0
		self.tp_lh = 0.0
		self.prop_names = ["tphl", "tplh"]
		self.properties.append((_("Propagation delay:"), None, ""))
		self.properties.append((_("tPHL:"), (const.property_float, 0, 1000, 3, 100), "µs"))
		self.values.append(0)
		self.properties.append((_("tPLH:"), (const.property_float, 0, 1000, 3, 100), "µs"))
		self.values.append(0)

	def propertyChanged(self, prop):
		self.tp_hl = prop[0] * 0.000001
		self.tp_lh = prop[1] * 0.000001
		return False

	def drawComponent(self, cr, layout):
		if Preference.symbol_type == 0:
			cairo_paths(cr, (30, -35), (30, -5), (60, -20))
		elif Preference.symbol_type == 1:
			cr.rectangle(30, -40, 30, 40)
		cr.close_path()
		cr.stroke()
		cr.arc(66, - 20, 6, 0, 2 * math.pi)
		cr.stroke()
		if Preference.symbol_type == 1:
			cairo_draw_text(cr, layout, "1", 45, -40, 0.5, 0.0)
			cr.fill()
		

	def drawComponentEditOverlap(self, cr, layout):
		cairo_paths(cr, (10, -20), (30, -20))
		cairo_paths(cr, (72, -20), (90, -20))
		cr.stroke()


	def drawComponentRunOverlap(self, cr, layout):
		if self.input_level[0]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (10, -20), (30, -20))
		cr.stroke()
		if self.output_level[0]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (72, -20), (90, -20))
		cr.stroke()



	def isMouseOvered(self, x, y):
		if self.pos_x + 13 <= x <= self.pos_x + 87 and self.pos_y - 37 <= y <= self.pos_y - 3:
			return True
		return False

	def calculate(self, input_datas, time):
		new_output = not input_datas[0]
		if new_output != self.output_level[0]:
			if self.output_level[0]:
				self.output_stack = [[[time + self.tp_hl, new_output]]]
			else:
				self.output_stack = [[[time + self.tp_lh, new_output]]]
		else:
			self.output_stack = [[]]

class AND(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("AND")
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
			cairo_paths(cr, (60, 0), (30, 0), (30, -40), (60, -40))
			cr.arc(60, -20, 20, -0.5 * math.pi, 0.5 * math.pi)
			cr.stroke()

		elif Preference.symbol_type == 1:
			cr.rectangle(30, -40, 50, 40)
			cr.stroke()
			cairo_draw_text(cr, layout, "&", 55, -40, 0.5, 0.0)
			cr.fill()
		


	def drawComponentEditOverlap(self, cr, layout):
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
		cairo_paths(cr, (10, -30), (30, -30))
		cr.stroke()
		if self.input_level[1]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (10, -10), (30, -10))
		cr.stroke()
		if self.values[0] == 3:
			if self.input_level[2]:
				cr.set_source(Preference.highlevel_color)
			else:
				cr.set_source(Preference.lowlevel_color)
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
		new_output = input_datas[0] and input_datas[1] if self.values[0] == 2 else input_datas[0] and input_datas[1] and input_datas[2]
		if new_output != self.output_level[0]:
			if self.output_level[0]:
				self.output_stack = [[[time + self.tp_hl, new_output]]]
			else:
				self.output_stack = [[[time + self.tp_lh, new_output]]]
		else:
			self.output_stack = [[]]

class OR(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("OR")
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
			cairo_bezier(cr, 30, -40, 50, -40, 65, -40, 80, -20)
			cairo_bezier(cr, 30, 0, 50, 0, 65, 0, 80, -20)

			cr.stroke()
			


		elif Preference.symbol_type == 1:
			cr.rectangle(30, -40, 50, 40)
			cr.stroke()
			

			cairo_draw_text(cr, layout, "≥1", 55, -40, 0.5, 0.0)
			cr.fill()

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
		new_output = input_datas[0] or input_datas[1] if self.values[0] == 2 else input_datas[0] or input_datas[1] or input_datas[2]
		if new_output != self.output_level[0]:
			if self.output_level[0]:
				self.output_stack = [[[time + self.tp_hl, new_output]]]
			else:
				self.output_stack = [[[time + self.tp_lh, new_output]]]
		else:
			self.output_stack = [[]]

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
		new_output = (input_datas[0] + input_datas[1]) % 2 if self.values[0] == 2 else (input_datas[0] + input_datas[1] + input_datas[2]) % 2
		if new_output != self.output_level[0]:
			if self.output_level[0]:
				self.output_stack = [[[time + self.tp_hl, new_output]]]
			else:
				self.output_stack = [[[time + self.tp_lh, new_output]]]
		else:
			self.output_stack = [[]]

class NAND(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("NAND")
		self.comp_rect = [10, -40, 110, 0]
		self.input_pins = [(10, -30), (10, -10)]
		self.output_pins = [(110, -20)]
		self.input_pins_dir = [const.direction_E, const.direction_E]
		self.output_pins_dir = [const.direction_W]
		self.input_level = [False, False]
		self.output_level = [True]
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
			cairo_paths(cr, (60, 0), (30, 0), (30, -40), (60, -40))
			cr.arc(60, -20, 20, -0.5 * math.pi, 0.5 * math.pi)
			cr.stroke()
			cr.arc(86, -20, 6, 0, 2 * math.pi)
			cr.stroke()
		elif Preference.symbol_type == 1:
			cr.rectangle(30, -40, 50, 40)
			cr.stroke()
			cairo_paths(cr, (80, -28), (92, -20))
			cr.stroke()
			cairo_draw_text(cr, layout, "&", 55, -40, 0.5, 0.0)
			cr.fill()

	def drawComponentEditOverlap(self, cr, layout):
		cairo_paths(cr, (10, -30), (30, -30))
		if self.values[0] == 3:
			cairo_paths(cr, (10, -20), (30, -20))
		cairo_paths(cr, (10, -10), (30, -10))
		cairo_paths(cr, (92, -20), (110, -20))
		cr.stroke()

	def drawComponentRunOverlap(self, cr, layout):
		if self.input_level[0]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (10, -30), (30, -30))
		cr.stroke()
		if self.input_level[1]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (10, -10), (30, -10))
		cr.stroke()
		if self.values[0] == 3:
			if self.input_level[2]:
				cr.set_source(Preference.highlevel_color)
			else:
				cr.set_source(Preference.lowlevel_color)
			cairo_paths(cr, (10, -20), (30, -20))
			cr.stroke()
		if self.output_level[0]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (92, -20), (110, -20))
		cr.stroke()

	def isMouseOvered(self, x, y):
		if self.pos_x + 13 <= x <= self.pos_x + 107 and self.pos_y - 37 <= y <= self.pos_y - 3:
			return True
		return False

	def calculate(self, input_datas, time):
		new_output = not (input_datas[0] and input_datas[1]) if self.values[0] == 2 else not (input_datas[0] and input_datas[1] and input_datas[2])
		if new_output != self.output_level[0]:
			if self.output_level[0]:
				self.output_stack = [[[time + self.tp_hl, new_output]]]
			else:
				self.output_stack = [[[time + self.tp_lh, new_output]]]
		else:
			self.output_stack = [[]]

class NOR(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("NOR")
		self.comp_rect = [10, -40, 110, 0]
		self.input_pins = [(10, -30), (10, -10)]
		self.output_pins = [(110, -20)]
		self.input_pins_dir = [const.direction_E, const.direction_E]
		self.output_pins_dir = [const.direction_W]
		self.input_level = [False, False]
		self.output_level = [True]
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
			cairo_bezier(cr, 30, -40, 50, -40, 65, -40, 80, -20)
			cairo_bezier(cr, 30, 0, 50, 0, 65, 0, 80, -20)
			cr.stroke()
			cr.arc(86, -20, 6, 0, 2 * math.pi)
			cr.stroke()
		elif Preference.symbol_type == 1:
			cr.rectangle(30, -40, 50, 40)
			cr.stroke()
			cairo_paths(cr, (80, -28), (92, -20))
			cr.stroke()
			cairo_draw_text(cr, layout, "≥1", 55, -40, 0.5, 0.0)
			cr.fill()

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
		cairo_paths(cr, (92, -20), (110, -20))
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
		cairo_paths(cr, (92, -20), (110, -20))
		cr.stroke()

	def isMouseOvered(self, x, y):
		if self.pos_x + 13 <= x <= self.pos_x + 107 and self.pos_y - 37 <= y <= self.pos_y - 3:
			return True
		return False

	def calculate(self, input_datas, time):
		new_output = not (input_datas[0] or input_datas[1]) if self.values[0] == 2 else not (input_datas[0] or input_datas[1] or input_datas[2])
		if new_output != self.output_level[0]:
			if self.output_level[0]:
				self.output_stack = [[[time + self.tp_hl, new_output]]]
			else:
				self.output_stack = [[[time + self.tp_lh, new_output]]]
		else:
			self.output_stack = [[]]

class SW(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("Switch")
		self.comp_rect = [10, -40, 70, 0]
		self.input_pins = []
		self.output_pins = [(70, -20)]
		self.input_pins_dir = []
		self.output_pins_dir = [const.direction_W]
		self.output_stack = [[]]
		self.input_level = []
		self.output_level = [False]
		self.output_store = [[]]
		self.prop_names = ["initstate"]
		self.properties.append((_("Initial state:"), (const.property_select, _("Low level"), _("High level")), ""))
		self.values.append(0)
		self.store = [False]

	def drawComponent(self, cr, layout):
		cr.rectangle(10, -40, 40, 40)
		cr.rectangle(15, -30, 30, 10)
		cr.stroke()
		cairo_draw_text(cr, layout, "L", 20, -10, 0.5, 0.5)
		cairo_draw_text(cr, layout, "H", 40, -10, 0.5, 0.5)
		cr.fill()

	def drawComponentEditOverlap(self, cr, layout):
		cairo_paths(cr, (50, -20), (70, -20))
		cr.rectangle(17, -28, 12, 6)
		cr.stroke()

	def drawComponentRunOverlap(self, cr, layout):
		if self.store[0]:
			cr.rectangle(30.5, -28.5, 13, 7)
		else:
			cr.rectangle(16.5, -28.5, 13, 7)
		cr.fill()
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
		self.clicked_time = 0.0
		self.store[0] = self.values[0]
		
	def click(self, x, y, time):
		self.store[0] = not self.store[0]
		self.clicked_time = time
		return True

	def calculate(self, input_datas, time):
		self.output_stack = [[[self.clicked_time, self.store[0]]]]

class VDD(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("Vdd rail")
		self.comp_rect = [10, -40, 30, 0]
		self.input_pins = []
		self.output_pins = [(20, 0)]
		self.input_pins_dir = []
		self.output_pins_dir = [const.direction_N]
		self.input_level = []
		self.output_level = [True]
		self.output_stack = [[]]

	def drawComponent(self, cr, layout):
		cairo_paths(cr, (10, -20), (30, -20))
		cr.rectangle(19, -21, 2, 2)
		cr.stroke()
		cairo_draw_text(cr, layout, "Vdd", 20, -30, 0.5, 0.5)
		cr.fill()

	def drawComponentEditOverlap(self, cr, layout):
		cairo_paths(cr, (20, -20), (20, 0))
		cr.stroke()

	def drawComponentRunOverlap(self, cr, layout):
		cr.set_source(Preference.highlevel_color)
		cairo_paths(cr, (20, -20), (20, 0))
		cr.stroke()

	def isMouseOvered(self, x, y):
		if self.pos_x + 13 <= x <= self.pos_x + 27 and self.pos_y - 37 <= y <= self.pos_y - 3:
			return True
		return False

class GND(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("GND rail")
		self.comp_rect = [10, -50, 30, 0]
		self.input_pins = []
		self.output_pins = [(20, -50)]
		self.input_pins_dir = []
		self.output_pins_dir = [const.direction_S]
		self.input_level = []
		self.output_level = [False]
		self.output_stack = [[]]

	def drawComponent(self, cr, layout):
		cairo_paths(cr, (10, -30), (30, -30))
		cairo_paths(cr, (16, -30), (12, -20))
		cairo_paths(cr, (22, -30), (18, -20))
		cairo_paths(cr, (28, -30), (24, -20))
		cr.stroke()
		cairo_draw_text(cr, layout, "GND", 20, -10, 0.5, 0.5)
		cr.fill()

	def drawComponentEditOverlap(self, cr, layout):
		cairo_paths(cr, (20, -50), (20, -30))
		cr.stroke()

	def drawComponentRunOverlap(self, cr, layout):
		cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (20, -50), (20, -30))
		cr.stroke()

	def isMouseOvered(self, x, y):
		if self.pos_x + 13 <= x <= self.pos_x + 27 and self.pos_y - 47 <= y <= self.pos_y - 3:
			return True
		return False

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


class TriStateBuffer(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("TriStateBuffer")
		self.comp_rect = [10, -40, 90, 0]

		self.input_pins = [(10, -20), (40, -60)]
		self.output_pins = [(80, -20)]
		self.input_pins_dir = [const.direction_E, const.direction_N]
		self.output_pins_dir = [const.direction_W]
		self.input_level = [False, False]
		self.output_level = [False]

		self.inverted = False
		self.active_high = True

		self.prop_names = ['active', 'inverted']
		self.properties.append((_("Active :"), (const.property_select, _("Low"), _("High")), ""))
		self.values.append(1)
		self.properties.append((_("Inverted :"), (const.property_select, _("True"), _("False")), ""))
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
