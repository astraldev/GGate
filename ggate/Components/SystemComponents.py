# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from gettext import gettext as _
from ggate import const
from ggate import Preference
from ggate.Utils import *
import math

class BaseComponent():
	def __init__(self, *args, **kwds):
		self.description = ""
		self.pos_x = 0
		self.pos_y = 0
		self.matrix = (1, 0, 0, 1)
		self.mouse_button = False
		self.properties = []
		self.values = []
		self.prop_names = []
		self.input_pins = []
		self.output_pins = []
		self.rot_input_pins = []
		self.rot_output_pins = []
		self.input_level = []
		self.output_level = []
		self.output_stack = []
		self.input_pins_dir = []
		self.output_pins_dir = []
		self.store = []

		self.scale = [1.0, 1.0]
	
	def enlarge(self, *args):
		self.scale[0] = self.scale[0] + 0.05
		self.scale[1] = self.scale[1] + 0.05
	
	def shrink(self, *args):
		self.scale[0] = self.scale[0] - 0.05
		self.scale[1] = self.scale[1] - 0.05
		
	def drawComponent(self, cr, layout):
		return

	def drawComponentEditOverlap(self, cr, layout):
		return

	def drawComponentRunOverlap(self, cr, layout):
		return

	def isMouseOvered(self, x, y):
		return False

	def mouse_down(self, x, y):
		if self.isMouseOvered(x, y):
			self.mouse_button = True

	def mouse_up(self, x, y, time):
		if self.mouse_button:
			self.mouse_button = False
			if self.isMouseOvered(x, y):
				return self.click(x, y, time)
		return False

	def set_rot_props(self):
		self.rot_comp_rect = [self.matrix[0] * self.comp_rect[0] + self.matrix[1] * self.comp_rect[1],
		                      self.matrix[2] * self.comp_rect[0] + self.matrix[3] * self.comp_rect[1],
		                      self.matrix[0] * self.comp_rect[2] + self.matrix[1] * self.comp_rect[3],
		                      self.matrix[2] * self.comp_rect[2] + self.matrix[3] * self.comp_rect[3]]
		self.rot_comp_rect = [min((self.rot_comp_rect[0], self.rot_comp_rect[2])),
		                      min((self.rot_comp_rect[1], self.rot_comp_rect[3])),
		                      max((self.rot_comp_rect[0], self.rot_comp_rect[2])),
		                      max((self.rot_comp_rect[1], self.rot_comp_rect[3]))]
		self.rot_input_pins = self.input_pins[:]
		self.rot_input_pins_dir = self.input_pins_dir[:]
		for i, p in enumerate(self.input_pins):
			self.rot_input_pins[i] = (self.matrix[0] * self.rot_input_pins[i][0] + self.matrix[1] * self.rot_input_pins[i][1],
			                          self.matrix[2] * self.rot_input_pins[i][0] + self.matrix[3] * self.rot_input_pins[i][1])
			self.rot_input_pins_dir[i] = (self.matrix[0] * self.rot_input_pins_dir[i][0] + self.matrix[1] * self.rot_input_pins_dir[i][1],
			                              self.matrix[2] * self.rot_input_pins_dir[i][0] + self.matrix[3] * self.rot_input_pins_dir[i][1])
		self.rot_output_pins = self.output_pins[:]
		self.rot_output_pins_dir = self.output_pins_dir[:]
		for i, p in enumerate(self.output_pins):
			self.rot_output_pins[i] = (self.matrix[0] * self.rot_output_pins[i][0] + self.matrix[1] * self.rot_output_pins[i][1],
			                           self.matrix[2] * self.rot_output_pins[i][0] + self.matrix[3] * self.rot_output_pins[i][1])
			self.rot_output_pins_dir[i] = (self.matrix[0] * self.rot_output_pins_dir[i][0] + self.matrix[1] * self.rot_output_pins_dir[i][1],
			                               self.matrix[2] * self.rot_output_pins_dir[i][0] + self.matrix[3] * self.rot_output_pins_dir[i][1])
										   
	def click(self, x, y, time):
		return False

	def propertyChanged(self, prop):
		return False

	def initialize(self):
		return

	def calculate(self, input_datas, time):
		return

class Probe(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("Probe")
		self.comp_rect = [10, -20, 55, 0]
		self.input_pins = [(10, -10)]
		self.output_pins = []
		self.input_pins_dir = [const.direction_E]
		self.output_pins_dir = []
		self.input_level = [False]
		self.output_level = []
		self.prop_names = ["name"]
		self.properties.append((_("Name:"), (const.property_string, 20), ""))
		self.values.append("Probe")
		self.width = 12

	def propertyChanged(self, prop):
		if prop[0] == "":
			return True
		return False

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

