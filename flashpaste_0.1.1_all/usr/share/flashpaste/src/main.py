import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
from .window import MainWindow
from .preferences import PreferencesWindow

class FlashPasteApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="io.github.angelorosa.flashpaste",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(self)
        win.present()

    def do_startup(self):
        Adw.Application.do_startup(self)
        
        # Actions
        pref_action = Gio.SimpleAction.new("preferences", None)
        pref_action.connect("activate", self._on_preferences)
        self.add_action(pref_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

    def _on_preferences(self, action, param):
        win = PreferencesWindow(transient_for=self.props.active_window)
        win.present()

    def _on_about(self, action, param):
        dialog = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="FlashPaste",
            application_icon="edit-paste-symbolic",
            developer_name="Angelo Rosa",
            version="0.1.1",
            copyright="© 2026 Angelo Rosa",
            license_type=Gtk.License.MIT_X11,
        )
        dialog.present()

def main():
    app = FlashPasteApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
