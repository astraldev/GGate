from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame

from gi.repository import Gtk, Adw, Gdk
from gettext import gettext as _
from ggate.Components.Windows.TimingGraph.Diagram import TimingGraphDiagram


class TimingGraphDisplayWindow (Adw.Dialog):
    def __init__(self, parent: MainFrame):
       Adw.Dialog.__init__(self, can_close=True)
       self._parent = parent
       self.set_title(_("Timing Graph"))
       self.set_content_width(600)
       self.set_content_height(400)

       self._draw_area = TimingGraphDiagram(parent)
       self.set_child(self._draw_area)
    
    def display(self):
       self._draw_area.draw()
       self.present(self._parent)
       