# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import cairo
import os
from ggate.const import definitions as const
from ggate.Utils import cairo_paths
from ggate import Preference
from ggate.Utils import get_components_rect
from gi.repository import Gtk, PangoCairo
from gettext import gettext as _


def add_image_filters(dialog):
  filter_png = Gtk.FileFilter()
  filter_png.set_name(const.pngfile_text)
  filter_png.add_pattern("*.png")
  dialog.add_filter(filter_png)
  filter_svg = Gtk.FileFilter()
  filter_svg.set_name(const.svgfile_text)
  filter_svg.add_pattern("*.svg")
  dialog.add_filter(filter_svg)
  filter_pdf = Gtk.FileFilter()
  filter_pdf.set_name(const.pdffile_text)
  filter_pdf.add_pattern("*.pdf")
  dialog.add_filter(filter_pdf)
  filter_ps = Gtk.FileFilter()
  filter_ps.set_name(const.psfile_text)
  filter_ps.add_pattern("*.ps")
  dialog.add_filter(filter_ps)

def save_image_dialog(parent, handler):

  chooser = Gtk.FileChooserDialog()
  chooser.set_title(_("Save as image"))
  chooser.set_transient_for(parent)
  chooser.set_action(Gtk.FileChooserAction.SAVE)
  chooser.add_button('Cancel', Gtk.ResponseType.CANCEL)
  chooser.add_button('Save', Gtk.ResponseType.ACCEPT)
  chooser.set_modal(True)
  add_image_filters(chooser)

  def response(dialog, response):

    if response == Gtk.ResponseType.ACCEPT:
      filepath = chooser.get_file().get_path()
      filter_name = chooser.get_filter().get_name()

      if filter_name == const.pngfile_text:
        if "." not in os.path.basename(filepath):
          filepath += ".png"
      elif filter_name == const.svgfile_text:
        if "." not in os.path.basename(filepath):
          filepath += ".svg"
      elif filter_name == const.pdffile_text:
        if "." not in os.path.basename(filepath):
          filepath += ".pdf"
      elif filter_name == const.psfile_text:
        if "." not in os.path.basename(filepath):
          filepath += ".ps"
      else:
        dialog.close()
        return None

      dialog.close()
      handler((filepath, filter_name))
    else:
      dialog.close()
    

  chooser.connect('response', response)
  chooser.present()

def save_schematics_as_image(circuit, running, parent):

  def handler(choosedata):
    filepath = choosedata[0]
    filter_name = choosedata[1]

    settingsdialog = SaveSchematicsImageDialog(running, parent)
    settingsdialog.connect('response', _save_schematics_as_image_response, (running, circuit, filter_name, filepath))
    settingsdialog.present()

  save_image_dialog(parent, handler)

def _save_schematics_as_image_response(settingsdialog, response, content):

  running, circuit, filter_name, filepath = content
  if response == Gtk.ResponseType.CANCEL:
    settingsdialog.close()
    return

  scale = settingsdialog.scale_spin.get_value()
  margin = settingsdialog.margin_spin.get_value()
  drawvoltage = settingsdialog.voltstate_check.get_active() if running else False
  crect = get_components_rect(circuit.components)

  settingsdialog.close()
  width = (crect[2] - crect[0] + 1) * scale + margin * 2 + 1
  height = (crect[3] - crect[1] + 1) * scale + margin * 2 + 1

  if filter_name == const.pngfile_text:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
  elif filter_name == const.svgfile_text:
    surface = cairo.SVGSurface(filepath, width, height)
  elif filter_name == const.pdffile_text:
    surface = cairo.PDFSurface(filepath, width, height)
  elif filter_name == const.psfile_text:
    surface = cairo.PSSurface(filepath, width, height)

  cr = cairo.Context(surface)
  cr.translate(margin, margin)
  cr.scale(scale, scale)
  cr.translate(int(-crect[0]), int(-crect[1]))
  draw_schematics_for_file(cr, circuit, drawvoltage)

  if filter_name == const.pngfile_text:
    surface.write_to_png(filepath)
  elif filter_name == const.svgfile_text:
    surface.finish()
  elif filter_name == const.pdffile_text:
    surface.finish()
  elif filter_name == const.psfile_text:
    surface.finish()

  settingsdialog.close()

  settingsdialog.parent.statusbar.push(0, "Image schematics saved..")

def save_timing_diagram_as_image(diagram_area, parent):

  def handler(data):
    filepath = data[0]
    filter_name = data[1]

    settingsdialog = SaveTimingDiagramDialog(parent)
    settingsdialog.connect('response', _save_timing_diagram_as_image_response, (diagram_area, filepath, filter_name))
    settingsdialog.present()


  save_image_dialog(parent, handler)
  
