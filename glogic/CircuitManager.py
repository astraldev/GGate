# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import copy, os, gettext, pickle
from gi.repository import Gtk, Gdk, GObject
from glogic import const, Preference
from glogic.Utils import *
from glogic.Components import *
from gettext import gettext as _
from glogic.ComponentConverter import components_to_string, string_to_components

class CircuitManager(GObject.GObject):

	__gsignals__ = {
		'currenttime-changed': (GObject.SIGNAL_RUN_FIRST, None, (float,)),
		'title-changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
		'message-changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
		'item-unselected': (GObject.SIGNAL_RUN_FIRST, None, ()),
		'alert': (GObject.SIGNAL_RUN_FIRST, None, (str,))
	}

	def __init__(self):
		GObject.GObject.__init__(self)
		self.components = []
		self.selected_components = []
		self.net_connections = []
		self.net_levels = []
		self.net_no_dot = []
		self.components_history = [[]]
		self.action_count = 0
		self.save_point = 0
		self.current_time = 0.0
		self.need_save = False
		self.simple_change = True
		self.filepath = ""
		self.probe_levels_history = []
		self.component_state_history = []

	def save_file(self, filepath):
		try:
			fp = open(filepath, mode="w", encoding="utf-8")
		except TypeError:
			import codecs
			fp = codecs.open(filepath, mode="w", encoding="utf-8")
		except IOError:
			return True
		fp.write(components_to_string(self.components))
		fp.close()
		self.filepath = filepath
		self.need_save = False
		self.simple_change = True
		self.save_point = self.action_count
		self.emit("title-changed", "%s - %s" % (os.path.basename(filepath), const.app_name))
		return False

	def open_file(self, filepath):
		try:
			fp = open(filepath, mode="r", encoding="utf-8")
		except TypeError:
			import codecs
			fp = codecs.open(filepath, mode="r", encoding="utf-8")
		except IOError:
			return True
		tmp = string_to_components(fp.read())
		if isinstance(tmp, str):
			self.emit("alert", tmp)
			fp.close()
			return True
		else:
			self.reset_circuit()
			self.components = tmp
			self.components_history = [copy.deepcopy(self.components)]
			self.filepath = filepath
			self.emit("title-changed", "%s - %s" % (os.path.basename(filepath), const.app_name))
			fp.close()
		return False

	def analyze_connections(self):
		# Analyze connections
		self.net_connections = []
		self.net_no_dot = []
		not_added = self.components[:]
		net_not_empty = True
		while True:
			connection = []
			changed_flag = True
			net_not_empty = False
			while changed_flag:
				changed_flag = False
				remlist = []
				for c in not_added:
					if c[0] == const.component_net:
						net_not_empty = True
						if len(connection) == 0:
							connection.append((c[1], c[2]))
							connection.append((c[3], c[4]))
							remlist.append(c)
						else:
							if (c[1], c[2]) in connection:
								if not (c[3], c[4]) in connection:
									connection.append((c[3], c[4]))
									changed_flag = True
								remlist.append(c)
							elif (c[3], c[4]) in connection:
								if not (c[1], c[2]) in connection:
									connection.append((c[1], c[2]))
									changed_flag = True
								remlist.append(c)
				for c in remlist:
					not_added.remove(c)

			if not net_not_empty:
				break

			for con_p in connection:
				cnt = 0
				for c in self.components:
					if c[0] == const.component_net:
						if con_p[0] == c[1] and con_p[1] == c[2]:
							cnt += 1
						elif con_p[0] == c[3] and con_p[1] == c[4]:
							cnt += 1
					else:
						for p in c[1].rot_input_pins + c[1].rot_output_pins:
							if con_p[0] == c[1].pos_x + p[0] and con_p[1] == c[1].pos_y + p[1]:
								cnt += 1
				if cnt <= 2:
					self.net_no_dot.append(con_p)

			self.net_connections.append(connection)

		for c in self.components:
			if c[0] != const.component_net:
				for p in c[1].rot_input_pins + c[1].rot_output_pins:
					found = False
					for net in self.net_connections:
						if (c[1].pos_x + p[0], c[1].pos_y + p[1]) in net:
							found = True
							break
					if not found:
						self.net_connections.append([(c[1].pos_x + p[0], c[1].pos_y + p[1])])

	def split_nets(self, x, y):
		# Split nets on the specified point
		spl_list = []
		for c in self.components:
			if c[0] == const.component_net:
				if (y - c[2]) * (c[3] - c[1]) == (x - c[1]) * (c[4] - c[2]):
					if (c[1] <= x <= c[3] and c[2] <= y <= c[4]) or (c[3] <= x <= c[1] and c[4] <= y <= c[2]):
						spl_list.append(c)

		for c in spl_list:
			self.components.remove(c)
			net_selected = False
			if c in self.selected_components:
				self.selected_components.remove(c)
				net_selected = True
			if x != c[1] or y != c[2]:
				if not [const.component_net, c[1], c[2], x, y] in self.components and not [const.component_net, x, y, c[1], c[2]] in self.components:
					component_data = [const.component_net, c[1], c[2], x, y]
					self.components.append(component_data)
					if net_selected:
						self.selected_components.append(component_data)
			if x != c[3] or y != c[4]:
				if not [const.component_net, c[3], c[4], x, y] in self.components and not [const.component_net, x, y, c[3], c[4]] in self.components:
					component_data = [const.component_net, x, y, c[3], c[4]]
					self.components.append(component_data)
					if net_selected:
						self.selected_components.append(component_data)

	def connect_nets(self, x, y, lock_selected = False):
		nets = []
		for c in self.components:
			if c[0] == const.component_net:
				if c[1] == x and c[2] == y or c[3] == x and c[4] == y:
					if not (lock_selected and c in self.selected_components):
						nets.append(c)
			else:
				# Cannot connect if there are terminals of components
				for p in c[1].rot_input_pins + c[1].rot_output_pins:
					if c[1].pos_x + p[0] == x and c[1].pos_y + p[1] == y:
						return

		if len(nets) == 2:
			if (nets[0][1] - nets[0][3]) * (nets[1][2] - nets[1][4]) == (nets[1][1] - nets[1][3]) * (nets[0][2] - nets[0][4]):
				if nets[0][1] == x and nets[0][2] == y:
					if nets[1][1] == x and nets[1][2] == y:
						if (nets[0][1] - nets[0][3]) * (nets[1][1] - nets[1][3]) <= 0 and (nets[0][2] - nets[0][4]) * (nets[1][2] - nets[1][4]) <= 0:
							component_data = [const.component_net, nets[0][3], nets[0][4], nets[1][3], nets[1][4]]
							self.components.append(component_data)
							self.components.remove(nets[0])
							self.components.remove(nets[1])
							net_selected = False
							if nets[0] in self.selected_components:
								self.selected_components.remove(nets[0])
								net_selected = True
							if nets[1] in self.selected_components:
								self.selected_components.remove(nets[1])
								net_selected = True
							if net_selected:
								self.selected_components.append(component_data)
					else:
						if (nets[0][1] - nets[0][3]) * (nets[1][1] - nets[1][3]) >= 0 and (nets[0][2] - nets[0][4]) * (nets[1][2] - nets[1][4]) >= 0:
							component_data = [const.component_net, nets[0][3], nets[0][4], nets[1][1], nets[1][2]]
							self.components.append(component_data)
							self.components.remove(nets[0])
							self.components.remove(nets[1])
							net_selected = False
							if nets[0] in self.selected_components:
								self.selected_components.remove(nets[0])
								net_selected = True
							if nets[1] in self.selected_components:
								self.selected_components.remove(nets[1])
								net_selected = True
							if net_selected:
								self.selected_components.append(component_data)
				else:
					if nets[1][1] == x and nets[1][2] == y:
						if (nets[0][1] - nets[0][3]) * (nets[1][1] - nets[1][3]) >= 0 and (nets[0][2] - nets[0][4]) * (nets[1][2] - nets[1][4]) >= 0:
							component_data = [const.component_net, nets[0][1], nets[0][2], nets[1][3], nets[1][4]]
							self.components.append(component_data)
							self.components.remove(nets[0])
							self.components.remove(nets[1])
							net_selected = False
							if nets[0] in self.selected_components:
								self.selected_components.remove(nets[0])
								net_selected = True
							if nets[1] in self.selected_components:
								self.selected_components.remove(nets[1])
								net_selected = True
							if net_selected:
								self.selected_components.append(component_data)
					else:
						if (nets[0][1] - nets[0][3]) * (nets[1][1] - nets[1][3]) <= 0 and (nets[0][2] - nets[0][4]) * (nets[1][2] - nets[1][4]) <= 0:
							component_data = [const.component_net, nets[0][1], nets[0][2], nets[1][1], nets[1][2]]
							self.components.append(component_data)
							self.components.remove(nets[0])
							self.components.remove(nets[1])
							net_selected = False
							if nets[0] in self.selected_components:
								self.selected_components.remove(nets[0])
								net_selected = True
							if nets[1] in self.selected_components:
								self.selected_components.remove(nets[1])
								net_selected = True
							if net_selected:
								self.selected_components.append(component_data)

	def set_netlevels(self):
		self.net_levels = [-1]*len(self.net_connections)
		for c in self.components:
			if c[0] != const.component_net:
				for i,p in enumerate(c[1].rot_output_pins):
					for j,net in enumerate(self.net_connections):
						if (c[1].pos_x + p[0], c[1].pos_y + p[1]) in net:
							if self.net_levels[j] != -1 and self.net_levels[j] != c[1].output_level[i]:
								self.emit("message-changed", _("Output port is short circuit!"))
								return True
							self.net_levels[j] = c[1].output_level[i]
		return False

	def initialize_logic(self):
		self.probe_levels_history = []
		self.component_state_history = []
		self.current_time = 0.0
		for c in self.components:
			if c[0] != const.component_net:
				c[1].initialize()

	def revert_state(self):
		if self.component_state_history:
			t = 0
			for i, comp_state in reversed(list(enumerate(self.component_state_history))):
				if comp_state[0] <= self.current_time:
					t = i
					break
			i = 2
			for c in self.components:
				if c[0] != const.component_net:
					c[1].input_level = self.component_state_history[t][i][0]
					c[1].output_level = self.component_state_history[t][i][1]
					c[1].output_stack = self.component_state_history[t][i][2]
					c[1].store = self.component_state_history[t][i][3]
					i += 1
			self.net_levels = self.component_state_history[t][1]

		self.emit("currenttime-changed", self.current_time)

	def analyze_logic(self):
		counter = 0
		stop_time = Preference.max_calc_duration
		max_iters = Preference.max_calc_iters

		if self.component_state_history:
			t = 0
			for i, comp_state in reversed(list(enumerate(self.component_state_history))):
				if comp_state[0] <= self.current_time:
					t = i
					break
			self.current_time = self.component_state_history[t][0]
			self.component_state_history = self.component_state_history[:t]
			self.probe_levels_history = self.probe_levels_history[:t]

		while self.current_time < stop_time:
			net_levels_history = []

			while True:
				if self.set_netlevels():
					return True

				for c in self.components:
					if c[0] != const.component_net:
						input_datas = []
						for p in c[1].rot_input_pins:
							for j, net in enumerate(self.net_connections):
								if (c[1].pos_x + p[0], c[1].pos_y + p[1]) in net:
									if self.net_levels[j] == -1:
										self.emit("message-changed", _("Input port is open circuit!"))
										return True
									input_datas.append(self.net_levels[j])

						c[1].calculate(input_datas, self.current_time)
						c[1].input_level = input_datas[:]

						for i, p in enumerate(c[1].rot_output_pins):
							if c[1].output_stack[i]:
								if c[1].output_stack[i][0][0] == self.current_time:
									c[1].output_level[i] = c[1].output_stack[i].pop(0)[1]
								elif c[1].output_level[i] == c[1].output_stack[i][0][1]:
									c[1].output_stack[i].pop(0)

				if self.net_levels in net_levels_history[:-1]:
					if self.net_levels == net_levels_history[len(net_levels_history) - 1]:
						self.emit("message-changed", "")
						break
					else:
						self.emit("message-changed", _("This circuit oscillates on infinite frequency!"))
						return True

				net_levels_history.append(self.net_levels)

				if counter >= max_iters:
					self.emit("message-changed", _("This logic is complexity! (iters > %d)") % max_iters)
					return True

				counter += 1

			probe_levels = [self.current_time]
			for c in self.components:
				if c[0] == const.component_probe:
					probe_levels.append(c[1].input_level[0])
			self.probe_levels_history.append(probe_levels)

			comp_state = [self.current_time, self.net_levels[:]]
			for c in self.components:
				if c[0] != const.component_net:
					comp_state.append((c[1].input_level[:], c[1].output_level[:], copy.deepcopy(c[1].output_stack), copy.deepcopy(c[1].store)))
			self.component_state_history.append(comp_state)

			tmptime = self.current_time
			timelist = []
			for c in self.components:
				if c[0] != const.component_net:
					for s in c[1].output_stack:
						if s and s[0][0] != self.current_time:
							timelist.append(s[0][0])
			if timelist:
				self.current_time = min(timelist)
			if tmptime == self.current_time:
				break

			for c in self.components:
				if c[0] != const.component_net:
					for i, s in enumerate(c[1].output_stack):
						if s and s[0][0] == self.current_time:
							c[1].output_level[i] = s.pop(0)[1]

		self.emit("currenttime-changed", self.current_time)
		return False

	def remove_selected_component(self):
		for c in self.selected_components:
			self.components.remove(c)

		for c in self.selected_components:
			if c[0] == const.component_net:
				self.connect_nets(c[1], c[2])
				self.connect_nets(c[3], c[4])
			else:
				for p in c[1].rot_input_pins + c[1].rot_output_pins:
					self.connect_nets(c[1].pos_x + p[0], c[1].pos_y + p[1])

		self.selected_components = []
		self.emit("item-unselected")

	def reset_circuit(self):
		self.selected_components = []
		self.emit("item-unselected")
		self.components = []
		self.components_history = [[]]
		self.action_count = 0
		self.save_point = 0
		self.need_save = False
		self.simple_change = True
		self.filepath = ""

	def push_history(self):
		self.action_count += 1
		if self.action_count < len(self.components_history):
			self.components_history = self.components_history[0:self.action_count]
			if self.action_count <= self.save_point:
				self.simple_change = False
		self.components_history.append(copy.deepcopy(self.components))
		self.need_save = True
		self.emit("title-changed", "%s [%s] - %s" % (os.path.basename(self.filepath) if self.filepath != "" else const.text_notitle, const.text_modified, const.app_name))

	def undo(self):
		self.action_count -= 1
		if self.action_count >= 0:
			self.components = copy.deepcopy(self.components_history[self.action_count])

		if self.save_point == self.action_count and self.simple_change:
			self.need_save = False
			self.emit("title-changed", "%s - %s" % (os.path.basename(self.filepath) if self.filepath != "" else const.text_notitle, const.app_name))
		else:
			self.need_save = True
			self.emit("title-changed", "%s [%s] - %s" % ((os.path.basename(self.filepath) if self.filepath != "" else const.text_notitle), const.text_modified, const.app_name))

		self.selected_components = []
		self.emit("item-unselected")

	def redo(self):
		self.action_count += 1
		if self.action_count < len(self.components_history):
			self.components = copy.deepcopy(self.components_history[self.action_count])

		if self.save_point == self.action_count and self.simple_change:
			self.need_save = False
			self.emit("title-changed", "%s - %s" % (os.path.basename(self.filepath) if self.filepath != "" else const.text_notitle, const.app_name))
		else:
			self.need_save = True
			self.emit("title-changed", "%s [%s] - %s" % ((os.path.basename(self.filepath) if self.filepath != "" else const.text_notitle), const.text_modified, const.app_name))

		self.selected_components = []
		self.emit("item-unselected")

	def rotate_left_selected_components(self):
		if not self.selected_components:
			return
		rect = get_components_rect(self.selected_components)
		if rect[2] - rect[0] > 1080:
			return
		center_x = (rect[0] + rect[2]) / 2
		center_x = int(center_x / 10) * 10

		center_y = (rect[1] + rect[3]) / 2
		center_y = int(center_y / 10) * 10
		
		for c in self.selected_components:
			if c[0] == const.component_net:
				(c[1], c[2]) = rotate_left_90(c[1], c[2], center_x, center_y)
				(c[3], c[4]) = rotate_left_90(c[3], c[4], center_x, center_y)
			else:
				(c[1].pos_x, c[1].pos_y) = rotate_left_90(c[1].pos_x, c[1].pos_y, center_x, center_y)
				c[1].matrix = multiply_matrix((0, 1, -1, 0), c[1].matrix)
				c[1].set_rot_props()
		fit_components(self.selected_components, 1920, 1080)

	def rotate_right_selected_components(self):
		if not self.selected_components:
			return
		rect = get_components_rect(self.selected_components)
		if rect[2] - rect[0] > 1080:
			return
		center_x = (rect[0] + rect[2]) / 2
		center_y = (rect[1] + rect[3]) / 2
		center_x = int(center_x / 10) * 10
		center_y = int(center_y / 10) * 10
		for c in self.selected_components:
			if c[0] == const.component_net:
				(c[1], c[2]) = rotate_right_90(c[1], c[2], center_x, center_y)
				(c[3], c[4]) = rotate_right_90(c[3], c[4], center_x, center_y)
			else:
				(c[1].pos_x, c[1].pos_y) = rotate_right_90(c[1].pos_x, c[1].pos_y, center_x, center_y)
				c[1].matrix = multiply_matrix((0, -1, 1, 0), c[1].matrix)
				c[1].set_rot_props()
		fit_components(self.selected_components, 1920, 1080)

	def flip_hori_selected_components(self):
		if not self.selected_components:
			return
		rect = get_components_rect(self.selected_components)
		center_x = (rect[0] + rect[2]) / 2
		for c in self.selected_components:
			if c[0] == const.component_net:
				c[1] = -c[1] + center_x * 2
				c[3] = -c[3] + center_x * 2
			else:
				c[1].pos_x = -c[1].pos_x + center_x * 2
				c[1].matrix = multiply_matrix((-1, 0, 0, 1), c[1].matrix)
				c[1].set_rot_props()

	def flip_vert_selected_components(self):
		if not self.selected_components:
			return
		rect = get_components_rect(self.selected_components)
		center_y = (rect[1] + rect[3]) / 2
		for c in self.selected_components:
			if c[0] == const.component_net:
				c[2] = -c[2] + center_y * 2
				c[4] = -c[4] + center_y * 2
			else:
				c[1].pos_y = -c[1].pos_y + center_y * 2
				c[1].matrix = multiply_matrix((1, 0, 0, -1), c[1].matrix)
				c[1].set_rot_props()
