# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import math
from gettext import gettext as _
from ggate import const
from ggate.Components.SystemComponents import BaseComponent
from ggate import Preference
from ggate.Utils import *

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

class SISOShiftRegister(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("SISO shift register")
		self.comp_rect = [10, -60, 120, 0]
		self.input_pins = [(10, -30), (10, -10)]
		self.output_pins = [(120, -30), (120, -10)]
		self.input_pins_dir = [const.direction_E, const.direction_E]
		self.output_pins_dir = [const.direction_W, const.direction_W]
		self.input_level = [False, False]
		self.output_level = [False, True]
		self.tp_hl = 0.0
		self.tp_lh = 0.0
		self.prop_names = ["bits", "trig", "tphl", "tplh"]
		self.properties.append((_("Number of bits:"), (const.property_int, 0, 1000, 0, 100), ""))
		self.values.append(0)
		self.properties.append((_("Trigger type:"), (const.property_select, _("Positive edge"), _("Negative edge")), ""))
		self.values.append(0)
		self.properties.append((_("Propagation delay:"), None, ""))
		self.properties.append((_("tPHL:"), (const.property_float, 0, 1000, 3, 100), "µs"))
		self.values.append(0)
		self.properties.append((_("tPLH:"), (const.property_float, 0, 1000, 3, 100), "µs"))
		self.values.append(0)
		self.store = [0]

	def propertyChanged(self, prop):
		self.tp_hl = prop[2] * 0.000001
		self.tp_lh = prop[3] * 0.000001
		return False

	def drawComponent(self, cr, layout):
		cr.rectangle(30, -60, 70, 60)
		if self.values[1] == 1:
			cr.arc(25, -10, 5, 0, 2 * math.pi)
		cairo_paths(cr, (30, -15), (40, -10), (30, -5))
		cr.stroke()
		cairo_draw_text(cr, layout, "SISO", 65, -50, 0.5, 0.5)
		cairo_draw_text(cr, layout, "D", 45, -30, 0.0, 0.5)
		cairo_draw_text(cr, layout, "CK", 45, -10, 0.0, 0.5)
		cairo_draw_text(cr, layout, "Q", 95, -30, 1.0, 0.5)
		cairo_draw_text(cr, layout, "~Q", 95, -10, 1.0, 0.5)
		cr.fill()

	def drawComponentEditOverlap(self, cr, layout):
		cairo_paths(cr, (10, -30), (30, -30))
		if self.values[1] == 0:
			cairo_paths(cr, (10, -10), (30, -10))
		else:
			cairo_paths(cr, (10, -10), (20, -10))
		cairo_paths(cr, (100, -30), (120, -30))
		cairo_paths(cr, (100, -10), (120, -10))
		cr.stroke()

	def drawComponentRunOverlap(self, cr, layout):
		if self.input_level[0]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		if self.values[1] == 0:
			cairo_paths(cr, (10, -30), (30, -30))
		else:
			cairo_paths(cr, (10, -30), (20, -30))
		cr.stroke()
		if self.input_level[1]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (10, -10), (30, -10))
		cr.stroke()
		if self.output_level[0]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (100, -30), (120, -30))
		cr.stroke()
		if self.output_level[1]:
			cr.set_source(Preference.highlevel_color)
		else:
			cr.set_source(Preference.lowlevel_color)
		cairo_paths(cr, (100, -10), (120, -10))
		cr.stroke()

	def isMouseOvered(self, x, y):
		if self.pos_x + 13 <= x <= self.pos_x + 117 and self.pos_y - 57 <= y <= self.pos_y - 3:
			return True
		return False

	def initialize(self):
		self.store[0] = 0
		self.stack = [False for i in range(self.values[0])]
		self.output_stack = [[[0.0, False]], [[0.0, True]]]

	def calculate(self, input_datas, time):
		if (self.values[1] == 0 and not self.input_level[1] and input_datas[1]) or (self.values[1] == 1 and self.input_level[1] and not input_datas[1]): # trigger
			self.stack.append(input_datas[0])
			output = self.stack.pop(0)
			output_data = [output, not output]
			stack_with_tphl_lh(time, self.output_level, self.output_stack, output_data, self.tp_hl, self.tp_lh)

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

