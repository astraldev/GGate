# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import cairo, os
from glogic import const
from glogic.Utils import cairo_paths
from glogic import Preference
from glogic.Utils import get_components_rect
from gi.repository import Gtk, Pango, PangoCairo
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

def save_image_dialog(parent):
	chooser = Gtk.FileChooserDialog(_("Save as image"), parent, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT), flags=Gtk.DialogFlags.MODAL)
	chooser.set_transient_for(parent)
	chooser.set_modal(True)
	add_image_filters(chooser)
	while True:
		if chooser.run() == Gtk.ResponseType.ACCEPT:
			filepath = chooser.get_filename()
			filter_name = chooser.get_filter().get_name()
			if filter_name == const.pngfile_text:
				if not "." in os.path.basename(filepath):
					filepath += ".png"
			elif filter_name == const.svgfile_text:
				if not "." in os.path.basename(filepath):
					filepath += ".svg"
			elif filter_name == const.pdffile_text:
				if not "." in os.path.basename(filepath):
					filepath += ".pdf"
			elif filter_name == const.psfile_text:
				if not "." in os.path.basename(filepath):
					filepath += ".ps"
			else:
				chooser.destroy()
				return None

			if os.path.exists(filepath):
				dialog = Gtk.MessageDialog(chooser, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, _("Overwrite to the existing file?"))
				dialog.format_secondary_text(_("The file already exist. Overwrite it?"))
				retval = dialog.run()
				dialog.destroy()
				if retval == Gtk.ResponseType.NO:
					continue

		else:
			chooser.destroy()
			return None
		break
	chooser.destroy()
	return (filepath, filter_name)

def save_schematics_as_image(circuit, running, parent):
	choosedata = save_image_dialog(parent)
	if choosedata is None:
		return
	filepath = choosedata[0]
	filter_name = choosedata[1]

	settingsdialog = SaveSchematicsImageDialog(running, parent)
	if settingsdialog.run() == Gtk.ResponseType.CANCEL:
		settingsdialog.destroy()
		return

	scale = settingsdialog.scale_spin.get_value()
	mergin = settingsdialog.mergin_spin.get_value()
	drawvoltage = settingsdialog.voltstate_check.get_active() if running else False
	crect = get_components_rect(circuit.components)

	settingsdialog.destroy()
	width = (crect[2] - crect[0] + 1) * scale + mergin * 2 + 1
	height = (crect[3] - crect[1] + 1) * scale + mergin * 2 + 1

	if filter_name == const.pngfile_text:
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
	elif filter_name == const.svgfile_text:
		surface = cairo.SVGSurface(filepath, width, height)
	elif filter_name == const.pdffile_text:
		surface = cairo.PDFSurface(filepath, width, height)
	elif filter_name == const.psfile_text:
		surface = cairo.PSSurface(filepath, width, height)

	cr = cairo.Context(surface)
	cr.translate(mergin, mergin)
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

	settingsdialog.destroy()

def save_timingdiagram_as_image(diagramarea, parent):
	choosedata = save_image_dialog(parent)
	if choosedata is None:
		return
	filepath = choosedata[0]
	filter_name = choosedata[1]

	settingsdialog = SaveTimingDiagramDialog(parent)
	if settingsdialog.run() == Gtk.ResponseType.CANCEL:
		settingsdialog.destroy()
		return

	scale = settingsdialog.scale_spin.get_value()

	settingsdialog.destroy()
	width = (diagramarea.diagram_width + diagramarea.name_width) * scale
	height = diagramarea.img_height * scale
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
	diagramarea.draw_names(cr)
	cr.translate(diagramarea.name_width, 0)
	diagramarea.draw_diagrams(cr)

	if filter_name == const.pngfile_text:
		surface.write_to_png(filepath)
	elif filter_name == const.svgfile_text:
		surface.finish()
	elif filter_name == const.pdffile_text:
		surface.finish()
	elif filter_name == const.psfile_text:
		surface.finish()

	settingsdialog.destroy()

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
			if not (c[1], c[2]) in circuit.net_no_dot:
				cr.rectangle(c[1]-1.5, c[2]-1.5, 3, 3)
			elif not (c[3], c[4]) in circuit.net_no_dot:
				cr.rectangle(c[3]-1.5, c[4]-1.5, 3, 3)
	cr.fill()

class SaveSchematicsImageDialog(Gtk.Dialog):
	def __init__(self, running, parent):
		Gtk.Dialog.__init__(self, _("Save as image"), parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		hbox = Gtk.Box()
		hbox.pack_start(Gtk.Label(_("Scale:")), False, False, 3)
		self.scale_spin = Gtk.SpinButton()
		self.scale_spin.set_increments(1, 10)
		self.scale_spin.set_range(0.1, 10)
		self.scale_spin.set_digits(2)
		self.scale_spin.set_value(1.0)
		hbox.pack_start(self.scale_spin, False, False, 3)
		vbox.pack_start(hbox, False, False, 3)

		hbox = Gtk.Box()
		hbox.pack_start(Gtk.Label(_("Mergin:")), False, False, 3)
		self.mergin_spin = Gtk.SpinButton()
		self.mergin_spin.set_increments(1, 10)
		self.mergin_spin.set_range(0, 100)
		self.mergin_spin.set_value(5)
		hbox.pack_start(self.mergin_spin, False, False, 3)
		vbox.pack_start(hbox, False, False, 3)

		if running:
			hbox = Gtk.Box()
			hbox.pack_start(Gtk.Label(_("Draw voltage states:")), False, False, 3)
			self.voltstate_check = Gtk.CheckButton("")
			hbox.pack_start(self.voltstate_check, False, False, 3)
			vbox.pack_start(hbox, False, False, 3)

		box = self.get_content_area()
		box.add(vbox)
		self.show_all()

class SaveTimingDiagramDialog(Gtk.Dialog):
	def __init__(self, parent):
		Gtk.Dialog.__init__(self, _("Save as image"), parent, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		hbox = Gtk.Box()
		hbox.pack_start(Gtk.Label(_("Scale:")), False, False, 3)
		self.scale_spin = Gtk.SpinButton()
		self.scale_spin.set_increments(1, 10)
		self.scale_spin.set_range(0.1, 10)
		self.scale_spin.set_digits(2)
		self.scale_spin.set_value(1.0)
		hbox.pack_start(self.scale_spin, False, False, 3)
		vbox.pack_start(hbox, False, False, 3)

		box = self.get_content_area()
		box.add(vbox)
		self.show_all()
