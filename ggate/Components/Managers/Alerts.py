from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame
from gi.repository import Gtk

class AlertDialogs(Gtk.AlertDialog):
  def __init__(self, mainframe: MainFrame, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.mainframe = mainframe

  def __get_unsaved_buffer_alert_result(self, allow, deny):
    def internal(dialog, result):
      result = self.choose_finish(result)
      if result == 0:
        return
      elif result == 1:
        allow()
      else:
        deny()
    
    return internal
  
  def alert_open_unsaved_buffer(self):
    # todo: translations
    self.set_message("Unsaved changes")
    self.set_detail("Buffer was modified, save changes?")
    self.set_buttons(["Cancel", "Yes", "No"])
    self.set_cancel_button(0)
    self.set_default_button(1)
    self.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        self.mainframe.on_action_save_pressed,
        self.mainframe.file_manager.open_activated,
      )
    )

  def alert_new_unsaved_buffer(self):
    # todo: translations
    self.set_message("Unsaved changes")
    self.set_detail("Buffer was modified, save changes before creating new buffer?")
    self.set_buttons(["Cancel", "Yes", "No"])
    self.set_cancel_button(0)
    self.set_default_button(1)
    self.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        self.mainframe.on_action_save_pressed,
        self.mainframe.create_new_buffer,
      )
    )
  
  def alert_close_unsaved_buffer(self):
    # todo: translations
    self.set_message("Unsaved changes")
    self.set_detail("Buffer was modified, save changes before closing?")
    self.set_buttons(["Cancel", "Yes", "No"])
    self.set_cancel_button(0)
    self.set_default_button(1)
    self.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        self.mainframe.on_action_save_pressed,
        self.mainframe.application.quit,
      )
    )
  
