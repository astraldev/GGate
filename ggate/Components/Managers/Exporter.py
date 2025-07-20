from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame

class Exporter:
    def __init__(self, mainframe: MainFrame):
       self.mainframe = mainframe
