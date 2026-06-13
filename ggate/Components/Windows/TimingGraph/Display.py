from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame

from gi.repository import Gtk, Adw, Gdk
from ggate.Components.Windows.TimingGraph.Diagram import TimingGraphDiagram


class TimingGraphDisplayWindow (Adw.Dialog):
    def __init__(self, parent: MainFrame):
       Adw.Dialog.__init__(self, can_close=True)

       self._draw_area = TimingGraphDiagram(parent)
       self.header_bar = Gtk.HeaderBar()
    
    def display(self):
       self._draw_area.draw()
       self.present()
       