from gi.repository import Gtk

class StatusDisplay(Gtk.Label):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.actions = []
    self.set_selectable(False)
    self.set_single_line_mode(True)
    self.set_halign(Gtk.Align.END)
    self.set_hexpand(True)
    self.set_margin_start(30)
    self.set_margin_end(10)

  def update(self, text):
    if text != "":
      self.actions.append(text)
    self.set_markup_with_mnemonic(text)