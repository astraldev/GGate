# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

from asyncio import constants
import gi

import copy, os, sys, webbrowser
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio
from glogic import config, const
from glogic.Exporter import save_schematics_as_image
from gettext import gettext as _
from glogic.DrawArea import DrawArea
from glogic.ComponentView import ComponentView
from glogic.CircuitManager import CircuitManager
from glogic.PropertyWindow import PropertyWindow
from glogic.PreferencesWindow import PreferencesWindow
from glogic import Preference
from glogic.Components import *
from glogic.TimingDiagramWindow import TimingDiagramWindow
from glogic.ComponentConverter import components_to_string, string_to_components

themed_icons = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
themed_icons.add_search_path(config.DATADIR+"/images")

class MainFrame(Gtk.ApplicationWindow):
	def __init__(self, *args, **kwargs):
		Gtk.Window.__init__(self, title="%s - %s" % (const.text_notitle, const.app_name), **kwargs)
		self.application = kwargs['application']
		self.running_mode = False
		self.pause_running_mode = False
		self.clicked_on_pause = False

		self.circuit = CircuitManager()
		self.circuit.connect("title-changed", self.on_circuit_title_changed)
		self.circuit.connect("message-changed", self.on_circuit_message_changed)
		self.circuit.connect("item-unselected", self.on_circuit_item_unselected)
		self.circuit.connect("alert", self.on_circuit_alert)

		Preference.load_settings()


		# Component window
		self.comp_window = ComponentView()
		self.comp_window.connect("component-checked", self.on_comp_checked)
		
		self.create_window()

		# Property window
		self.prop_window = PropertyWindow()
		self.prop_window.set_transient_for(self)
		self.prop_window.connect("window-hidden", self.on_propwindow_hidden)
		self.prop_window.connect("property-changed", self.on_property_changed)

		# Timing diagram window
		self.diagram_window = TimingDiagramWindow(self)

		# Preferences window
		self.pref_window = PreferencesWindow(self)

		# About dialog
		self.about_dialog = Gtk.AboutDialog()
		# self.about_dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(config.DATADIR+"/images/glogic.png"))
		self.about_dialog.set_program_name(const.app_name)
		self.about_dialog.set_version(config.VERSION if config.BZRREV == "" else "%s (+bzr%s)" % (config.VERSION, config.BZRREV))
		self.about_dialog.set_comments(const.description)
		self.about_dialog.set_copyright(const.copyright)
		self.about_dialog.set_website(const.website)
		self.about_dialog.set_license(const.license)
		self.about_dialog.set_authors(const.developer)
		tr_credits = _("translator-credits")
		if tr_credits != "translator-credits":
			self.about_dialog.set_translator_credits(tr_credits)

		self.clipboard = Gdk.Display().get_primary_clipboard()

		if len(sys.argv) >= 2:
			self.circuit.open_file(sys.argv[1])
			self.drawarea.redraw = True
			self.drawarea.queue_draw()

	def set_up_action_bar(self, *args):
		# Rotate Left Action
		self.action_rotleft = Gtk.Button()
		image = Gtk.Image.new_from_icon_name('object-rotate-left-symbolic')
		self.action_rotleft.set_child(image)
		self.action_rotleft.connect('clicked', self.on_action_rotate_left_90)

		self.action_bar.pack_start(self.action_rotleft)

		# Rotate Right Action
		self.action_rotright = Gtk.Button()
		image = Gtk.Image.new_from_icon_name('object-rotate-right-symbolic')
		self.action_rotright.set_child(image)
		self.action_rotright.connect('clicked', self.on_action_rotate_right_90)

		self.action_bar.pack_start(self.action_rotright)

		# Flip Horizontal 
		self.action_fliphori = Gtk.Button()
		image = Gtk.Image.new_from_icon_name('object-flip-horizontal-symbolic')
		self.action_fliphori.set_child(image)
		self.action_fliphori.connect('clicked', self.on_action_flip_horizontally)

		self.action_bar.pack_start(self.action_fliphori)

		# Flip Vertical
		self.action_flipvert = Gtk.Button()
		image = Gtk.Image.new_from_icon_name('object-flip-vertical-symbolic')
		self.action_flipvert.set_child(image)
		self.action_flipvert.connect('clicked', self.on_action_flip_vertically)

		self.action_bar.pack_start(self.action_flipvert)

		# Add Net
		self.action_net = Gtk.ToggleButton()
		image = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(
                        config.DATADIR+"images/add-net.png"))
		self.action_net.set_child(image)
		self.action_net.connect('clicked', self.on_action_net_toggled)
		self.action_bar.pack_start(self.action_net)
		self.action_net.set_active(False)

		self._toggle_run_state = -1
		self._self_toggle = False


	def create_window(self):
		self.set_default_size(640, 400)
		
		paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		menu_xml = """
		<ui>
			<menubar name="MenuBar">
				<menu action="file">
					<menuitem action="new"/>
					<menuitem action="open"/>
					<separator/>
					<menuitem action="save"/>
					<menuitem action="saveas"/>
					<separator/>
					<menuitem action="saveimage"/>
					<separator/>
					<menuitem action="quit"/>
				</menu>
				<menu action="edit">
					<menuitem action="undo"/>
					<menuitem action="redo"/>
					<separator/>
					<menuitem action="cut"/>
					<menuitem action="copy"/>
					<menuitem action="paste"/>
					<menuitem action="delete"/>
					<separator/>
					<menuitem action="property"/>
					<separator/>
					<menuitem action="rotleft"/>
					<menuitem action="rotright"/>
					<menuitem action="fliphori"/>
					<menuitem action="flipvert"/>
					<separator/>
					<menuitem action="prefs"/>
				</menu>
				<menu action="add">
					<menuitem action="components"/>
					<menuitem action="net"/>
				</menu>
				<menu action="simulate">
					<menuitem action="run"/>
					<menuitem action="pause-run"/>
					<menuitem action="diagram"/>
				</menu>
				<menu action="help">
					<menuitem action="contents"/>
					<separator/>
					<menuitem action="trans"/>
					<menuitem action="report"/>
					<separator/>
					<menuitem action="about"/>
				</menu>
			</menubar>
			<toolbar name="ToolBar">
				<toolitem action="new" />
				<toolitem action="open" />
				<toolitem action="save" />
				<separator/>
				<toolitem action="undo" />
				<toolitem action="redo" />
				<separator/>
				<toolitem action="components" />
				<toolitem action="net" />
				<separator/>
				<toolitem action="run" />
				<toolitem action="pause-run" />
			</toolbar>
		</ui>
		"""
		actions = {
			"-new"        : ['Gtk.STOCK_NEW', _("_New"), "<Control>N", _("Close this circuit and create a new one."), self.on_action_new_pressed],
			"-open"		 : ['Gtk.STOCK_OPEN', _("_Open..."), "<Control>O", _("Close this circuit and open the other one."), self.on_action_open_pressed],
			"-save"		 : ['Gtk.STOCK_SAVE', _("_Save"), "<Control>S", _("Save this circuit."), self.on_action_save_pressed],
			"-saveas"     : ['Gtk.STOCK_SAVE_AS', _("Save _As..."), "<Shift><Control>S", _("Save this circuit with a new name."), self.on_action_saveas_pressed],
			"-saveimage"  : [None, _("Save as _image..."), None, _("Save schematics as image file."), self.on_action_save_image],
			"-quit"		 : ['Gtk.STOCK_QUIT', _("_Quit"), "<Control>Q", _("Close this application."), self.on_action_quit_pressed],
			"-undo"		 : ['Gtk.STOCK_UNDO', _("_Undo"), "<Control>Z", _("Undo the previous action."), self.on_action_undo_pressed],
			"-redo"		 : ['Gtk.STOCK_REDO', _("_Redo"), "<Shift><Control>Z", _("Redo the action that you have canceled."), self.on_action_redo_pressed],
			"-cut"        : ['Gtk.STOCK_CUT', _("Cu_t"), "<Control>X", _("Cut selected components."), self.on_action_cut_pressed],
			"-copy"		 : ['Gtk.STOCK_COPY', _("_Copy"), "<Control>C", _("Copy selected components."), self.on_action_copy_pressed],
			"-paste"      : ['Gtk.STOCK_PASTE', _("_Paste"), "<Control>V", _("Paste copied components."), self.on_action_paste_pressed],
			"-delete"     : ['Gtk.STOCK_DELETE', _("_Delete"), "Delete", _("Delete selected components."), self.on_action_delete_pressed],
			"-prefs"      : ['Gtk.STOCK_PREFERENCES', _("Pr_eferences"), None, _("Set preferences of this application."), self.on_action_prefs_pressed],
			"-contents"   : ['Gtk.STOCK_HELP', _("_Contents"), None, _("Show the help browser."), self.on_action_show_help],
			"-trans"      : [None, _("Translate This Application..."), None, _("Connect to the Launchpad website to help translate this application."), self.on_action_translate_pressed],
			"report"     : [None, _("Report a Problem..."), None, _("Connect to the Launchpad website to report a problem of this application."), self.on_action_bug_pressed],
			"-about"      : ['Gtk.STOCK_ABOUT', _("_About"), None, _("Show about dialog."), self.on_action_about_pressed],
			"-file"		 : [None, _("_File")],
			"-edit"		 : [None, _("_Edit")],
			"-add"        : [None, _("_Add")],
			"-simulate"   : [None, _("_Simulate")],
			"-help"		 : [None, _("_Help")]
		}
		toggle_actions = [
			("property",   'properties-icon', _("_Properties"), "<Control>P", _("Show property dialog."), self.on_action_property_toggled),
			("components", None, _("_Components..."), "<Control>A", _("Show components window."), self.on_btn_add_components_toggled),
			("net",        None, _("_Net"), "<Control>E", _("Add nets to this circuit."), self.on_action_net_toggled),
			# ("run",        'play-icon', _("_Run"), "F5", _("Run and simulate this circuit."), self.on_action_run_),
			("diagram",    None, _("_Timing Diagram"), "<Control>T", _("Show timing diagram window."), self.on_action_diagram_pressed),
		]

		# actiongroup.add_actions(actions)
		# actiongroup.add_toggle_actions(toggle_actions)

		# self.action_undo = actiongroup.get_action("undo")
		# self.action_redo = actiongroup.get_action("redo")
		# self.action_cut = actiongroup.get_action("cut")
		# self.action_copy = actiongroup.get_action("copy")
		# self.action_paste = actiongroup.get_action("paste")
		# self.action_delete = actiongroup.get_action("delete")
		# self.action_property = actiongroup.get_action("property")
		# self.action_rotleft = actiongroup.get_action("rotleft")
		# self.action_rotright = actiongroup.get_action("rotright")
		# self.action_fliphori = actiongroup.get_action("fliphori")
		# self.action_flipvert = actiongroup.get_action("flipvert")
		# self.action_components = actiongroup.get_action("components")
		# self.action_net = actiongroup.get_action("net")
		# self.action_run = actiongroup.get_action("run")
		# self.action_pause_run = actiongroup.get_action("pause-run")
		# self.action_diagram = actiongroup.get_action("diagram")

		# self.action_undo.set_sensitive(False)
		# self.action_redo.set_sensitive(False)
		# self.action_diagram.set_sensitive(False)
		# self.action_pause_run.set_sensitive(False)

		# uimanager = Gtk.UIManager()
		# uimanager.add_ui_from_string(menu_xml)
		# self.add_accel_group(uimanager.get_accel_group())
		# uimanager.insert_action_group(actiongroup)

		# action = actiongroup.get_action("components")
		# action.set_icon_name("add-component")
		# action = actiongroup.get_action("net")
		# action.set_icon_name("add-net")

		# Menu bar

		# TODO: Remove the menu bar and put a menu button on the WindowTitleBar With all the content On it
		# menubar = uimanager.get_widget("/MenuBar")
		# box.pack_start(menubar, False, False, 0)

		# # Tool bar

		# # TODO: Remove the tool bar and Create a pane for the components then Create a button on the left part of the title bar for run and pause
		# toolbar = uimanager.get_widget("/ToolBar")
		# toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
		# box.pack_start(toolbar, False, False, 0)

		# Menu Button

		self.menu_button = Gtk.MenuButton.new()
		self.menu_button.set_direction(Gtk.ArrowType.NONE)

		# Menu Popover

		_menu_builder = Gtk.Builder.new_from_string(const.menu_xml , -1)
		_menu = _menu_builder.get_object("app-menu")

		self.popover = Gtk.PopoverMenu.new_from_model(_menu)
		self.menu_button.set_popover(self.popover)

		# play pause button
		play_button = Gtk.ToggleButton()
		play_image = Gtk.Image.new_from_icon_name('media-playback-start-symbolic')
		play_button.connect('toggled', self.on_action_run_toggled)
		play_button.connect('clicked', self.on_action_run_clicked)

		play_button.set_child(play_image)


		# Header Bar
		self.header_bar = Gtk.HeaderBar()
		self.header_bar.pack_start(self.menu_button)
		self.header_bar.pack_end(play_button)

		self.set_titlebar(self.header_bar)

		# Draw area
		self.drawarea = DrawArea(self)
		self.drawarea.circuit = self.circuit
		box.append(self.drawarea)
		self.drawarea.set_vexpand(True)
		self.drawarea.set_hexpand(True)

		# Status bar
		self.statusbar = Gtk.Statusbar()
		self.action_bar = Gtk.ActionBar()

		self.set_up_action_bar()

		action_bar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

		action_bar_box.append(self.action_bar)
		action_bar_box.append(self.statusbar)

		self.action_bar.set_hexpand(False)
		# self.action_bar.set_halign(Gtk.Align.END)

		self.statusbar.set_hexpand(True)
		self.statusbar.set_halign(Gtk.Align.FILL)

		box.append(action_bar_box)

		# component box
		paned.set_start_child(self.comp_window)
		paned.set_end_child(box)

		box.set_vexpand(True)

		self.comp_window.set_vexpand(False)
		paned.set_wide_handle(False)
		paned.set_resize_start_child(False)
		paned.set_shrink_start_child(False)

		self.set_child(paned)

		# Connect events
		self.connect("close-request", self.on_window_delete)

		# Reopen it later.
		#self.disable_edit_actions()

	def on_action_about_pressed(self, widget):
		self.about_dialog.run()
		self.about_dialog.hide()

	def on_action_new_pressed(self, widget):
		if self.check_modified():
			return
		if self.drawarea.drag_enabled:
			return

		self.set_title("%s - %s" % (const.text_notitle, const.app_name))
		self.reset_frame()
		self.circuit.reset_circuit()
		self.drawarea.nearest_component = None
		self.drawarea.redraw = True
		self.drawarea.queue_draw()

	def add_filters(self, dialog):
		filter_wxl = Gtk.FileFilter()
		filter_wxl.set_name(const.glcfile_text)
		filter_wxl.add_pattern("*.glc")
		dialog.add_filter(filter_wxl)
		filter_any = Gtk.FileFilter()
		filter_any.set_name(const.anyfile_text)
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)

	def reset_frame(self):
		# reset prop window
		self.statusbar.push(0, "")
		self.drawarea.set_component(const.component_none)
		self.action_undo.set_sensitive(False)
		self.action_redo.set_sensitive(False)
		self.disable_edit_actions()
		self.action_diagram.set_sensitive(False)
		self.action_net.set_active(False)
		self.action_run.set_active(False)
		# self.action_diagram.set_active(False)
		self.diagram_window.destroy()
		self.diagram_window = TimingDiagramWindow(self)

	def on_action_open_pressed(self, *args):
		if self.check_modified():
			return
		while True:
			dialog = Gtk.FileChooserDialog(_("Open file"), self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
			dialog.set_transient_for(self)
			self.add_filters(dialog)
			if dialog.run() == Gtk.ResponseType.ACCEPT:
				filepath = dialog.get_filename()
			else:
				break

			if not self.circuit.open_file(filepath):
				self.reset_frame()
				self.drawarea.redraw = True
				self.drawarea.queue_draw()
				break

			dialog.destroy()

		dialog.destroy()

	def overwrite_save(self):
		if self.circuit.filepath == "":
			return self.rename_save()
		else:
			if self.circuit.save_file(self.circuit.filepath):
				return self.rename_save()
			return False

	def rename_save(self):
		chooser = Gtk.FileChooserDialog(_("Save file"), self, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT), flags=Gtk.DialogFlags.MODAL)
		chooser.set_transient_for(self)
		chooser.set_modal(True) 
		self.add_filters(chooser)
		while True:
			if chooser.run() == Gtk.ResponseType.ACCEPT:
				filepath = chooser.get_filename()
				filter_name = chooser.get_filter().get_name()
				if filter_name == const.glcfile_text:
					if not "." in os.path.basename(filepath):
						filepath += ".glc"

				if os.path.exists(filepath):
					dialog = Gtk.MessageDialog(chooser, Gtk.DialogFlags.MODAL, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, _("Overwrite to the existing file?"))
					dialog.format_secondary_text(_("The file already exist. Overwrite it?"))
					retval = dialog.run()
					dialog.destroy()
					if retval == Gtk.ResponseType.NO:
						continue

			else:
				chooser.destroy()
				return True

			if not self.circuit.save_file(filepath):
				chooser.destroy()
				return False

	def on_action_save_pressed(self, *args):
		self.overwrite_save()

	def on_action_saveas_pressed(self, *args):
		self.rename_save()

	def on_action_quit_pressed(self, *args):
		self.application.quit()

	def check_modified(self):
		if self.circuit.need_save:
			dialog = Gtk.MessageDialog(transient_for=self)
			dialog.set_modal(True)
			dialog.add_button('Yes', Gtk.ResponseType.YES)
			dialog.add_button('No', Gtk.ResponseType.NO)
			dialog.set_markup(_("Save the modified schematics?"))
			# dialog.format_secondary_markup(_("The schematics was modifed. Save the changes before closing?"))

			dialog.present()

			dialog.connect('response', self.on_response)
		return False

	def on_response(self, widget, retval, *args):
			if retval == Gtk.ResponseType.YES:
				return self.overwrite_save()
			elif retval == Gtk.ResponseType.NO:
				return False
			else:
				return True

	def on_btn_add_components_toggled(self, widget):
		return

		# if widget.get_active():
		# 	self.comp_window.show_all()
		# else:
		# 	self.comp_window.hide()


	def on_window_delete(self, *args):
		if self.check_modified():
			return True
		return False

	def on_action_net_toggled(self, widget):
		if widget.get_active():
			self.drawarea.netstarted = False
			# self.comp_window.uncheck_all_buttons()
			widget.set_active(True)
			self.drawarea.set_component(const.component_net)
		elif self.drawarea.get_component() == const.component_net:
			self.drawarea.set_component(const.component_none)
		self.drawarea.queue_draw()
		
	def on_action_run_toggled(self, widget, *args):

		if not self._self_toggle:
			self._toggle_run_state += 1

		if self._toggle_run_state == 1 and not self._self_toggle:
			self._self_toggle = True
			return widget.set_active(True)


		if self._toggle_run_state > 2:
			self._toggle_run_state = 0

		self._self_toggle = False
		

	def on_action_run_clicked(self, widget, *args):

		print(self._toggle_run_state)

		if (self._toggle_run_state == 0) or (self._toggle_run_state == 2):
			icon = Gtk.Image.new_from_icon_name('media-playback-pause-symbolic')
			widget.set_child(icon)
		
			if self.drawarea.drag_enabled:
				return
			if self.running_mode:
				self.running_mode = False
				self.clicked_on_pause = False
				if self.circuit.action_count < len(self.circuit.components_history) - 1:
					self.action_redo.set_sensitive(True)
				# self.action_property.set_sensitive(True)
				self.comp_window.set_all_sensitive(True)
				self.action_net.set_sensitive(True)
				# self.action_diagram.set_sensitive(False)
				# self.action_diagram.set_active(False)
				self.diagram_window.hide()
				self.statusbar.push(0, "")
			else:
				self.running_mode = True
				self.circuit.selected_components = []
				# self.action_undo.set_sensitive(False)
				# self.action_redo.set_sensitive(False)
				self.disable_edit_actions()
				# self.action_property.set_sensitive(False)
				# self.action_property.set_active(False)

				self.comp_window.set_all_sensitive(False)

				self.action_net.set_sensitive(False)
				# self.action_net.set_active(False)
				# self.action_diagram.set_sensitive(True)
				self.prop_window.hide()
				self.drawarea.set_component(const.component_none)
				self.drawarea.component_dragged = False
				self.drawarea.drag_enabled = False
				self.drawarea.rect_select_enabled = False
				self.circuit.analyze_connections()
				self.circuit.initialize_logic()
				if not self.circuit.analyze_logic():
					self.diagram_window.diagramarea.createDiagram()
			self.drawarea.redraw = True
			self.drawarea.queue_draw()

		if (self._toggle_run_state == 2) and self.pause_running_mode:
			play_image = Gtk.Image.new_from_icon_name('media-playback-start-symbolic')
			widget.set_child(play_image)
			
			self.pause_running_mode = False
			if not self.circuit.analyze_logic():
				self.diagram_window.diagramarea.createDiagram()
			self.drawarea.queue_draw()
			self.clicked_on_pause = False

		if self._toggle_run_state == 1:
			play_image = Gtk.Image.new_from_icon_name('media-playback-stop-symbolic')
			widget.set_child(play_image)
			self.pause_running_mode = True


	def on_action_cut_pressed(self, widget):
		self.on_action_copy_pressed(widget)
		self.on_action_delete_pressed(widget)

	def on_action_copy_pressed(self, widget):
		self.clipboard.set_text(components_to_string(self.circuit.selected_components), -1)
		self.clipboard.store()

	def on_action_paste_pressed(self, widget):
		str_data = self.clipboard.wait_for_text()
		if str_data != None:
			tmp = string_to_components(str_data)
			if isinstance(tmp, str):
				dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _("Error"))
				dialog.format_secondary_text(tmp)
				dialog.run()
				dialog.destroy()
				return
			else:
				pasted_components = tmp

			if not pasted_components:
				return

			self.drawarea.set_component(const.component_none)
			self.drawarea.set_pasted_components(pasted_components)

	def on_action_undo_pressed(self, widget):
		self.circuit.undo()
		if self.circuit.action_count == 0:
			self.action_undo.set_sensitive(False)
		self.action_redo.set_sensitive(True)
		self.disable_edit_actions()
		self.drawarea.redraw = True
		self.drawarea.queue_draw()

	def on_action_redo_pressed(self, widget):
		self.circuit.redo()
		self.action_undo.set_sensitive(True)
		if self.circuit.action_count == len(self.circuit.components_history) - 1:
			self.action_redo.set_sensitive(False)
		self.disable_edit_actions()
		self.drawarea.redraw = True
		self.drawarea.queue_draw()

	def on_action_delete_pressed(self, widget):
		self.circuit.remove_selected_component()
		self.drawarea.nearest_component = None
		self.drawarea.preselected_component = None
		self.circuit.push_history()
		self.action_undo.set_sensitive(True)
		self.action_redo.set_sensitive(False)
		self.disable_edit_actions()
		self.drawarea.redraw = True
		self.drawarea.queue_draw()

	def on_action_rotate_left_90(self, widget):
		if comp_dict[self.drawarea.get_component()] is None:
			self.circuit.rotate_left_selected_components()
			self.circuit.push_history()
			self.drawarea.redraw = True
		else:
			self.drawarea.rotate_left_picked_components()
		self.drawarea.queue_draw()

	def on_action_rotate_right_90(self, widget):
		if comp_dict[self.drawarea.get_component()] is None:
			self.circuit.rotate_right_selected_components()
			self.circuit.push_history()
			self.drawarea.redraw = True
		else:
			self.drawarea.rotate_right_picked_components()
		self.drawarea.queue_draw()

	def on_action_flip_horizontally(self, widget):
		if comp_dict[self.drawarea.get_component()] is None:
			self.circuit.flip_hori_selected_components()
			self.circuit.push_history()
			self.drawarea.redraw = True
		else:
			self.drawarea.flip_hori_picked_components()
		self.drawarea.queue_draw()

	def on_action_flip_vertically(self, widget):
		if comp_dict[self.drawarea.get_component()] is None:
			self.circuit.flip_vert_selected_components()
			self.circuit.push_history()
			self.drawarea.redraw = True
		else:
			self.drawarea.flip_vert_picked_components()
		self.drawarea.queue_draw()

	def on_action_property_toggled(self, widget):
		if widget.get_active():
			self.drawarea.set_selected_component_to_prop_window()
			self.prop_window.show_all()
		else:
			self.prop_window.hide()

	def on_action_show_help(self, widget):
		Gtk.show_uri(None, const.help, Gdk.CURRENT_TIME)

	def on_action_translate_pressed(self, widget):
		webbrowser.open(const.devel_translate)

	def on_action_bug_pressed(self, widget):
		webbrowser.open(const.devel_bug)

	def on_action_diagram_pressed(self, widget):
		if widget.get_active():
			self.diagram_window.show_all()
		else:
			self.diagram_window.hide()

	def on_action_save_image(self, widget):
		save_schematics_as_image(self.circuit, self.running_mode, self)

	def on_action_prefs_pressed(self, widget):
		self.pref_window.update_dialog()
		if self.pref_window.run() == Gtk.ResponseType.APPLY:
			self.pref_window.apply_settings()
			Preference.save_settings()
			self.drawarea.redraw = True
			self.drawarea.queue_draw()
		self.pref_window.hide()

	def on_comp_checked(self, widget, comp_name):
		if comp_dict[comp_name]:
			self.action_rotleft.set_sensitive(True)
			self.action_rotright.set_sensitive(True)
			self.action_fliphori.set_sensitive(True)
			self.action_flipvert.set_sensitive(True)
		elif not self.circuit.selected_components:
			self.action_rotleft.set_sensitive(False)
			self.action_rotright.set_sensitive(False)
			self.action_fliphori.set_sensitive(False)
			self.action_flipvert.set_sensitive(False)
		if comp_name != const.component_none:
			self.action_net.set_active(False)
		elif self.drawarea.get_component() == const.component_net:
			return
		self.drawarea.set_component(comp_name)
		self.drawarea.queue_draw()

	def on_compwindow_hidden(self, widget):
		self.action_components.set_active(False)

	def on_propwindow_hidden(self, widget):
		return

	def on_property_changed(self, widget):
		self.drawarea.redraw = True
		self.drawarea.queue_draw()
		self.circuit.push_history()
		self.action_undo.set_sensitive(True)

	def on_circuit_title_changed(self, circuit, title):
		self.set_title(title)

	def on_circuit_message_changed(self, circuit, message):
		self.statusbar.push(0, message)

	def on_circuit_item_unselected(self, circuit):
		self.prop_window.setComponent(None)

	def on_circuit_alert(self, circuit, message):
		dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _("Error"))
		dialog.format_secondary_text(message)
		dialog.run()
		dialog.destroy()

	def disable_edit_actions(self):
		if comp_dict[self.drawarea.get_component()] is None:
			self.action_rotleft.set_sensitive(False)
			self.action_rotright.set_sensitive(False)
			self.action_fliphori.set_sensitive(False)
			self.action_flipvert.set_sensitive(False)

