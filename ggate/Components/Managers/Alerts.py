from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame
from gi.repository import Gtk, Adw

# TODO: translations

class AlertDialogs(Adw.AlertDialog):
  def __init__(self, mainframe: MainFrame, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.mainframe = mainframe
    self.responses = [("cancel", "Cancel"), ("yes", "Yes"), ("no", "No")]

    self.CANCEL_RESPONSE = self.responses[0][0]
    self.YES_RESPONSE = self.responses[1][0]
    self.NO_RESPONSE = self.responses[2][0]

  def __get_unsaved_buffer_alert_result(self, allow, deny):
    def internal(dialog, result):
      result = self.choose_finish(result)
      if result == self.CANCEL_RESPONSE:
        return
      elif result == self.YES_RESPONSE:
        allow()
      else:
        deny()
    
    return internal
  
  def alert_open_unsaved_buffer(self):
    self.set_heading("Unsaved changes")
    self.set_body("Buffer was modified, save changes?")

    self.add_responses(*self.responses)
    self.set_default_response(self.YES_RESPONSE)
    self.set_close_response(self.CANCEL_RESPONSE)

    self.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        self.mainframe.on_action_save_pressed,
        self.mainframe.file_manager.open_activated,
      )
    )

  def alert_new_unsaved_buffer(self):
    self.set_heading("Unsaved changes")
    self.set_body("Buffer was modified, save changes before creating new buffer?")

    self.add_responses(*self.responses)
    self.set_default_response(self.YES_RESPONSE)
    self.set_close_response(self.CANCEL_RESPONSE)

    self.set_response_appearance(
      self.NO_RESPONSE,
      Adw.ResponseAppearance.DESTRUCTIVE
    )

    self.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        self.mainframe.on_action_save_pressed,
        self.mainframe.create_new_buffer,
      )
    )
  
  def alert_close_unsaved_buffer(self):
    self.set_heading("Unsaved changes")
    self.set_body("Buffer was modified, save changes before closing?")
    
    self.add_responses(*self.responses)
    self.set_default_response(self.YES_RESPONSE)
    self.set_close_response(self.CANCEL_RESPONSE)

    self.set_response_appearance(
      self.NO_RESPONSE,
      Adw.ResponseAppearance.DESTRUCTIVE
    )

    self.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        self.mainframe.on_action_save_pressed,
        self.mainframe.application.quit,
      )
    )
  
