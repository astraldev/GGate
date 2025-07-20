from __future__ import annotations
from collections import Counter
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame

import os
import copy
import igraph
from gi.repository import GObject
from shapely.geometry import LineString, Point
from ggate.Components.LogicGates.SystemComponents import BaseComponent
from ggate.Components.LogicGates import logic_gates
from ggate.const import definitions
from ggate import config
from ggate import Preference
from ggate.Utils import encode_text, decode_text, fit_components, get_components_rect, multiply_matrix, rotate_left_90, rotate_right_90
from gettext import gettext as _

CircuitComponent = Tuple[definitions, BaseComponent]

class CircuitConverter():
  def __init__(self, circuit: CircuitManager):
    self.circuit = circuit
    self.data = ""
  
  def _start_write(self):
    self.data = ""
    self._add_data("version", [
      ("author", [config.compatibility["version"]]),
      ("required", [config.compatibility["required"]]),
    ])

  def _add_data(self, key: str, attributes: list[tuple[str, list[str]]]) -> None:
    self.data += f"{key}"

    for attr_name, attr_value in attributes:
      self.data += "\n"
      attr_value = [str(x) for x in attr_value]
      str_attrs = ",".join(attr_value)
      self.data += f" {attr_name}={str_attrs}"
    
    self.data += "\n\n"

  def components_to_string(self):
    self._start_write()
    for c in self.circuit.components:
      if c[0] == definitions.component_net:
        self._add_data("net", [
          ("position", [c[1], c[2], c[3], c[4]]),
        ])
      else:
        self._add_data(c[0], [
          ("position", [c[1].pos_x, c[1].pos_y]),
          ("input_level", [str(int(p)) for p in c[1].input_level]),
          ("output_level", [str(int(p)) for p in c[1].output_level]),
          ("matrix", [str(int(p)) for p in c[1].matrix]),
          (
            "properties",
            [
              f"{c[1].prop_names[i]}:{encode_text(str(p))}" \
                for i, p in enumerate(c[1].values)
            ]
          ),
        ])
    self.data = self.data.strip()
    return self.data
  
  def _parse_section_content(self, lines: list[str]) -> dict:
    result = {}

    for line in lines:
      parts = line.strip().split('=')
      if len(parts) == 2:
        key = parts[0].strip()
        values = parts[1].strip().split(',')
        result[key] = values

    return result

  def parse_section(self, section: str):
    lines = section.split("\n")
    which = lines[0].strip()
    content = self._parse_section_content(lines[1:])
    
    if which == "net":
      content["position"] = [int(x) for x in content["position"]]
      if len(content["position"]) != 4:
        content["position"] = [0, 10, 10, 10]

      return [definitions.component_net, *content["position"]]
    
    elif which in logic_gates:
      component: CircuitComponent = [which, copy.deepcopy(logic_gates[which])]
      if (position := content.get("position", None)) and len(position) == 2:
        component[1].pos_x = int(position[0])
        component[1].pos_y = int(position[1])

      if (input_level := content.get("input_level", None)):
        component[1].input_level = [
          bool(int(level if level.isdigit() else 0)) \
            for level in input_level
        ]

      if (output_level := content.get("output_level", None)):
        component[1].output_level = [
          bool(int(level if level.isdigit() else 0)) \
            for level in output_level
        ]

      if (matrix := content.get("matrix", None)) and len(matrix) == 4:
        component[1].matrix = [float(m) for m in matrix]
      
      if (properties := content.get("properties", None)):
        for property in properties:
          if property == "":
            continue

          name, value = property.split(":")
          value = decode_text(value)
          if name in component[1].prop_names:
            index = component[1].prop_names.index(name)

            if component[1].properties[index][1] == definitions.property_int:
              component[1].values[index] = int(value)

            elif component[1].properties[index][1] == definitions.property_float:
              component[1].values[index] = float(value)
      
            elif component[1].properties[index][1] == definitions.property_select:
              component[1].values[index] = int(value)

            else:
              component[1].values[index] = value

      return component

    elif which == "version":
      current_version = config.VERSION
      current_required = config.compatibility["required"]

      authored_version = content.get("author", [current_version])[0]
      required_version = content.get("required", [current_required])[0]
      compatibility = config.is_compatible(required_version)
      if compatibility == 1:
        return _("Compatibility error: This circuit requires ggate %s or later.") % required_version
      elif compatibility == -1:
        return _("Compatibility error: This circuit was created by %(creator)s. ggate %(this)s doesn't support older than %(minimum)s.") \
          % { "creator": authored_version, "this": current_version, "minimum": current_required }

      return None
    return None

  def string_to_components(self, str_data) -> list[CircuitComponent]:
    components: list[CircuitComponent] = []

    for section in str_data.split("\n\n"):
      section = section.strip()
      if not section or section == "":
        continue

      parsed_section = self.parse_section(section)
      if parsed_section is None:
        continue
      elif isinstance(parsed_section, str):
        return parsed_section
      else:
        components.append(parsed_section)

    return components


