# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from ggate.const import definitions as const
from gi.repository import Gtk, GObject
from gettext import gettext as _

class PropertyWindow(Gtk.Dialog):

  __gsignals__ = {
    'property-changed': (GObject.SIGNAL_RUN_FIRST, None, ()),
    'window-hidden': (GObject.SIGNAL_RUN_LAST, None, ())
  }

  def __init__(self):

    self.title = _("Properties")
    Gtk.Window.__init__(self, title=self.title)
    self.set_resizable(True)
    self.set_size_request(310, -1)

    self.vbox = None

    self.prop_controls = []
    self.old_values = []
  
    self.connect("close-request", self.on_window_delete)

  def on_apply_btn_clicked(self, setter=False, *widget):
    values = []
    i = 0

    if self.component is None: return
    
    for p in self.component.properties:
      if isinstance(p[1], tuple):
        if p[1][0] == const.property_select:
          values.append(self.prop_controls[i].get_active())

        elif p[1][0] == const.property_int:
          values.append(int(self.prop_controls[i].get_value()))
          self.prop_controls[i].update()

        elif p[1][0] == const.property_float:
          values.append(self.prop_controls[i].get_value())
          self.prop_controls[i].update()
          
        else:
          values.append(self.prop_controls[i].get_text())
      elif p[1] == const.property_bool:
        values.append(self.prop_controls[i].get_active())
      else:
        i -= 1
      i += 1

    if self.component.propertyChanged(values):

      def _response(widget, *args): widget.close()

      dialog = Gtk.MessageDialog()
      dialog.set_transient_for(self)
      dialog.set_modal(True)
      dialog.add_button("Ok", Gtk.ButtonsType.OK)
      dialog.set_markup(_("Set values are invalid."))

      dialog.present()
      dialog.connect('response', _response)

    else:

      self.component.values = values
      self.component.set_rot_props()
    
    self.emit("property-changed")

  def setComponent(self, component):
     
    if component is None:
      return

    self.component = component
    if self.vbox is not None:
      self.set_child(None)

    self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    if component is None:
      label = Gtk.Label(label=_("Please select a component to edit properties."))
      self.vbox.append(label)
      label.set_vexpand(True)
      label.set_hexpand(True)
      label.set_margin_bottom(15)
      label.set_margin_top(15)
      label.set_margin_end(15)
      label.set_margin_start(15)
      
      self.set_title(self.title)

    else:

      self.set_title("%s - %s" % (self.title, component.description))

      if len(component.properties) != 0:
        layout = Gtk.ListBox()
        i = 0
        # Create property editor
        self.prop_controls = []
        for (j, p) in enumerate(component.properties):
          caption = Gtk.Label(label=p[0])
          caption.set_margin_start(2)
          caption.set_margin_top(1)

          has_property = True

          if isinstance(p[1], tuple):
            if p[1][0] == const.property_select:
              ctrl = Gtk.ComboBoxText()
              choices = p[1][1:]
              for choice in choices:
                ctrl.append_text(choice)
              ctrl.set_active(self.component.values[i])
              ctrl.set_halign(Gtk.Align.START)
              ctrl.set_hexpand(True)
              ctrl.connect("changed", self.on_apply_btn_clicked)

            elif p[1][0] == const.property_int:
              ctrl = Gtk.SpinButton()
              ctrl.set_increments(1, 10)
              ctrl.set_halign(Gtk.Align.START)
              ctrl.set_hexpand(True)
              ctrl.set_range(p[1][1], p[1][2])
              ctrl.set_value(component.values[i])
              ctrl.connect("value-changed", self.on_apply_btn_clicked)
              # ctrl.set_size_request(p[1][3], -1)

            elif p[1][0] == const.property_float:
              ctrl = Gtk.SpinButton()
              ctrl.set_increments(1, 10)
              ctrl.set_halign(Gtk.Align.START)
              ctrl.set_hexpand(True)
              ctrl.set_range(p[1][1], p[1][2])
              ctrl.set_digits(p[1][3] if p[1][3] < 3 else 2)
              ctrl.set_value(component.values[i])
              ctrl.connect("value-changed", self.on_apply_btn_clicked)
              # ctrl.set_size_request(p[1][4], -1)

            else:
              ctrl = Gtk.Entry()
              ctrl.set_text(component.values[i])
              ctrl.set_halign(Gtk.Align.START)
              ctrl.set_hexpand(True)
              ctrl.connect("activate", self.on_apply_btn_clicked)
              ctrl.set_width_chars(p[1][1])

          elif p[1] == const.property_bool:
            ctrl = Gtk.CheckButton("")
            ctrl.set_halign(Gtk.Align.START)
            ctrl.set_hexpand(True)
            ctrl.set_active(component.values[i])
            ctrl.connect("toggled", self.on_apply_btn_clicked)

          else:
            ctrl = Gtk.Label(label='')
            i -= 1
            has_property = False
          i += 1

          propbox = Gtk.ListBoxRow()
          propbox.set_activatable(False)

          ctrl.set_margin_top(3)
          ctrl.set_margin_bottom(3)
          ctrl.set_margin_end(3)
          ctrl.set_halign(Gtk.Align.START)
          ctrl.set_size_request(60, -1)


          if has_property:
            self.prop_controls.append(ctrl)

          _label = Gtk.Label(label=p[2])
          _label.set_margin_top(3)
          _label.set_margin_bottom(3)
          _label.set_margin_start(3)
          _label.set_margin_end(3)

          if isinstance(ctrl, Gtk.Label):
            if ctrl.get_text() == '':
              caption = Gtk.Label()
              caption.set_markup(f'<b>{p[0]}</b>')
              caption.set_margin_top(5)
              caption.set_margin_bottom(5)
              caption.set_margin_start(2)
              caption.set_margin_end(2)

          _list_prop_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
          _list_prop_row.append(ctrl)

          _list_prop_row.append(_label)
          # _list_prop_row.set_halign(Gtk.Align.START)
          _list_prop_row.set_hexpand(True)
          caption.set_hexpand(True)

          _list_box_row = Gtk.Box()
          _list_box_row.append(caption)
          _list_box_row.append(_list_prop_row)

          caption.set_size_request(100, -1)

          _list_prop_row.set_size_request(90, -1)

          propbox.set_child(_list_box_row)
          layout.append(propbox)
        
        frame = Gtk.Frame()
        frame.set_child(layout)
        layout.add_css_class('view')
        layout.add_css_class('rich-list')
        layout.set_selection_mode(Gtk.SelectionMode.NONE)
        self.vbox.append(frame)

        frame.set_margin_top(10)
        frame.set_margin_bottom(10)
        frame.set_margin_start(10)
        frame.set_margin_end(10)

      else:
        _label = Gtk.Label(label=_("This component has no property."))
        self.vbox.append(_label)
        _label.set_margin_top(15)
        _label.set_margin_end(15)
        _label.set_margin_start(15)
        _label.set_margin_bottom(15)
    
    # self.on_apply_btn_clicked(True)

    self.set_child(self.vbox)
    self.vbox.show()
    self.queue_resize()

  def on_window_delete(self, *args):
    self.emit("window-hidden")
