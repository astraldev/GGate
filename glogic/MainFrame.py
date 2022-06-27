# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import os
import sys
import webbrowser
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio
from glogic import UserInterfaces, config, const
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

class ShortCutWindow:
    def __init__(self, parent):
        shortcut_builder = Gtk.Builder.new_from_string(UserInterfaces.shortcut_ui, -1)
        shortcut_window = shortcut_builder.get_object("shortcuts")
        shortcut_window.set_transient_for(parent)
        shortcut_window.show()

class MainFrame(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        Gtk.Window.__init__(self, title="%s - %s" %
                            (const.text_notitle, const.app_name), **kwargs)
        self.application = kwargs['application']
        self.running_mode = False
        self.pause_running_mode = False
        self.clicked_on_pause = False

        self.circuit = CircuitManager()
        self.circuit.connect("title-changed", self.on_circuit_title_changed)
        self.circuit.connect(
            "message-changed", self.on_circuit_message_changed)
        self.circuit.connect(
            "item-unselected", self.on_circuit_item_unselected)
        self.circuit.connect("alert", self.on_circuit_alert)

        Preference.load_settings()

        # Component window
        self.comp_window = ComponentView()
        self.comp_window.connect("component-checked", self.on_comp_checked)

        self.create_window()

        # Property window
        self.prop_window = PropertyWindow()
        self.prop_window.set_transient_for(self)
        self.prop_window.set_hide_on_close(True)
        self.prop_window.set_modal(True)

        self.prop_window.connect("window-hidden", self.on_propwindow_hidden)
        self.prop_window.connect("property-changed", self.on_property_changed)

        # Timing diagram window
        self.diagram_window = TimingDiagramWindow(self)

        # Preferences window
        self.pref_window = PreferencesWindow(self)

        # About dialog
        self.about_dialog = Gtk.AboutDialog()
        picture = Gdk.Texture.new_for_pixbuf(GdkPixbuf.Pixbuf.new_from_file(config.DATADIR+"/images/glogic.png"))
        self.about_dialog.set_logo(picture)
        self.about_dialog.set_program_name(const.app_name)
        self.about_dialog.set_version(config.VERSION )
        self.about_dialog.set_comments(const.description)
        self.about_dialog.set_copyright(const.copyright)
        self.about_dialog.set_website(const.website)
        self.about_dialog.set_license(const.license)
        self.about_dialog.set_authors(const.developer)

        tr_credits = _("translator-credits")
        if tr_credits != "translator-credits":
            self.about_dialog.set_translator_credits(tr_credits)

        self.clipboard = self.get_clipboard()

        if len(sys.argv) >= 2:
            self.circuit.open_file(sys.argv[1])
            self.drawarea.redraw = True
            self.drawarea.queue_draw()

    def set_up_shortcuts(self, *args):

        actions = {
            "application": [
                ('app.on_action_new_pressed',       ["<Ctrl>N"]),
                ('app.on_action_open_pressed',      ["<Ctrl>O"]),
                ('app.on_action_save_pressed',   	["<Ctrl>S"]),
                ('app.on_action_quit_pressed',   	["<Ctrl>Q"]),
                ('app.on_action_saveas_pressed',    ["<Ctrl><Shift>S"]),
                ('app.on_show_shortcut',            ['<Ctrl><Shift>question'])
            ],
            'window':	   [
                (
                    self.toggle_run,
                    'app.toggle_run',
                    ['F5']
                ),
                (
                    self.toggle_net,
                    'app.toggle_net',
                    ['<Ctrl>E']
                ),
                (
                    self.on_action_undo_pressed,     
                    'app.on_action_undo_pressed',   	
                    ["<Ctrl>Z"]
                ),
                (
                    self.on_action_redo_pressed,     
                    'app.on_action_redo_pressed',   	
                    ["<Ctrl><Shift>Z"]
                ),
                (
                    self.on_action_cut_pressed,      
                    'app.on_action_cut_pressed',    	
                    ["<Ctrl>X"]
                ),
                (
                    self.on_action_copy_pressed,     
                    'app.on_action_copy_pressed',   	
                    ["<Ctrl>C"]
                ),
                (
                    self.on_action_paste_pressed,    
                    'app.on_action_paste_pressed',  	
                    ["<Ctrl>V"]
                ),
                (
                    self.on_action_diagram_pressed,  
                    'app.on_action_diagram_pressed',	
                    ["<Ctrl>T"]
                ),
                (
                    self.on_action_property_pressed, 
                    'app.on_action_property_toggled',  
                    ["<Ctrl>P"]
                )
            ]
        }

        for action, accel in actions['application']:
            self.application.set_accels_for_action(action, accel)

        for handler, action_desc, accel in actions['window']:
            action = Gio.SimpleAction.new(action_desc.split('.')[-1])
            action.connect('activate', handler)
            self.application.add_action(action)
            self.application.set_accels_for_action(action_desc, accel)

    def set_up_action_bar(self, *args):
        # Rotate Left Action
        self.action_rotleft = Gtk.Button()
        image = Gtk.Image.new_from_icon_name('object-rotate-left-symbolic')
        self.action_rotleft.set_child(image)
        self.action_rotleft.connect('clicked', self.on_action_rotate_left_90)
        self.action_rotleft.set_tooltip_markup(_("Rotate component ") + '<b>' + _('Left 90°') + '</b>')

        self.action_bar.pack_start(self.action_rotleft)

        # Rotate Right Action
        self.action_rotright = Gtk.Button()
        image = Gtk.Image.new_from_icon_name('object-rotate-right-symbolic')
        self.action_rotright.set_child(image)
        self.action_rotright.connect('clicked', self.on_action_rotate_right_90)
        self.action_rotright.set_tooltip_markup(
            _("Rotate component ") + '<b>' + _('Right 90°') + "</b>")

        self.action_bar.pack_start(self.action_rotright)

        # Flip Horizontal
        self.action_fliphori = Gtk.Button()
        image = Gtk.Image.new_from_icon_name('object-flip-horizontal-symbolic')
        self.action_fliphori.set_child(image)
        self.action_fliphori.connect('clicked', self.on_action_flip_horizontally)
        self.action_fliphori.set_tooltip_markup(_('Flip component ' + '<b>' + _('horizontally') + '</b>'))

        self.action_bar.pack_start(self.action_fliphori)

        # Flip Vertical
        self.action_flipvert = Gtk.Button()
        image = Gtk.Image.new_from_icon_name('object-flip-vertical-symbolic')
        self.action_flipvert.set_child(image)
        self.action_flipvert.connect('clicked', self.on_action_flip_vertically)
        self.action_flipvert.set_tooltip_markup(_('Flip component ') + '<b>' + _('vertically') + '</b>')

        self.action_bar.pack_start(self.action_flipvert)

        # Add Net
        self.action_net = Gtk.ToggleButton()
        image = Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file(config.DATADIR+"images/add-net.png"))
        self.action_net.set_child(image)
        self.action_net.connect('toggled', self.on_action_net_toggled)
        self.action_net.set_tooltip_markup(_('Add net to circuit') + '<b>' + _(' Ctrl+E') + '</b>')
        self.action_bar.pack_start(self.action_net)
        self.action_net.set_active(False)

        self._toggle_run_state = -1
        self._self_toggle = False

    def create_window(self):
        self.set_default_size(640, 400)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Menu Button

        self.menu_button = Gtk.MenuButton.new()
        self.menu_button.set_direction(Gtk.ArrowType.NONE)

        # Menu Popover

        _menu_builder = Gtk.Builder.new_from_string(UserInterfaces.menu_xml, -1)
        _menu = _menu_builder.get_object("app-menu")

        self.popover = Gtk.PopoverMenu.new_from_model(_menu)
        self.menu_button.set_popover(self.popover)

        # play pause button
        self.action_run = Gtk.ToggleButton()
        play_image = Gtk.Image.new_from_icon_name('media-playback-start-symbolic')
        self.action_run.set_tooltip_text(_("Run and simulate this circuit"))
        self.action_run.connect('toggled', self.on_action_run_toggled)
        self.action_run.connect('toggled', self.on_action_run_clicked)

        self.action_run.set_child(play_image)

        # Header Bar
        self.header_bar = Gtk.HeaderBar()
        self.header_bar.pack_start(self.menu_button)
        self.header_bar.pack_end(self.action_run)

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
        self.set_up_shortcuts()

        action_bar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        _box = Gtk.Box()
        _box.set_hexpand(False)
        _box.set_halign(Gtk.Align.START)

        _box.append(self.action_bar)
        action_bar_box.append(_box)
        action_bar_box.append(self.statusbar)

        self.statusbar.set_hexpand(True)
        self.statusbar.set_halign(Gtk.Align.FILL)

        action_bar_box.set_hexpand(True)

        box.append(action_bar_box)

        # Component box
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

        self.disable_edit_actions()

    def on_action_about_pressed(self, *widget):
        self.about_dialog.present()

    def on_action_new_pressed(self, *args):
        self.check_modified(new=True)

        if self.drawarea.drag_enabled:
            return

    def _new_activated(self, *args):
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
        self.disable_edit_actions()
        self.action_net.set_active(False)
        self.diagram_window.destroy()
        self.diagram_window = TimingDiagramWindow(self)

    def on_action_open_pressed(self, *args):
        if self.check_modified(open=True):
            return

    def _open_activated(self, *args):
        dialog = Gtk.FileChooserDialog()
        dialog.set_title(_("Open file"))
        dialog.set_transient_for(self)
        dialog.set_action(Gtk.FileChooserAction.OPEN)

        cancel_button = dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        cancel_button.add_css_class('destructive-action')

        open_button = dialog.add_button("Open", Gtk.ResponseType.ACCEPT)
        open_button.add_css_class('suggested-action')

        dialog.set_transient_for(self)
        self.add_filters(dialog)

        dialog.connect('response', self._open_file)
        dialog.present()

    def _open_file(self, dialog, value, *args):

        if value == Gtk.ResponseType.ACCEPT:
            filepath = dialog.get_file().get_path()

        else:
            dialog.close()
            return

        if not self.circuit.open_file(filepath):
            self.reset_frame()
            self.drawarea.redraw = True
            self.drawarea.queue_draw()
            self.statusbar.push(0, f"Opened {filepath.split('/')[-1]}")
        dialog.close()

    def overwrite_save(self, **kwargs):

        if self.circuit.filepath == "":
            self.rename_save(quit=kwargs.get('quit', False))
        else:
            if not self.circuit.save_file(self.circuit.filepath):
                self.rename_save(ask=False if kwargs.get('save', False) else True)

                if kwargs.get('quit', True) and (not kwargs.get('save', False)):
                    self.application.quit()

    def rename_save(self, ask=True, **kwargs):
        if not ask:
            return
        chooser = Gtk.FileChooserDialog()
        chooser.set_title("<b>Save file</b>"),
        chooser.set_transient_for(self)
        chooser.set_application(self.application)
        chooser.set_action(Gtk.FileChooserAction.SAVE)

        cancel_button = chooser.add_button('Cancel', Gtk.ResponseType.CANCEL)
        cancel_button.add_css_class('destructive-action')

        save_button = chooser.add_button('Save', Gtk.ResponseType.ACCEPT)
        save_button.add_css_class('suggested-action')

        chooser.set_modal(True)

        chooser.connect('response', self.on_save_response, kwargs)
        chooser.present()
        self.add_filters(chooser)

    def on_save_response(self, dialog, response, *args):

        if response == Gtk.ResponseType.ACCEPT:
            filepath = dialog.get_file().get_path()
            filter_name = dialog.get_filter().get_name()

            if filter_name == const.glcfile_text:
                if not "." in os.path.basename(filepath):
                    filepath += ".glc"

                self.circuit.save_file(filepath)
                dialog.close()
                if args[0].get('quit', False) is True:
                    self.application.quit()
                    return
                else:
                    self.statusbar.push(0, "Saved file... ")

            else:
                dialog.close()
                if not self.circuit.save_file(filepath):
                    self.application.quit()
        else:
            dialog.close()
            return True
    
    def toggle_net(self, *args):
        self.action_net.set_active(not self.action_net.get_active())

    def toggle_run(self, *argrs):
        self.action_run.set_active(not self.action_run.get_active())

    def on_action_save_pressed(self, *args):
        self.overwrite_save(save=True)

    def on_action_saveas_pressed(self, *args):
        self.rename_save()

    def on_action_quit_pressed(self, *args):
        self.application.quit()

    def check_modified(self, **kwargs):
        if self.circuit.need_save:
            dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.QUESTION)
            dialog.set_application(self.application)
            dialog.set_modal(True)
            dialog.add_button('Cancel', Gtk.ResponseType.CANCEL)
            dialog.add_button('Yes', Gtk.ResponseType.YES)
            dialog.add_button('No', Gtk.ResponseType.NO)
            dialog.set_markup(_("<b>Save the modified schematics?</b>"))

            message_area = dialog.get_message_area()

            secondary_text = Gtk.Label()
            secondary_text.set_text(
                _("The schematics was modifed. Save the changes before closing?"))

            message_area.append(secondary_text)

            dialog.present()
            dialog.connect('response', self.on_response, kwargs)
            return True

        elif kwargs.get('new', False):
            self._new_activated()

        elif kwargs.get('open', False):
            self._open_activated()

        return False

    def on_response(self, widget, retval, *args):

        should_close = not (args[0].get("open", False)
                            or args[0].get('new', False))

        if retval == Gtk.ResponseType.YES:

            if args[0].get('new', False):
                self.overwrite_save(new=True)

            elif args[0].get('open', False):
                self.overwrite_save(open=True)

            else:
                self.overwrite_save(quit=should_close)

        elif (retval == Gtk.ResponseType.NO):
            widget.destroy()
            if should_close:
                self.application.quit()
            elif args[0].get('open', False) is True:
                self._open_activated()
            elif args[0].get('new', False) is True:
                self._new_activated()

        else:
            widget.destroy()
            return True

    def on_window_delete(self, *args):
        if not self.check_modified():
            return False
        return True

    def on_action_net_toggled(self, widget, *args):

        if widget.get_active():
            self.drawarea.netstarted = False
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

        if (self._toggle_run_state == 0) or (self._toggle_run_state == 2):
            icon = Gtk.Image.new_from_icon_name('media-playback-pause-symbolic')
            widget.set_tooltip_markup(_("Pause circuit simulation"))
            widget.set_child(icon)

            if self.drawarea.drag_enabled:
                return

            if self.running_mode:
                self.running_mode = False
                self.clicked_on_pause = False
                if self.circuit.action_count < len(self.circuit.components_history) - 1:
                    self.action_redo.set_sensitive(True)
                self.comp_window.set_all_sensitive(True)
                self.action_net.set_sensitive(True)

                self.diagram_window.close()
                self.diagram_window = TimingDiagramWindow(self)

                self.statusbar.push(0, "")
            else:
                self.running_mode = True
                self.circuit.selected_components = []

                self.disable_edit_actions()

                self.comp_window.set_all_sensitive(False)

                self.action_net.set_sensitive(False)
                self.action_net.set_active(False)
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
            play_image = Gtk.Image.new_from_icon_name(
                'media-playback-start-symbolic')
            widget.set_tooltip_markup(_("Run and simulate this circuit"))
            widget.set_child(play_image)

            self.pause_running_mode = False
            if not self.circuit.analyze_logic():
                self.diagram_window.diagramarea.createDiagram()
            self.drawarea.queue_draw()
            self.clicked_on_pause = False

        if self._toggle_run_state == 1:
            play_image = Gtk.Image.new_from_icon_name('media-playback-stop-symbolic')
            widget.set_tooltip_markup(_("Stop circuit simulation"))
            widget.set_child(play_image)
            self.pause_running_mode = True

    def on_action_cut_pressed(self, *widget):
        self.on_action_copy_pressed()
        self.on_action_delete_pressed()

    def on_action_copy_pressed(self, *widget):
        self.clipboard.set(components_to_string(self.circuit.selected_components))

    def on_action_paste_pressed(self, *widget):
        def _handler(clipboard, task):
            str_data = clipboard.read_text_finish(task)
            if str_data != None:
                tmp = string_to_components(str_data)
                if isinstance(tmp, str):
                    dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.ERROR, button_type=Gtk.ButtonsType.OK)
                    dialog.set_markup(_("Error"))
                    dialog.get_message_area().append(Gtk.Label(label=tmp))
                    dialog.present()
                    return
                else:
                    pasted_components = tmp

                if not pasted_components:
                    return

                self.drawarea.set_component(const.component_none)
                self.drawarea.set_pasted_components(pasted_components)
        self.clipboard.read_text_async(None, _handler)

    def on_action_undo_pressed(self, *widget):

        if self.circuit.action_count == 0:
            return

        self.circuit.undo()
        self.disable_edit_actions()
        self.drawarea.redraw = True
        self.drawarea.queue_draw()

    def on_action_redo_pressed(self, *widget):

        if self.circuit.action_count == len(self.circuit.components_history) - 1:
            return

        self.circuit.redo()
        self.disable_edit_actions()
        self.drawarea.redraw = True
        self.drawarea.queue_draw()

    def on_action_delete_pressed(self, *args):
        self.circuit.remove_selected_component()
        self.drawarea.nearest_component = None
        self.drawarea.preselected_component = None
        self.circuit.push_history()
        self.disable_edit_actions()
        self.drawarea.redraw = True
        self.drawarea.queue_draw()

    def on_action_rotate_left_90(self, *widget):
        if comp_dict[self.drawarea.get_component()] is None:
            self.circuit.rotate_left_selected_components()
            self.circuit.push_history()
            self.drawarea.redraw = True
        else:
            self.drawarea.rotate_left_picked_components()
        self.drawarea.queue_draw()

    def on_action_rotate_right_90(self, *widget):
        if comp_dict[self.drawarea.get_component()] is None:
            self.circuit.rotate_right_selected_components()
            self.circuit.push_history()
            self.drawarea.redraw = True
        else:
            self.drawarea.rotate_right_picked_components()
        self.drawarea.queue_draw()

    def on_action_flip_horizontally(self, *widget):
        if comp_dict[self.drawarea.get_component()] is None:
            self.circuit.flip_hori_selected_components()
            self.circuit.push_history()
            self.drawarea.redraw = True
        else:
            self.drawarea.flip_hori_picked_components()
        self.drawarea.queue_draw()

    def on_action_flip_vertically(self, *widget):
        if comp_dict[self.drawarea.get_component()] is None:
            self.circuit.flip_vert_selected_components()
            self.circuit.push_history()
            self.drawarea.redraw = True
        else:
            self.drawarea.flip_vert_picked_components()
        self.drawarea.queue_draw()

    def on_action_property_pressed(self, *widget):
        self.drawarea.set_selected_component_to_prop_window()
        self.prop_window.present()

    def on_action_show_help(self, *args):
        Gtk.show_uri(None, const.help, Gdk.CURRENT_TIME)

    def on_action_translate_pressed(self, *args):
        webbrowser.open(const.devel_translate)

    def on_action_bug_pressed(self, *args):
        webbrowser.open(const.devel_bug)

    def on_action_diagram_pressed(self, *widget):
        self.diagram_window.present()
            

    def on_action_save_image(self, *args):
        save_schematics_as_image(self.circuit, self.running_mode, self)

    def _prefs_changed(self, dialog, response, *args):
        if response == Gtk.ResponseType.APPLY:
            self.pref_window.apply_settings()
            

            Preference.save_settings()
            self.drawarea.redraw = True
            self.drawarea.queue_draw()
        self.pref_window = PreferencesWindow(self)
        dialog.close()

    def on_action_prefs_pressed(self, *widget):
        self.pref_window.connect('response', self._prefs_changed)
        self.pref_window.update_dialog()
        self.pref_window.present()

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
        self.action_net.set_sensitive(True)
        self.drawarea.queue_draw()

    def on_compwindow_hidden(self, widget):
        self.action_components.set_active(False)

    def on_propwindow_hidden(self, widget):
        
        widget.destroy()
        self.prop_window = PropertyWindow()
        self.prop_window.set_transient_for(self)
        self.prop_window.set_hide_on_close(True)
        self.prop_window.set_modal(True)

        self.drawarea.queue_draw()

        return

    def on_property_changed(self, widget):
        self.drawarea.redraw = True
        self.circuit.push_history()
        self.drawarea.queue_draw()

    def on_circuit_title_changed(self, circuit, title):
        self.set_title(title)

    def on_circuit_message_changed(self, circuit, message):
        self.statusbar.push(0, message)

    def on_circuit_item_unselected(self, circuit):
        self.prop_window.setComponent(None)

    def on_circuit_alert(self, circuit, message):
        dialog = Gtk.MessageDialog(transient_for=self, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK)
        dialog.set_markup(_("Error"))
        dialog.get_message_area().append(Gtk.Label(label=_(message)))
        dialog.present()

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
                try:
                    cmd = f'self.window.{action}'
                except:
                    return _
                eval(cmd)(*args)
        return _
    
    def on_show_shortcut(self, *args):
        ShortCutWindow(self.window)

    def do_startup(self, *args):
        Gtk.Application.do_startup(self)

        # New File Pressed
        action = Gio.SimpleAction.new("on_action_new_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_new_pressed'))
        self.add_action(action)

        # Open File Pressed
        action = Gio.SimpleAction.new("on_action_open_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_open_pressed'))
        self.add_action(action)

        # Save
        action = Gio.SimpleAction.new("on_action_save_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_save_pressed'))
        self.add_action(action)

        # Save As
        action = Gio.SimpleAction.new("on_action_saveas_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_saveas_pressed'))
        self.add_action(action)

        # Save Image
        action = Gio.SimpleAction.new("on_action_save_image", None)
        action.connect("activate", self.action_handler('on_action_save_image'))
        self.add_action(action)

        # Help Section

        action = Gio.SimpleAction.new("on_action_show_help", None)
        action.connect("activate", self.action_handler('on_action_show_help'))
        self.add_action(action)

        action = Gio.SimpleAction.new("on_action_translate_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_translate_pressed'))
        self.add_action(action)

        action = Gio.SimpleAction.new("on_action_bug_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_bug_pressed'))
        self.add_action(action)

        # About
        action = Gio.SimpleAction.new("on_action_about_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_about_pressed'))
        self.add_action(action)

        # Preference

        action = Gio.SimpleAction.new("on_action_prefs_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_prefs_pressed'))
        self.add_action(action)

        # Shortcut

        action = Gio.SimpleAction.new("on_show_shortcut", None)
        action.connect("activate", self.on_show_shortcut)
        self.add_action(action)

        # Quit
        action = Gio.SimpleAction.new("on_action_quit_pressed", None)
        action.connect("activate", self.action_handler(
            'on_action_quit_pressed'))
        self.add_action(action)

    def do_activate(self, *args):
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainFrame(application=self)
            self.add_window(self.window)
        self.window.present()
        self.window.show()
