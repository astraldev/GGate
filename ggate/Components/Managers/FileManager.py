from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame

from ggate.const import definitions
from gi.repository import Gtk, Gio
from os import path

class FileIOManager():
  @staticmethod
  def read_file(filepath: str):
    try:
      fp = open(filepath, mode="r", encoding="utf-8")
    except TypeError:
      import codecs
      fp = codecs.open(filepath, mode="r", encoding="utf-8")
    except IOError:
      return (False, None)
    
    return (True, fp.read())
  
  @staticmethod
  def write_file(filepath: str, data: str):
    try:
      fp = open(filepath, mode="w", encoding="utf-8")
    except TypeError:
      import codecs
      fp = codecs.open(filepath, mode="w", encoding="utf-8")
    except IOError:
      return False
    
    fp.write(data)
    fp.close()

    return True

class FileManager(Gtk.FileDialog):
  OPEN = 0
  SAVE = 1
  SAVE_AS = 2

  GLC = 3
  IMG = 4

  def __init__(self, mainframe: MainFrame, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.mainframe = mainframe
    self.state = None
    self.type = FileManager.GLC

  @classmethod
  def for_glc(cls, mainframe: MainFrame):  
    glc_filters = Gtk.FileFilter()
    glc_filters.set_name(definitions.glcfile_text)
    glc_filters.add_pattern("*.glc")

    any_filters = Gtk.FileFilter()
    any_filters.set_name(definitions.anyfile_text)
    any_filters.add_pattern("*")

    list_model = Gio.ListStore()
    list_model.append(glc_filters)
    list_model.append(any_filters)

    fm = cls(mainframe)
    fm.set_filters(list_model)
    fm.type = cls.GLC

    return fm
  
  @classmethod
  def for_img(cls, mainframe: MainFrame):
    png_filter = Gtk.FileFilter()
    png_filter.set_name(definitions.pngfile_text)
    png_filter.add_pattern("*.png")

    svg_filter = Gtk.FileFilter()
    svg_filter.set_name(definitions.svgfile_text)
    svg_filter.add_pattern("*.svg")

    pdf_filter = Gtk.FileFilter()
    pdf_filter.set_name(definitions.pdffile_text)
    pdf_filter.add_pattern("*.pdf")

    ps_filter = Gtk.FileFilter()
    ps_filter.set_name(definitions.psfile_text)
    ps_filter.add_pattern("*.ps")

    list_model = Gio.ListStore()
    list_model.append(png_filter)
    list_model.append(svg_filter)
    list_model.append(pdf_filter)
    list_model.append(ps_filter)

    fm = cls(mainframe)
    fm.set_filters(list_model)
    fm.type = cls.IMG

    return fm
  
  def open_activated(self, *args):
    self.state = FileManager.OPEN
    self.open(
      parent=self.mainframe,
      callback=self.__file_opened,
    )

  def save_activated(self, *args):
    self.state = FileManager.SAVE
    if not path.exists(self.mainframe.circuit.filepath):
      return self.save_as_activated()

    self.save(
      parent=self.mainframe,
      callback=self.__file_saved,
    )
  
  def save_as_activated(self, *args):
    self.state = FileManager.SAVE_AS

    self.save(
      parent=self.mainframe,
      callback=self.__file_saved,
    )

  def __file_opened(self, dialog, value, *args):
    if not value: return
  
    results = self.open_finish(value)
    filepath = results.get_path()
    if not filepath: return

    self.mainframe.open_file_complete(filepath)
  
  def __file_saved(self, dialog, value, *args):
    if not value: return

    results = self.save_finish(value)
    filepath = results.get_path()
    if not filepath: return
    
    if self.state == FileManager.SAVE:
      self.mainframe.save_file__complete(filepath)
    elif self.state == FileManager.SAVE_AS:
      self.mainframe.save_file_as__complete(filepath)
    
    self.state = None