class PIPOShiftRegister(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("PIPO shift register")
		self.comp_rect = [10, -200, 120, 0]
		self.input_pins = [(10, -170), (10, -150), (10, -130), (10, -110), (10, -90), (10, -70), (10, -50), (10, -30), (10, -10)]
		self.output_pins = [(120, -110), (120, -90), (120, -70), (120, -50)]
		self.input_pins_dir = [const.direction_E, const.direction_E, const.direction_E, const.direction_E, const.direction_E, const.direction_E, const.direction_E, const.direction_E, const.direction_E]
		self.output_pins_dir = [const.direction_W, const.direction_W, const.direction_W, const.direction_W]
		self.input_level = [False, False, False, False, False, False, False, False, False]
		self.output_level = [False, False, False, False]
		self.tp_hl = 0.0
		self.tp_lh = 0.0
		self.outpin_t = -110
		self.outpin_b = -50
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
		self.outpin_t = -60 - (prop[0] - 1) * 10
		self.outpin_b = -60 + (prop[0] - 1) * 10
		self.comp_rect = [10, min((self.outpin_t - 90, -90)), 120, max((self.outpin_b + 50, -30))]
		self.input_pins = [(10, y) for y in range(self.outpin_t - 60, self.outpin_b + 41, 20)]
		self.input_pins_dir = [const.direction_E for i in range(prop[0] + 5)]
		self.input_level = [False for i in range(prop[0] + 5)]
		self.output_pins = [(120, y) for y in range(self.outpin_t, self.outpin_b + 1, 20)]
		self.output_pins_dir = [const.direction_W for i in range(prop[0])]
		self.output_level = [False for i in range(prop[0])]
		self.tp_hl = prop[2] * 0.000001
		self.tp_lh = prop[3] * 0.000001
		return False

	def drawComponent(self, cr, layout):
		cr.rectangle(30, self.comp_rect[1], 70, self.comp_rect[3] - self.comp_rect[1])
		if self.values[1] == 1:
			cr.arc(25, self.outpin_b + 20, 5, 0, 2 * math.pi)
		cairo_paths(cr, (30, self.outpin_b + 35), (40, self.outpin_b + 40), (30, self.outpin_b + 45))
		cr.stroke()
		cairo_draw_text(cr, layout, "PIPO", 65, self.comp_rect[1] + 10, 0.5, 0.5)
		cairo_draw_text(cr, layout, "S0", 45, self.outpin_t - 60, 0.0, 0.5)
		cairo_draw_text(cr, layout, "S1", 45, self.outpin_t - 40, 0.0, 0.5)
		cairo_draw_text(cr, layout, "SR", 45, self.outpin_t - 20, 0.0, 0.5)
		for i, y in enumerate(range(self.outpin_t, self.outpin_b + 1, 20)):
			cairo_draw_text(cr, layout, "D%d" % i, 45, y, 0.0, 0.5)
			cairo_draw_text(cr, layout, "Q%d" % i, 95, y, 1.0, 0.5)
		cairo_draw_text(cr, layout, "SL", 45, self.outpin_b + 20, 0.0, 0.5)
		cairo_draw_text(cr, layout, "CK", 45, self.outpin_b + 40, 0.0, 0.5)
		cr.fill()

	def drawComponentEditOverlap(self, cr, layout):
		cairo_paths(cr, (10, self.outpin_t - 60), (30, self.outpin_t - 60))
		cairo_paths(cr, (10, self.outpin_t - 40), (30, self.outpin_t - 40))
		cairo_paths(cr, (10, self.outpin_t - 20), (30, self.outpin_t - 20))
		for i, y in enumerate(range(self.outpin_t, self.outpin_b + 1, 20)):
			cairo_paths(cr, (10, y), (30, y))
			cairo_paths(cr, (100, y), (120, y))
		cairo_paths(cr, (10, self.outpin_b + 20), (30, self.outpin_b + 20))
		if self.values[1] == 0:
			cairo_paths(cr, (10, self.outpin_b + 40), (30, self.outpin_b + 40))
		else:
			cairo_paths(cr, (10, self.outpin_b + 40), (20, self.outpin_b + 40))
		cr.stroke()

	def drawComponentRunOverlap(self, cr, layout):
		for i, y in enumerate(range(self.outpin_t - 60, self.outpin_b + 21, 20)):
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
			cairo_paths(cr, (10, self.outpin_b + 40), (30, self.outpin_b + 40))
		else:
			cairo_paths(cr, (10, self.outpin_b + 40), (20, self.outpin_b + 40))
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
		if (self.values[1] == 0 and not self.input_level[-1] and input_datas[-1]) or (self.values[1] == 1 and self.input_level[-1] and not input_datas[-1]): # trigger
			if input_datas[0] and input_datas[1]:
				self.store = input_datas[3:-2]
			elif not input_datas[0] and input_datas[1]:
				self.store.append(input_datas[-2])
				self.store.pop(0)
			elif input_datas[0] and not input_datas[1]:
				self.store.insert(0, input_datas[2])
				self.store.pop()
			else:
				return
			stack_with_tphl_lh(time, self.output_level, self.output_stack, self.store, self.tp_hl, self.tp_lh)
		else:
			return

