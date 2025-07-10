import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

# Create the main application window
class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Alert Dialog Example")
        self.set_default_size(400, 300)

        # Create a button that will trigger the alert dialog
        button = Gtk.Button(label="Show Alert")
        button.connect("clicked", self.on_button_clicked)
        self.set_child(button)

    def on_button_clicked(self, widget):
        # Create an AlertDialog instance
        alert = Gtk.NativeDialog.newv()
        alert.set_transient_for(self)
        
        # Show the alert dialog
        alert.show(parent=self)

# Create the application
class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.AlertDialogExample")

    def do_activate(self):
        win = MyWindow(self)
        win.present()

# Run the application
app = MyApplication()
app.run()
