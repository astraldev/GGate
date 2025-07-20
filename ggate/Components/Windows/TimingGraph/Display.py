from typing import TYPE_CHECKING
from gi.repository import Gtk, Adw, Gdk

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame
  from ggate.CircuitManager import CircuitManager

class TimingGraphDisplayWindow (Adw.Dialog):
    def __init__(self, parent: MainFrame):
       Adw.Dialog.__init__(self, can_close=True)

       self.header_bar = Gtk.HeaderBar()
       