def _save_timing_diagram_as_image_response(settingsdialog, response, content):
  diagram_area, filepath, filter_name = content

  if response == Gtk.ResponseType.CANCEL:
    settingsdialog.close()
    return

  scale = settingsdialog.scale_spin.get_value()

  settingsdialog.close()

  width = (diagram_area.diagram_width + diagram_area.name_width) * scale
  height = diagram_area.img_height * scale
  if filter_name == const.pngfile_text:
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, int(width), int(height))
  elif filter_name == const.svgfile_text:
    surface = cairo.SVGSurface(filepath, width, height)
  elif filter_name == const.pdffile_text:
    surface = cairo.PDFSurface(filepath, width, height)
  elif filter_name == const.psfile_text:
    surface = cairo.PSSurface(filepath, width, height)

  cr = cairo.Context(surface)
  cr.set_line_width(1.0)
  cr.scale(scale, scale)
  diagram_area.draw_names(cr)
  cr.translate(diagram_area.name_width, 0)
  diagram_area.draw_diagrams(cr)

  if filter_name == const.pngfile_text:
    surface.write_to_png(filepath)
  elif filter_name == const.svgfile_text:
    surface.finish()
  elif filter_name == const.pdffile_text:
    surface.finish()
  elif filter_name == const.psfile_text:
    surface.finish()

  settingsdialog.close()
  settingsdialog.parent.statusbar.push(0, "Timing diagram saved..")

def draw_schematics_for_file(cr, circuit, withlevels):

  cr.translate(0.5, 0.5)
  matrix = cr.get_matrix()
  cr.set_line_width(1.0)
  layout = PangoCairo.create_layout(cr)
  layout.set_font_description(Preference.drawing_font)

  circuit.analyze_connections()
  if withlevels:
    circuit.set_netlevels()

  # Draw net
  for c in circuit.components:
    if c[0] == const.component_net:
      if withlevels:
        for i,net in enumerate(circuit.net_connections):
          if (c[1], c[2]) in net:
            if circuit.net_levels[i] == 1:
              cr.set_source(Preference.highlevel_color)
            elif circuit.net_levels[i] == 0:
              cr.set_source(Preference.lowlevel_color)
            else:
              cr.set_source(Preference.net_color_running)
      else:
        cr.set_source(Preference.net_color_running)

      cairo_paths(cr, (c[1], c[2]), (c[3], c[4]))
      cr.stroke()

  # Draw component
  for c in circuit.components:
    if c[0] != const.component_net:
      cr.translate(c[1].pos_x, c[1].pos_y)
      m = cairo.Matrix(xx = c[1].matrix[0], xy = c[1].matrix[1], yx = c[1].matrix[2], yy = c[1].matrix[3])
      cr.set_matrix(m.multiply(cr.get_matrix()))
      cr.set_source(Preference.component_color_running)
      c[1].drawComponent(cr, layout)
      if(withlevels):
        c[1].drawComponentRunOverlap(cr, layout)
      else:
        c[1].drawComponentEditOverlap(cr, layout)
      cr.set_matrix(matrix)

  # Draw terminal of nets
  cr.set_source(Preference.terminal_color_running)
  for c in circuit.components:
    if c[0] == const.component_net:
      if (c[1], c[2]) not in circuit.net_no_dot:
        cr.rectangle(c[1]-1.5, c[2]-1.5, 3, 3)
      elif (c[3], c[4]) not in circuit.net_no_dot:
        cr.rectangle(c[3]-1.5, c[4]-1.5, 3, 3)
  cr.fill()

