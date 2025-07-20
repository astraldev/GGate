# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from abc import ABC, abstractmethod
from gettext import gettext as _
from typing import List
from gi.repository import Pango
import cairo

class PropertyError:
  def __init__(self, message: str, positions: List[int] = None):
    self.positions = positions if positions is not None else []
    self.message = message

class BaseComponent(ABC):
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
  
  @abstractmethod
  def drawComponent(self, cr: cairo.Context, layout: Pango.Layout):
    return

  @abstractmethod
  def drawComponentEditOverlap(self, cr: cairo.Context, layout):
    return

  @abstractmethod
  def drawComponentRunOverlap(self, cr: cairo.Context, layout):
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

  def propertyChanged(self, prop) -> False | PropertyError:
    return False

  def initialize(self):
    return

  def calculate(self, input_datas, time):
    return