class CircuitManager(GObject.GObject):
  __gsignals__ = {
    'currenttime-changed': (GObject.SIGNAL_RUN_FIRST, None, (float,)),
    'title-changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    'message-changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    'item-unselected': (GObject.SIGNAL_RUN_FIRST, None, ()),
    'alert': (GObject.SIGNAL_RUN_FIRST, None, (str,))
  }

  def __init__(self, mainframe: MainFrame):
    GObject.GObject.__init__(self)
    self.components: list[CircuitComponent] = []
    self.selected_components: list[CircuitComponent] = []
    self.action_count = 0
    self.save_point = 0
    self.current_time = 0.0
    self.simple_change = True
    self.need_save = False
    self.filepath = ""
    self.mainframe = mainframe
    self.converter = CircuitConverter(self)

    self.net_connections = []
    self.net_levels = []
    self.net_no_dot = []
    self.components_history = [[]]
    self.probe_levels_history = []
    self.component_state_history = []

  def save_file(self, filepath):
    data = self.converter.components_to_string()
    success = self.mainframe.io_manager.write_file(filepath, data)

    if not success:
      self.emit("alert", _("Unable to save file!"))
      return False

    self.filepath = filepath
    self.need_save = False
    self.simple_change = True
    self.save_point = self.action_count
    self.emit("title-changed", "%s - %s" % (os.path.basename(filepath), definitions.app_name))
    self.emit('message-changed', _('Saved File ')+os.path.basename(filepath))

    return True

  def open_file(self, filepath):
    read_results = self.mainframe.io_manager.read_file(filepath)
    if not read_results[0]:
      self.emit("alert", _("Unable to open file!"))
      return True

    tmp = self.converter.string_to_components(read_results[1])
  
    if isinstance(tmp, str):
      self.emit("alert", tmp)
      return True

    self.reset_circuit()
    self.components = tmp
    self.components_history = [copy.deepcopy(self.components)]
    self.filepath = filepath
    self.emit("title-changed", "%s - %s" % (os.path.basename(filepath), definitions.app_name))
    self.emit('message-changed', _('Opened file ' + os.path.basename(filepath)))

    return False
  
  def __get_nets(self):
    components = self.components[:]
    nets = [net for net in components if net[0] == definitions.component_net]
    return nets
  
  def __get_other_components(self):
    components = self.components[:]
    other_components = [comp for comp in components if comp[0] != definitions.component_net]
    return other_components

  def __create_index_for_point(self):
    point_to_index = {}
    index_to_point = []
    
    def get_index(point):
      if point not in point_to_index:
        point_to_index[point] = len(index_to_point)
        index_to_point.append(point)
      return point_to_index[point]
    
    return get_index, index_to_point, point_to_index
  
  def analyze_net_connections(self):
    """This function analyzes net connections"""
    # Reset net connections
    self.net_connections = []

    # Reset not- broken nets
    self.net_no_dot = []

    # Get the list of components
    components = self.components[:]

    # Create an index mapper with cache
    get_index, index_to_point, _ = self.__create_index_for_point()

    nets = self.__get_nets()
    other_components = [comp for comp in components if comp not in nets]

    # Get the points of the lines
    nodes = []

    for _, comp in other_components:
      for pin in comp.rot_input_pins + comp.rot_output_pins:
        nodes.append((comp.pos_x + pin[0], comp.pos_y + pin[1]))

    # Parse net points (start(x,y), end(x,y))
    net_points = [[(x1,y1), (x2, y2)] for _, x1, y1, x2, y2, in nets]

    # Convert net points to edges
    edges = [(get_index(p1), get_index(p2)) for p1, p2 in net_points]

    # Add the nodes (pins) to the graph vertex list
    [get_index(node) for node in nodes]
    
    # Setup the graph
    graph = igraph.Graph()
    graph.add_vertices(len(index_to_point))
    graph.add_edges(edges)

    # Find connected components in the graph
    connections = []
    graph_components = graph.components()

    for comp in graph_components:
      if len(comp) > 1:
       connections.append([index_to_point[idx] for idx in comp])
    
    # Find pin to pin connections and add them to the connection list
    pin_to_pin = [[item] for item, count in Counter(nodes).items() if count > 1]
    connections += pin_to_pin

    # Flatten the connection array
    flat_connections = [point for connection in connections for point in connection]
    net_no_dots = []

    # Filter out connections that occur in more than 2 points
    for connection in flat_connections:
      count = 0
      for data in components:
        name = data[0]
        component = data[1:] if name == definitions.component_net else data[1]
        if name == definitions.component_net:
          x1, y1, x2, y2 = component
          if connection == (x1, y1) or connection == (x2, y2):
            count += 1
        else:
          for pin in component.rot_input_pins + component.rot_output_pins:
            x = component.pos_x + pin[0]
            y = component.pos_y + pin[1]
            if connection == (x, y):
              count += 1

      if count <= 2:
        net_no_dots.append(connection)

    self.net_no_dot = net_no_dots
    self.net_connections = connections
  

  def split_nets(self, x, y):
    """Splits nets at a certain point"""
    # Get component data
    components = self.components[:]
    nets = self.__get_nets()
    nets_with_point = []

    # Select nets to split
    for net in nets:
      _, x1, y1, x2, y2 = net
      point = Point(x, y)
      segment = LineString([(x1, y1), (x2, y2)])
      if segment.contains(point) or segment.touches(point):
        nets_with_point.append(net)

    for net in nets_with_point:
      _, x1, y1, x2, y2 = net
      was_selected = net in self.selected_components

      if was_selected:
        self.selected_components.remove(net)
      self.components.remove(net)

      split_net_left = [[_, x1, y1, x, y], [_, x, y, x1, y1]]
      split_net_right = [[_, x2, y2, x, y], [_, x, y, x2, y2]]

      already_split_left = all(net in components for net in split_net_left)
      already_split_right = all(net in components for net in split_net_right)

      if x != x1 or y != y1:
        if not already_split_left:
          net_data = split_net_left[0]
          self.components.append(net_data)
          was_selected and self.selected_components.append(net_data)

      if x != x2 or y != y2:
        if not already_split_right:
          net_data = split_net_right[0]
          self.components.append(net_data)
          was_selected and self.selected_components.append(net_data)


  # def split_nets(self, x, y):
  #   # Split nets on the specified point
  #   # self.split_nets_at_point(x, y)
  #   spl_list = []
  #   for c in self.components:
  #     if c[0] == definitions.component_net:
  #       if (y - c[2]) * (c[3] - c[1]) == (x - c[1]) * (c[4] - c[2]):
  #         if (c[1] <= x <= c[3] and c[2] <= y <= c[4]) or (c[3] <= x <= c[1] and c[4] <= y <= c[2]):
  #           spl_list.append(c)

  #   for c in spl_list:
  #     self.components.remove(c)
  #     net_selected = False
  #     if c in self.selected_components:
  #       self.selected_components.remove(c)
  #       net_selected = True
  #     if x != c[1] or y != c[2]:
  #       if [definitions.component_net, c[1], c[2], x, y] not in self.components and [definitions.component_net, x, y, c[1], c[2]] not in self.components:
  #         component_data = [definitions.component_net, c[1], c[2], x, y]
  #         print("legacy spln (left): ", component_data)
  #         self.components.append(component_data)
  #         if net_selected:
  #           self.selected_components.append(component_data)
  #     if x != c[3] or y != c[4]:
  #       if [definitions.component_net, c[3], c[4], x, y] not in self.components and [definitions.component_net, x, y, c[3], c[4]] not in self.components:
  #         component_data = [definitions.component_net, x, y, c[3], c[4]]
  #         print("legacy spln (right): ", component_data)
  #         self.components.append(component_data)
  #         if net_selected:
  #           self.selected_components.append(component_data)

  def connect_nets(self, x, y, lock_selected = False):
    nets = []
    for c in self.components:
      if c[0] == definitions.component_net:
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
              component_data = [definitions.component_net, nets[0][3], nets[0][4], nets[1][3], nets[1][4]]
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
              component_data = [definitions.component_net, nets[0][3], nets[0][4], nets[1][1], nets[1][2]]
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
              component_data = [definitions.component_net, nets[0][1], nets[0][2], nets[1][3], nets[1][4]]
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
              component_data = [definitions.component_net, nets[0][1], nets[0][2], nets[1][1], nets[1][2]]
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
      if c[0] != definitions.component_net:
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
      if c[0] != definitions.component_net:
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
        if c[0] != definitions.component_net:
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
          if c[0] != definitions.component_net:
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
        if c[0] == definitions.component_probe:
          probe_levels.append(c[1].input_level[0])
      self.probe_levels_history.append(probe_levels)

      comp_state = [self.current_time, self.net_levels[:]]
      for c in self.components:
        if c[0] != definitions.component_net:
          comp_state.append((c[1].input_level[:], c[1].output_level[:], copy.deepcopy(c[1].output_stack), copy.deepcopy(c[1].store)))
      self.component_state_history.append(comp_state)

      tmptime = self.current_time
      timelist = []
      for c in self.components:
        if c[0] != definitions.component_net:
          for s in c[1].output_stack:
            if s and s[0][0] != self.current_time:
              timelist.append(s[0][0])
      if timelist:
        self.current_time = min(timelist)
      if tmptime == self.current_time:
        break

      for c in self.components:
        if c[0] != definitions.component_net:
          for i, s in enumerate(c[1].output_stack):
            if s and s[0][0] == self.current_time:
              c[1].output_level[i] = s.pop(0)[1]

    self.emit("currenttime-changed", self.current_time)
    return False

  def remove_selected_component(self):
    for c in self.selected_components:
      self.components.remove(c)

    for c in self.selected_components:
      if c[0] == definitions.component_net:
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
    self.emit("title-changed", "%s [%s] - %s" % (os.path.basename(self.filepath) if self.filepath != "" else definitions.text_notitle, definitions.text_modified, definitions.app_name))

  def undo(self):
    self.action_count -= 1
    if self.action_count >= 0:
      self.components = copy.deepcopy(self.components_history[self.action_count])

    if self.save_point == self.action_count and self.simple_change:
      self.need_save = False
      self.emit("title-changed", "%s - %s" % (os.path.basename(self.filepath) if self.filepath != "" else definitions.text_notitle, definitions.app_name))
    else:
      self.need_save = True
      self.emit("title-changed", "%s [%s] - %s" % ((os.path.basename(self.filepath) if self.filepath != "" else definitions.text_notitle), definitions.text_modified, definitions.app_name))

    self.selected_components = []
    self.emit("item-unselected")

  def redo(self):
    self.action_count += 1
    if self.action_count < len(self.components_history):
      self.components = copy.deepcopy(self.components_history[self.action_count])

    if self.save_point == self.action_count and self.simple_change:
      self.need_save = False
      self.emit("title-changed", "%s - %s" % (os.path.basename(self.filepath) if self.filepath != "" else definitions.text_notitle, definitions.app_name))
    else:
      self.need_save = True
      self.emit("title-changed", "%s [%s] - %s" % ((os.path.basename(self.filepath) if self.filepath != "" else definitions.text_notitle), definitions.text_modified, definitions.app_name))

    self.selected_components = []
    self.emit("item-unselected")
  
  def _get_rect_center (self, rect):
    center_x = (rect[0] + rect[2]) / 2
    center_x = int(center_x / 10) * 10

    center_y = (rect[1] + rect[3]) / 2
    center_y = int(center_y / 10) * 10
    
    return center_x, center_y

  def rotate_left_selected_components(self):
    if not self.selected_components:
      return
    rect = get_components_rect(self.selected_components)

    if rect[2] - rect[0] > 1080:
      return
    
    center_x, center_y = self._get_rect_center(rect)
    
    for c in self.selected_components:
      if c[0] == definitions.component_net:
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
      if c[0] == definitions.component_net:
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
      if c[0] == definitions.component_net:
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
      if c[0] == definitions.component_net:
        c[2] = -c[2] + center_y * 2
        c[4] = -c[4] + center_y * 2
      else:
        c[1].pos_y = -c[1].pos_y + center_y * 2
        c[1].matrix = multiply_matrix((1, 0, 0, -1), c[1].matrix)
        c[1].set_rot_props()
