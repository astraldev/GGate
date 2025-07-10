import os
from gi.repository import Gtk, Gdk
from ggate.ComponentConverter import string_to_components
from ggate.config import DATADIR

def _get_icon_path(icon: str):
    return os.path.join(DATADIR, "images", "actions", f"{icon}.svg")

menu_xml = f"""
<interface>
  <menu id="model">
    <section>
        <attribute name="display-hint">horizontal-buttons</attribute>
        <item>
          <attribute name="label" translatable="yes">Flip Horizontally</attribute>
          <attribute name="action">menu.flip_hori</attribute>
          <attribute name="verb-icon">{_get_icon_path("flip-horizontal")}</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Flip Vertically</attribute>
          <attribute name="action">menu.flip_verti</attribute>
          <attribute name="verb-icon">{_get_icon_path("flip-vertical")}</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Rotate Left</attribute>
          <attribute name="action">menu.rot_left</attribute>
          <attribute name="verb-icon">{_get_icon_path("rotate-left")}</attribute>
        </item>
        <item>
          <attribute name="label" translatable="yes">Rotate right</attribute>
          <attribute name="action">menu.rot_right</attribute>
          <attribute name="verb-icon">{_get_icon_path("rotate-right")}</attribute>
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
        <item>
          <attribute name="label" translatable="yes">Delete</attribute>
          <attribute name="action">app.on_action_delete_pressed</attribute>
          <attribute name="accel">BackSpace</attribute>
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


class ContextMenu(Gtk.PopoverMenu):
    def __init__(self, parent):
        _menu_builder = Gtk.Builder.new_from_string(menu_xml, -1)
        _menu = _menu_builder.get_object("model")
        self._parent = parent

        super().__init__()
        self.set_menu_model(_menu)
        self.set_parent(parent)
        self.set_has_arrow(False)
    
    def _get_window(self) -> Gtk.ApplicationWindow:
        return self.get_parent().parent
    
    def _handle_clipboard(self, clipboard, task, *args):
        window = self._get_window()
        str_data = window.get_clipboard().read_text_finish(task)
        if str_data is not None:
            components = self._parent.circuit.converter.string_to_components(str_data)
            has_clipboard = not isinstance(components, str) and len(components) > 0
            window.action_set_enabled("app.on_action_paste_pressed", has_clipboard)

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

        window = self._get_window()
        window_actions = ["app.on_action_copy_pressed", "app.on_action_cut_pressed"]

        has_selected = len(self.get_parent().circuit.selected_components) == 1

        for action in self.get_parent().actions:
            self.action_set_enabled(action, has_selected)

        for action in window_actions:
            window.action_set_enabled(action, has_selected)

        window.get_clipboard().read_text_async(None, self._handle_clipboard)
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
