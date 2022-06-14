# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import cairo, sys
from gi.repository import Pango

class _Preference:
	def __setattr__(self, name, value):
		import cairo
		from gi.repository import Pango
		if isinstance(self.pref_dict[name], Pango.FontDescription):
			self.pref_dict[name] = Pango.FontDescription(value)
		elif isinstance(self.pref_dict[name], cairo.Pattern):
			try:
				rgb = value.split(",")
				self.pref_dict[name] = cairo.SolidPattern(float(rgb[0]), float(rgb[1]), float(rgb[2]))
			except ValueError:
				self.pref_dict[name] = cairo.SolidPattern(0.0, 0.0, 0.0)
		elif isinstance(self.pref_dict[name], int):
			self.pref_dict[name] = int(value)
		elif isinstance(self.pref_dict[name], float):
			self.pref_dict[name] = float(value)

	def __getattr__(self, name):
		return self.pref_dict[name]

	pref_dict = {
		"drawing_font": Pango.FontDescription("Liberation Mono 10"),
		"net_color": cairo.SolidPattern(0.0, 0.0, 1.0),
		"net_high_color": cairo.SolidPattern(0.5, 0.5, 1.0),
		"net_color_running": cairo.SolidPattern(0.0, 0.0, 0.0),
		"component_color": cairo.SolidPattern(0.0, 1.0, 0.0),
		"component_high_color": cairo.SolidPattern(0.5, 1.0, 0.5),
		"component_color_running": cairo.SolidPattern(0.0, 0.0, 0.0),
		"selected_color": cairo.SolidPattern(1.0, 1.0, 1.0),
		"cursor_color": cairo.SolidPattern(1.0, 1.0, 1.0),
		"terminal_color": cairo.SolidPattern(1.0, 0.0, 0.0),
		"preadd_color": cairo.SolidPattern(1.0, 0.75, 0.0),
		"picked_color": cairo.SolidPattern(1.0, 0.5, 0.0),
		"terminal_color_running": cairo.SolidPattern(0.0, 0.0, 0.0),
		"highlevel_color": cairo.SolidPattern(1.0, 0.0, 0.0),
		"lowlevel_color": cairo.SolidPattern(0.0, 0.0, 1.0),
		"bg_color": cairo.SolidPattern(0.0, 0.0, 0.0),
		"bg_color_running": cairo.SolidPattern(1.0, 1.0, 1.0),
		"grid_color": cairo.SolidPattern(0.25, 0.22, 0.25),
		"symbol_type": 0, #  0: MIL/ANSI  1: IEC
		"max_calc_iters": 10000,
		"max_calc_duration": 0.0002
	}

	def load_settings(self):
		import os
		from glogic import const
		try:
			fp = open(os.path.join(const.config_path, "preferences"), mode="r", encoding="utf-8")
		except TypeError:
			import codecs
			fp = codecs.open(os.path.join(const.config_path, "preferences"), mode="r", encoding="utf-8")
		except IOError:
			return
		for l in fp:
			pref = l.split("=")
			if len(pref) != 2:
				continue
			if pref[0] in self.pref_dict:
				self.__setattr__(pref[0], pref[1])

	def save_settings(self):
		import cairo, os
		from glogic import const
		from gi.repository import Pango
		try:
			if not os.path.isdir(const.config_path):
				os.makedirs(const.config_path)
			fp = open(os.path.join(const.config_path, "preferences"), mode="w", encoding="utf-8")
		except IOError:
			return
		for key in self.pref_dict:
			if isinstance(self.pref_dict[key], Pango.FontDescription):
				fp.write("%s=%s\n" % (key, self.pref_dict[key].to_string()))
			elif isinstance(self.pref_dict[key], cairo.Pattern):
				rgba = self.pref_dict[key].get_rgba()
				fp.write("%s=%f,%f,%f\n" % (key, rgba[0], rgba[1], rgba[2]))
			elif isinstance(self.pref_dict[key], int):
				fp.write("%s=%d\n" % (key, self.pref_dict[key]))
			elif isinstance(self.pref_dict[key], float):
				fp.write("%s=%.9f\n" % (key, self.pref_dict[key]))
		fp.close()

sys.modules[__name__] = _Preference()

