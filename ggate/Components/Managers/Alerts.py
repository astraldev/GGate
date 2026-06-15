from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ggate.MainFrame import MainFrame
from gi.repository import Adw

# TODO: translations

class AlertDialogs:
  def __init__(self, mainframe: MainFrame):
    self.mainframe = mainframe
    self.responses = [("cancel", "Cancel"), ("yes", "Yes"), ("no", "No")]

    self.CANCEL_RESPONSE = self.responses[0][0]
    self.YES_RESPONSE = self.responses[1][0]
    self.NO_RESPONSE = self.responses[2][0]

  def _create_dialog(self, heading: str, body: str) -> Adw.AlertDialog:
    dialog = Adw.AlertDialog()
    dialog.set_heading(heading)
    dialog.set_body(body)
    for response_id, label in self.responses:
      dialog.add_response(response_id, label)
    dialog.set_default_response(self.YES_RESPONSE)
    dialog.set_close_response(self.CANCEL_RESPONSE)
    return dialog

  def __get_unsaved_buffer_alert_result(self, dialog, allow, deny):
    def internal(dialog_obj, result):
      res = dialog.choose_finish(result)
      if res == self.CANCEL_RESPONSE:
        return
      elif res == self.YES_RESPONSE:
        allow()
      else:
        deny()
    return internal

  def alert_open_unsaved_buffer(self):
    dialog = self._create_dialog("Unsaved changes", "Buffer was modified, save changes?")
    dialog.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        dialog,
        self.mainframe.on_action_save_pressed,
        self.mainframe.file_manager.open_activated,
      )
    )

  def alert_new_unsaved_buffer(self):
    dialog = self._create_dialog("Unsaved changes", "Buffer was modified, save changes before creating new buffer?")
    dialog.set_response_appearance(
      self.NO_RESPONSE,
      Adw.ResponseAppearance.DESTRUCTIVE
    )
    dialog.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        dialog,
        self.mainframe.on_action_save_pressed,
        self.mainframe.create_new_buffer,
      )
    )
  
  def alert_close_unsaved_buffer(self):
    dialog = self._create_dialog("Unsaved changes", "Buffer was modified, save changes before closing?")
    dialog.set_response_appearance(
      self.NO_RESPONSE,
      Adw.ResponseAppearance.DESTRUCTIVE
    )
    dialog.choose(
      parent=self.mainframe,
      callback=self.__get_unsaved_buffer_alert_result(
        dialog,
        self.mainframe.on_action_save_pressed,
        self.mainframe.application.quit,
      )
    )
  
