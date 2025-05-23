# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from gi.repository import Gtk, Gdk 
from ggate.ComponentConverter import string_to_components

menu_xml = """
<interface>
  <menu id="model">
    <section>
        <attribute name="display-hint">horizontal-buttons</attribute>
        <item>
          <attribute name="label" translatable="yes">Flip Horizontally</attribute>
          <attribute name="action">menu.flip_hori</attribute>
          <attribute name="verb-icon">object-flip-horizontal-symbolic</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Flip Vertically</attribute>
          <attribute name="action">menu.flip_verti</attribute>
          <attribute name="verb-icon">object-flip-vertical-symbolic</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Rotate Left</attribute>
          <attribute name="action">menu.rot_left</attribute>
          <attribute name="verb-icon">object-rotate-left-symbolic</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Rotate right</attribute>
          <attribute name="action">menu.rot_right</attribute>
          <attribute name="verb-icon">object-rotate-right-symbolic</attribute>
        </item>
    </section>
    <section>
        <item>
          <attribute name="label" translatable="yes">Properties</attribute>
          <attribute name="action">menu.properties</attribute>
          <attribute name="accel">&lt;Ctrl&gt;P</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Add net</attribute>
          <attribute name="action">app.toggle_net</attribute>
          <attribute name="accel">&lt;Ctrl&gt;E</attribute>
        </item>
    </section>
    <section>
        <item>
          <attribute name="label" translatable="yes">Copy</attribute>
          <attribute name="action">app.on_action_copy_pressed</attribute>
          <attribute name="accel">&lt;Ctrl&gt;C</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Cut</attribute>
          <attribute name="action">app.on_action_cut_pressed</attribute>
          <attribute name="accel">&lt;Ctrl&gt;X</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Paste</attribute>
          <attribute name="action">app.on_action_paste_pressed</attribute>
          <attribute name="accel">&lt;Ctrl&gt;V</attribute>
        </item>
    </section>
  </menu>
</interface>
"""

running_xml = """
<interface>
  <menu id="model">
    <section>
        <item>
          <attribute name="label" translatable="yes">Timing Diagram</attribute>
          <attribute name="action">app.on_action_diagram_pressed</attribute>
        </item>
    </section>
  </menu>
</interface>
"""


class Menu(Gtk.PopoverMenu):
    def __init__(self, parent):
        _menu_builder = Gtk.Builder.new_from_string(menu_xml, -1)
        _menu = _menu_builder.get_object("model")
        super().__init__()
        self.set_menu_model(_menu)
        self.set_parent(parent)
        self.set_has_arrow(False)
    
    def calculate(self, x, y):
      parent = self.get_parent()
      point_x = x - parent.get_hadjustment().get_value()
      point_y = y - parent.get_vadjustment().get_value()
      return point_x, point_y
    
    def present(self, x, y, *args):
        rectangle = Gdk.Rectangle()
        rectangle.x, rectangle.y = self.calculate(x, y)
        rectangle.width = 1
        rectangle.height = 1

        window_actions = [
          'app.on_action_copy_pressed', 
          'app.on_action_cut_pressed',
        ]

        window =  self.get_parent().parent

        has_selected = len(self.get_parent().circuit.selected_components) == 1

        def _(clipboard, task):
          str_data = window.clipboard.read_text_finish(task)
          if str_data is not None:
            tmp = string_to_components(str_data)
            if not isinstance(tmp, str) and len(tmp) > 0:
              window.action_set_enabled('app.on_action_paste_pressed', True)
              return
          window.action_set_enabled('app.on_action_paste_pressed', False)

        for action in self.get_parent().actions:
          self.action_set_enabled(action, has_selected)
        for action in window_actions:
          if not has_selected:
            window.action_set_enabled(action, False)
          else:
            window.action_set_enabled(action, True)
            
        window.clipboard.read_text_async(None, _)

        self.set_pointing_to(rectangle)
        self.popup()

class RunningMenu(Gtk.PopoverMenu):

    def __init__(self, parent):
        _menu_builder = Gtk.Builder.new_from_string(running_xml, -1)
        _menu = _menu_builder.get_object("model")
        super().__init__()
        self.set_menu_model(_menu)
        self.set_parent(parent)
        self.set_has_arrow(False)
        
    def calculate(self, x, y):
      parent = self.get_parent()
      point_x = x - parent.get_hadjustment().get_value()
      point_y = y - parent.get_vadjustment().get_value()
      return point_x, point_y    

    def present(self, x, y):
        rectangle = Gdk.Rectangle()
        rectangle.x, rectangle.y = self.calculate(x, y)

        rectangle.width = 1
        rectangle.height = 1

        self.set_pointing_to(rectangle)
        self.popup()