class GLogicApplication(Gtk.Application):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, application_id="org.astralco.glogic", **kwargs)
		self.window = None
	
	def action_handler(self, action):
		def _(*args):
			if not self.window is None:
				# Dangerous Call :) 
				cmd = f'self.window.{action}'
				eval(cmd)(*args)
		return _

	def do_startup(self, *args):
		Gtk.Application.do_startup(self)

		# Open File Pressed
		action = Gio.SimpleAction.new("on_action_open_pressed", None)
		action.connect("activate", self.action_handler('on_action_open_pressed'))
		self.add_action(action)

		# Save 
		action = Gio.SimpleAction.new("on_action_save_pressed", None)
		action.connect("activate", self.action_handler('on_action_save_pressed'))
		self.add_action(action)

		# Save As
		action = Gio.SimpleAction.new("on_action_saveas_pressed", None)
		action.connect("activate", self.action_handler('on_action_saveas_pressed'))
		self.add_action(action)

		# Save Image
		action = Gio.SimpleAction.new("on_action_save_image", None)
		action.connect("activate", self.action_handler('on_action_save_image'))
		self.add_action(action)

		# About
		action = Gio.SimpleAction.new("on_action_about_pressed", None)
		action.connect("activate", self.action_handler('on_action_about_pressed'))
		self.add_action(action)

		# Quit
		action = Gio.SimpleAction.new("on_action_quit_pressed", None)
		action.connect("activate", self.action_handler('on_action_quit_pressed'))
		self.add_action(action)

	def do_activate(self, *args):
		if not self.window:
		    # Windows are associated with the application
		    # when the last one is closed the application shuts down
			self.window = MainFrame(application=self)
			self.add_window(self.window)
		self.window.present()
		self.window.show()