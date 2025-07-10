# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-

import os
import sys
import webbrowser

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gdk, GdkPixbuf, Gio, Adw
from ggate import UserInterfaces, config
from ggate.const import definitions as const
from ggate.Exporter import save_schematics_as_image
from gettext import gettext as _
from ggate.DrawArea import DrawArea
from ggate.ComponentView import ComponentView
from ggate.CircuitManager import CircuitManager
from ggate.PropertyWindow import PropertyWindow
from ggate.PreferencesWindow import PreferencesWindow
from ggate import Preference

from ggate.Components.LogicGates import logic_gates

from ggate.Components.Managers.FileManager import FileIOManager
from ggate.Components.Managers.FileManager import FileManager
from ggate.Components.Managers.Alerts import AlertDialogs

from ggate.StatusDisplay import StatusDisplay
from ggate.TimingDiagramWindow import TimingDiagramWindow

themed_icons = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
themed_icons.add_search_path(config.DATADIR + "/images")

TOOLTIPS = {
    "simulation": {
        "start": _("Run and simulate this circuit"),
        "stop": _("Stop simulation"),
        "pause": _("Continue simulation"),
    }
}

class ShortCutWindow:
    def __init__(self, parent):
        shortcut_builder = Gtk.Builder.new_from_string(UserInterfaces.shortcut_ui, -1)
        shortcut_window = shortcut_builder.get_object("shortcuts")
        shortcut_window.set_transient_for(parent)
        shortcut_window.show()

