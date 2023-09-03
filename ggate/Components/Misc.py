# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import math
from gettext import gettext as _
from ggate import const
from ggate.Components.SystemComponents import BaseComponent
from ggate.Utils import *
from gi.repository import Pango

class Text(BaseComponent):
	def __init__(self, *args, **kwds):
		BaseComponent.__init__(self, *args, **kwds)
		self.description = _("Text")
		self.comp_rect = [10, -12, 24, 0]
		self.prop_names = ["text"]
		self.properties.append((_("Text:"), (const.property_string, 20), ""))
		self.values.append("Text")
		self.width = 12
		self.height = 12

	def propertyChanged(self, prop):
		if prop[0] == "":
			return True
		return False

	def drawComponent(self, cr, layout):
		cairo_draw_text(cr, layout, self.values[0], 10, -10, 0.0, 0.5)
		cr.fill()
		(w, h) = layout.get_size()
		self.width = w / Pango.SCALE
		if self.width < 12:
			self.width = 12
		self.height = h / Pango.SCALE
		if self.height < 12:
			self.height = 12
		self.comp_rect = [10, -10-self.height/2, 10+self.width, -10+self.height/2]
		self.set_rot_props()

	def isMouseOvered(self, x, y):
		if self.pos_x + 10 <= x <= self.pos_x + self.width + 10 and self.pos_y - 10 - self.height / 2 <= y <= self.pos_y - 10 + self.height / 2:
			return True
		return False