class SaveSchematicsImageDialog(Gtk.Dialog):
  def __init__(self, running, parent):
    Gtk.Dialog.__init__(self)
    self.set_title(_("Save as image"))
    self.set_transient_for(parent)
    self.parent = parent
    self.set_application(parent.application)
    self.add_button("Cancel", Gtk.ResponseType.CANCEL)
    ok_button = self.add_button("Ok", Gtk.ResponseType.OK)
    ok_button.add_css_class("suggested-action")

    self.set_size_request(200, 150)
    self.set_resizable(False)
    
    frame = Gtk.Frame()
    vbox = Gtk.ListBox()
    vbox.add_css_class("view")

    frame.set_child(vbox)

    row_box = Gtk.ListBoxRow()

    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

    scale_label = Gtk.Label(label=_("Scale:"))

    scale_label.set_margin_top(3)
    scale_label.set_margin_end(10)
    scale_label.set_margin_start(3)
    scale_label.set_margin_bottom(3)

    scale_label.set_size_request(90, -1)

    hbox.append(scale_label)

    self.scale_spin = Gtk.SpinButton()
    self.scale_spin.set_increments(1, 10)
    self.scale_spin.set_range(0.1, 10)
    self.scale_spin.set_digits(2)
    self.scale_spin.set_value(1.0)

    self.scale_spin.set_margin_top(3)
    self.scale_spin.set_margin_end(3)
    self.scale_spin.set_margin_start(3)
    self.scale_spin.set_margin_bottom(3)

    hbox.append(self.scale_spin)

    hbox.set_margin_top(3)
    hbox.set_margin_end(3)
    hbox.set_margin_start(3)
    hbox.set_margin_bottom(3)

    row_box.set_child(hbox)

    vbox.append(row_box)

    row_box = Gtk.ListBoxRow()

    hbox = Gtk.Box()
    margin_label = Gtk.Label(label=_("Margin:"))

    margin_label.set_margin_top(3)
    margin_label.set_margin_end(10)
    margin_label.set_margin_start(3)
    margin_label.set_margin_bottom(3)

    margin_label.set_size_request(90, -1)

    hbox.append(margin_label)

    self.margin_spin = Gtk.SpinButton()
    self.margin_spin.set_increments(1, 10)
    self.margin_spin.set_range(0, 100)
    self.margin_spin.set_value(5)

    self.margin_spin.set_margin_top(3)
    self.margin_spin.set_margin_end(3)
    self.margin_spin.set_margin_start(3)
    self.margin_spin.set_margin_bottom(3)

    hbox.append(self.margin_spin)
    hbox.set_margin_top(3)
    hbox.set_margin_end(3)
    hbox.set_margin_start(3)
    hbox.set_margin_bottom(3)

    row_box.set_child(hbox)

    vbox.append(row_box)

    if running:

      row_box = Gtk.ListBoxRow()

      hbox = Gtk.Box()
      voltage_state_label = Gtk.Label(label=_("Draw voltage states:"))
      voltage_state_label.set_margin_top(3)
      voltage_state_label.set_margin_end(3)
      voltage_state_label.set_margin_start(3)
      voltage_state_label.set_margin_bottom(3)

      hbox.append(voltage_state_label)

      self.voltstate_check = Gtk.CheckButton()

      self.voltstate_check.set_margin_top(3)
      self.voltstate_check.set_margin_end(3)
      self.voltstate_check.set_margin_start(3)
      self.voltstate_check.set_margin_bottom(3)

      hbox.append(self.voltstate_check)

      hbox.set_margin_top(3)
      hbox.set_margin_end(3)
      hbox.set_margin_start(3)
      hbox.set_margin_bottom(3)

      row_box.set_child(hbox)

      vbox.append(row_box)

    box = self.get_content_area()
    frame.set_vexpand(True)
    frame.set_hexpand(True)
    frame.set_halign(Gtk.Align.FILL)
    frame.set_valign(Gtk.Align.FILL)

    frame.set_margin_start(3)
    frame.set_margin_bottom(3)
    frame.set_margin_top(3)
    frame.set_margin_end(3)

    box.append(frame)

class SaveTimingDiagramDialog(Gtk.Dialog):
  def __init__(self, parent):
    Gtk.Dialog.__init__(self)
    self.set_title(_("Save as image"))
    self.set_transient_for(parent)
    self.parent = parent
    self.add_button('Cancel', Gtk.ResponseType.CANCEL)
    ok_button = self.add_button("Ok", Gtk.ResponseType.OK)
    ok_button.add_css_class("suggested-action")

    self.set_size_request(200, 150)
    self.set_resizable(False)

    frame = Gtk.Frame()
    vbox = Gtk.ListBox()
    vbox.add_css_class("view")

    frame.set_child(vbox)

    row_box = Gtk.ListBoxRow()

    hbox = Gtk.Box()
    scale_label = Gtk.Label(label=_("Scale:"))

    scale_label.set_margin_top(3)
    scale_label.set_margin_end(10)
    scale_label.set_margin_start(3)
    scale_label.set_margin_bottom(3)

    scale_label.set_size_request(90, -1)

    hbox.append(scale_label)
    self.scale_spin = Gtk.SpinButton()
    self.scale_spin.set_increments(1, 10)
    self.scale_spin.set_range(0.1, 10)
    self.scale_spin.set_digits(2)
    self.scale_spin.set_value(1.0)

    self.scale_spin.set_margin_top(3)
    self.scale_spin.set_margin_end(3)
    self.scale_spin.set_margin_start(3)
    self.scale_spin.set_margin_bottom(3)

    hbox.append(self.scale_spin)


    hbox.set_margin_top(3)
    hbox.set_margin_end(3)
    hbox.set_margin_start(3)
    hbox.set_margin_bottom(3)

    row_box.set_child(hbox)

    vbox.append(row_box)

    box = self.get_content_area()
    frame.set_vexpand(True)
    frame.set_hexpand(True)
    frame.set_halign(Gtk.Align.FILL)
    frame.set_valign(Gtk.Align.FILL)

    frame.set_margin_start(3)
    frame.set_margin_bottom(3)
    frame.set_margin_top(3)
    frame.set_margin_end(3)

    box.append(frame)