class MainFrame(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        Adw.ApplicationWindow.__init__(
            self, title="%s - %s" % (const.text_notitle, const.app_name), **kwargs
        )
        self.application: Adw.Application = kwargs["application"]
        self.running_mode = False
        self.pause_running_mode = False

        self.io_manager = FileIOManager
        self.file_manager = FileManager.for_glc(self)
        self.alert_manager = AlertDialogs(self)
        self.circuit = CircuitManager(self)

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
        picture = Gdk.Texture.new_for_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file(config.DATADIR + "/images/ggate.png")
        )
        self.about_dialog.set_logo(picture)
        self.about_dialog.set_program_name(const.app_name)
        self.about_dialog.set_version(config.VERSION)
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
                ("app.on_action_new_pressed", ["<Ctrl>N"]),
                ("app.on_action_open_pressed", ["<Ctrl>O"]),
                ("app.on_action_save_pressed", ["<Ctrl>S"]),
                ("app.on_action_quit_pressed", ["<Ctrl>Q"]),
                ("app.on_action_saveas_pressed", ["<Ctrl><Shift>S"]),
                ("app.on_show_shortcut", ["<Ctrl><Shift>question"]),
            ],
            "window": [
                (self.toggle_run, "app.toggle_run", ["F5"]),
                (self.toggle_net, "app.toggle_net", ["<Ctrl>E"]),
                (
                    self.on_action_undo_pressed,
                    "app.on_action_undo_pressed",
                    ["<Ctrl>Z"],
                ),
                (
                    self.on_action_redo_pressed,
                    "app.on_action_redo_pressed",
                    ["<Ctrl><Shift>Z"],
                ),
                (
                    self.on_action_cut_pressed,
                    "app.on_action_cut_pressed",
                    ["<Ctrl>X"]
                ),
                (
                    self.on_action_copy_pressed,
                    "app.on_action_copy_pressed",
                    ["<Ctrl>C"],
                ),
                (
                    self.on_action_paste_pressed,
                    "app.on_action_paste_pressed",
                    ["<Ctrl>V"],
                ),
                (
                    self.on_action_delete_pressed,
                    "app.on_action_delete_pressed",
                    ["BackSpace"],
                ),
                (
                    self.on_action_diagram_pressed,
                    "app.on_action_diagram_pressed",
                    ["<Ctrl>T"],
                ),
                (
                    self.on_action_property_pressed,
                    "app.on_action_property_toggled",
                    ["<Ctrl>P"],
                ),
            ],
        }

        for action, accel in actions["application"]:
            self.application.set_accels_for_action(action, accel)

        for handler, action_desc, accel in actions["window"]:
            action = Gio.SimpleAction.new(action_desc.split(".")[-1])
            action.connect("activate", handler)
            self.application.add_action(action)
            self.application.set_accels_for_action(action_desc, accel)

    def set_up_action_bar(self, *args):
        # Rotate Left Action
        self.action_rotleft = Gtk.Button()
        image = Gtk.Image.new_from_icon_name("object-rotate-left-symbolic")
        self.action_rotleft.set_child(image)
        self.action_rotleft.connect("clicked", self.on_action_rotate_left_90)
        self.action_rotleft.set_tooltip_markup(
            _("Rotate component ") + "<b>" + _("Left 90°") + "</b>"
        )

        self.action_bar.pack_start(self.action_rotleft)

        # Rotate Right Action
        self.action_rotright = Gtk.Button()
        image = Gtk.Image.new_from_icon_name("object-rotate-right-symbolic")
        self.action_rotright.set_child(image)
        self.action_rotright.connect("clicked", self.on_action_rotate_right_90)
        self.action_rotright.set_tooltip_markup(
            _("Rotate component ") + "<b>" + _("Right 90°") + "</b>"
        )

        self.action_bar.pack_start(self.action_rotright)

        # Flip Horizontal
        self.action_fliphori = Gtk.Button()
        image = Gtk.Image.new_from_icon_name("object-flip-horizontal-symbolic")
        self.action_fliphori.set_child(image)
        self.action_fliphori.connect("clicked", self.on_action_flip_horizontally)
        self.action_fliphori.set_tooltip_markup(
            _("Flip component " + "<b>" + _("horizontally") + "</b>")
        )

        self.action_bar.pack_start(self.action_fliphori)

        # Flip Vertical
        self.action_flipvert = Gtk.Button()
        image = Gtk.Image.new_from_icon_name("object-flip-vertical-symbolic")
        self.action_flipvert.set_child(image)
        self.action_flipvert.connect("clicked", self.on_action_flip_vertically)
        self.action_flipvert.set_tooltip_markup(
            _("Flip component ") + "<b>" + _("vertically") + "</b>"
        )

        self.action_bar.pack_start(self.action_flipvert)

        # Add Net
        self.action_net = Gtk.ToggleButton()
        image = Gtk.Image.new_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file(config.DATADIR + "images/add-net.png")
        )
        self.action_net.set_child(image)
        self.action_net.connect("toggled", self.on_action_net_toggled)
        self.action_net.set_tooltip_markup(
            _("Add net to circuit") + "<b>" + _(" Ctrl+E") + "</b>"
        )
        self.action_bar.pack_start(self.action_net)
        self.action_net.set_active(False)

    def create_window(self):
        self.set_default_size(640, 400)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Menu Button

        self.menu_button = Gtk.MenuButton.new()
        self.menu_button.set_direction(Gtk.ArrowType.DOWN)
        self.menu_button.set_icon_name("open-menu-symbolic")

        # Menu Popover

        _menu_builder = Gtk.Builder.new_from_string(UserInterfaces.menu_xml, -1)
        _menu = _menu_builder.get_object("app-menu")

        self.popover = Gtk.PopoverMenu.new_from_model(_menu)
        self.menu_button.set_popover(self.popover)

        # play, pause, stop button
        self.action_run = Gtk.ToggleButton()
        self.action_pause = Gtk.Button()

        play_image = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
        self.action_run.set_tooltip_text(TOOLTIPS["simulation"]["start"])
        self.action_run.connect("toggled", self.on_action_run_clicked)

        pause_image = Gtk.Image.new_from_icon_name("media-playback-pause-symbolic")
        self.action_pause.set_tooltip_text(TOOLTIPS["simulation"]["pause"])
        self.action_pause.set_visible(False)
        self.action_pause.connect("clicked", self.on_action_pause_clicked)

        self.action_run.set_child(play_image)
        self.action_pause.set_child(pause_image)

        _run_pause_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        _run_pause_box.add_css_class("linked")
        _run_pause_box.append(self.action_run)
        _run_pause_box.append(self.action_pause)

        # Header Bar
        self.header_bar = Gtk.HeaderBar()

        if sys.platform.startswith("win32") or sys.platform.startswith("darwin"):
            self.header_bar.set_use_native_controls(True)

        if self.header_bar.get_use_native_controls():
            self.header_bar.pack_end(self.menu_button)
            self.header_bar.pack_end(_run_pause_box)
        else:
            self.header_bar.pack_start(self.menu_button)
            self.header_bar.pack_end(_run_pause_box)

        self.set_titlebar(self.header_bar)

        # Draw area
        self.drawarea = DrawArea(self)
        self.drawarea.circuit = self.circuit
        box.append(self.drawarea)
        self.drawarea.set_vexpand(True)
        self.drawarea.set_hexpand(True)

        # Status bar
        self.statusbar = StatusDisplay()
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

    def create_new_buffer(self, *args):
        self.set_title("%s - %s" % (const.text_notitle, const.app_name))
        self.reset_frame()
        self.circuit.reset_circuit()
        self.drawarea.nearest_component = None
        self.drawarea.redraw = True
        self.drawarea.queue_draw()

    def reset_frame(self):
        # reset prop window
        self.statusbar.update("")
        self.drawarea.set_component(const.component_none)
        self.disable_edit_actions()
        self.action_net.set_active(False)
        self.diagram_window.destroy()
        self.diagram_window = TimingDiagramWindow(self)

    # >> app action handlers >>

    def on_action_about_pressed(self, *widget):
        self.about_dialog.present()

    def on_action_new_pressed(self, *args):
        if self.circuit.need_save:
            return self.alert_manager.alert_new_unsaved_buffer()
        self.create_new_buffer()

    def on_action_open_pressed(self, *args):
        if not self.circuit.need_save:
            return self.file_manager.open_activated()

        self.alert_manager.alert_open_unsaved_buffer()

    def on_action_save_pressed(self, *args):
        fpath = self.circuit.filepath
        if not os.path.exists(fpath) or not self.save_file_complete():
            return self.on_action_saveas_pressed()

    def on_action_saveas_pressed(self, *args):
        self.file_manager.save_as_activated()

    def on_action_quit_pressed(self, *args):
        self.application.quit()

    # << app action handlers <<

    # >> file completion handlers >>

    def open_file_complete(self, path):
        """Loads a file path, resets the draw area, renders the file content and updates the status bar"""

        if self.circuit.open_file(path):
            return

        self.reset_frame()
        self.drawarea.redraw = True
        self.drawarea.queue_draw()

        # todo: translations
        self.statusbar.update(f"Opened <a href=\"file:///{path}\">{path.split('/')[-1]}</a>")

    def save_file__complete(self, path = None):
        "Saves current circuit to the specified path or opened file"
        path = path or self.circuit.filepath
        return self.circuit.save_file(path)

    def save_file_as__complete(self, path):
        "Saves current circuit to the specified path and reloads window"
        if not self.save_file__complete(path):
            return
        self.open_file_complete(path)

    # << file completion handlers <<

    def toggle_net(self, *args):
        self.action_net.set_active(not self.action_net.get_active())

    def toggle_run(self, *args):
        self.action_run.set_active(not self.action_run.get_active())

    def on_window_delete(self, *args):
        if self.circuit.need_save:
            self.alert_manager.alert_close_unsaved_buffer()
            return True
        return False

    def on_action_net_toggled(self, widget, *args):

        if widget.get_active():
            self.drawarea.netstarted = False
            widget.set_active(True)
            self.drawarea.set_component(const.component_net)

        elif self.drawarea.get_component() == const.component_net:
            self.drawarea.set_component(const.component_none)

        self.drawarea.queue_draw()

    def on_circuit_run(self, *args):
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
        self.circuit.analyze_net_connections()
        self.circuit.initialize_logic()
        if not self.circuit.analyze_logic():
            self.diagram_window.diagram_area.createDiagram()

        self.drawarea.redraw = True
        self.drawarea.queue_draw()

    def on_circuit_stop(self, *args):
        if self.running_mode:
            self.running_mode = False
            if self.circuit.action_count < len(self.circuit.components_history) - 1:
                self.action_redo.set_sensitive(True)
            self.comp_window.set_all_sensitive(True)
            self.action_net.set_sensitive(True)
            self.diagram_window.close()
            self.diagram_window = TimingDiagramWindow(self)
            self.statusbar.update("")
        self.drawarea.redraw = True
        self.drawarea.queue_draw()

    def on_action_pause_clicked(self, widget, *args):
        if self.drawarea.drag_enabled:
            return
        if self.pause_running_mode:  # if already paused, play simulation
            play_image = Gtk.Image.new_from_icon_name("media-playback-pause-symbolic")
            widget.set_tooltip_markup(TOOLTIPS["simulation"]["pause"])
            widget.set_child(play_image)

            self.pause_running_mode = False
            if not self.circuit.analyze_logic():
                self.diagram_window.diagram_area.createDiagram()
            self.drawarea.queue_draw()
        else:  # if not paused, pause it
            pause_image = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
            widget.set_tooltip_markup(TOOLTIPS["simulation"]["start"])
            widget.set_child(pause_image)
            self.pause_running_mode = True

    def on_action_run_clicked(self, widget, *args):
        if self.drawarea.drag_enabled:
            return
        if not self.running_mode:  # start running
            stop_image = Gtk.Image.new_from_icon_name("media-playback-stop-symbolic")
            widget.set_tooltip_markup(TOOLTIPS["simulation"]["stop"])
            widget.set_child(stop_image)
            self.on_circuit_run()
            self.action_pause.set_visible(True)
        else:
            start_image = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
            widget.set_tooltip_markup(TOOLTIPS["simulation"]["start"])
            widget.set_child(start_image)
            self.on_circuit_stop()
            self.action_pause.set_visible(False)

    def on_action_cut_pressed(self, *widget):
        self.on_action_copy_pressed()
        self.on_action_delete_pressed()

    def on_action_copy_pressed(self, *widget):
        self.clipboard.set(
            self.circuit.converter
                .components_to_string(self.circuit.selected_components)
        )

    def on_action_paste_pressed(self, *widget):
        def _handler(clipboard, task):
            str_data = clipboard.read_text_finish(task)
            if str_data is not None:
                tmp = string_to_components(str_data)
                if isinstance(tmp, str):
                    dialog = Gtk.MessageDialog(
                        transient_for=self,
                        message_type=Gtk.MessageType.ERROR,
                        button_type=Gtk.ButtonsType.OK,
                    )
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
        if logic_gates[self.drawarea.get_component()] is None:
            self.circuit.rotate_left_selected_components()
            self.circuit.push_history()
            self.drawarea.redraw = True
        else:
            self.drawarea.rotate_left_picked_components()
        self.drawarea.queue_draw()

    def on_action_rotate_right_90(self, *widget):
        if logic_gates[self.drawarea.get_component()] is None:
            self.circuit.rotate_right_selected_components()
            self.circuit.push_history()
            self.drawarea.redraw = True
        else:
            self.drawarea.rotate_right_picked_components()
        self.drawarea.queue_draw()

    def on_action_flip_horizontally(self, *widget):
        if logic_gates[self.drawarea.get_component()] is None:
            self.circuit.flip_hori_selected_components()
            self.circuit.push_history()
            self.drawarea.redraw = True
        else:
            self.drawarea.flip_hori_picked_components()
        self.drawarea.queue_draw()

    def on_action_flip_vertically(self, *widget):
        if logic_gates[self.drawarea.get_component()] is None:
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

    # def on_action_translate_pressed(self, *args):
    #     webbrowser.open(const.devel_translate)

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
        self.pref_window.connect("response", self._prefs_changed)
        self.pref_window.update_dialog()
        self.pref_window.present()

    def on_comp_checked(self, widget, comp_name):
        if logic_gates[comp_name]:
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
        self.prop_window.connect("window-hidden", self.on_propwindow_hidden)
        self.prop_window.connect("property-changed", self.on_property_changed)
        self.drawarea.queue_draw()

    def on_property_changed(self, widget):
        self.circuit.push_history()
        self.drawarea.redraw = True
        self.drawarea.queue_draw()

    def on_circuit_title_changed(self, circuit, title):
        self.set_title(title)

    def on_circuit_message_changed(self, circuit, message):
        self.statusbar.update(message)

    def on_circuit_item_unselected(self, circuit):
        self.prop_window.set_component(None)

    def on_circuit_alert(self, circuit, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
        )
        dialog.set_markup(_("Error"))
        dialog.get_message_area().append(Gtk.Label(label=_(message)))
        dialog.present()

    def disable_edit_actions(self):
        if logic_gates[self.drawarea.get_component()] is None:
            self.action_rotleft.set_sensitive(False)
            self.action_rotright.set_sensitive(False)
            self.action_fliphori.set_sensitive(False)
            self.action_flipvert.set_sensitive(False)


class GLogicApplication(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.astralco.ggate", **kwargs)
        self.window = None

    def action_handler(self, action):
        def _(*args):
            if self.window is not None:
                # Dangerous Call :)
                try:
                    cmd = f"self.window.{action}"
                    eval(cmd)(*args)
                except Exception:
                    return _
        return _

    def on_show_shortcut(self, *args):
        ShortCutWindow(self.window)

    def do_startup(self, *args):
        Gtk.Application.do_startup(self)

        # New File Pressed
        action = Gio.SimpleAction.new("on_action_new_pressed", None)
        action.connect("activate", self.action_handler("on_action_new_pressed"))
        self.add_action(action)

        # Open File Pressed
        action = Gio.SimpleAction.new("on_action_open_pressed", None)
        action.connect("activate", self.action_handler("on_action_open_pressed"))
        self.add_action(action)

        # Save
        action = Gio.SimpleAction.new("on_action_save_pressed", None)
        action.connect("activate", self.action_handler("on_action_save_pressed"))
        self.add_action(action)

        # Save As
        action = Gio.SimpleAction.new("on_action_saveas_pressed", None)
        action.connect("activate", self.action_handler("on_action_saveas_pressed"))
        self.add_action(action)

        # Save Image
        action = Gio.SimpleAction.new("on_action_save_image", None)
        action.connect("activate", self.action_handler("on_action_save_image"))
        self.add_action(action)

        # Help Section

        action = Gio.SimpleAction.new("on_action_show_help", None)
        action.connect("activate", self.action_handler("on_action_show_help"))
        self.add_action(action)

        # Report bug
        action = Gio.SimpleAction.new("on_action_bug_pressed", None)
        action.connect("activate", self.action_handler("on_action_bug_pressed"))
        self.add_action(action)

        # About
        action = Gio.SimpleAction.new("on_action_about_pressed", None)
        action.connect("activate", self.action_handler("on_action_about_pressed"))
        self.add_action(action)

        # Preference

        action = Gio.SimpleAction.new("on_action_prefs_pressed", None)
        action.connect("activate", self.action_handler("on_action_prefs_pressed"))
        self.add_action(action)

        # Shortcuts
        action = Gio.SimpleAction.new("on_show_shortcut", None)
        action.connect("activate", self.on_show_shortcut)
        self.add_action(action)

        # Quit
        action = Gio.SimpleAction.new("on_action_quit_pressed", None)
        action.connect("activate", self.action_handler("on_action_quit_pressed"))
        self.add_action(action)

    def do_activate(self, *args):
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainFrame(application=self)
            self.add_window(self.window)
        self.window.present()
        self.window.show()
