from gi.repository import Gtk, Adw, Gio

class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new("io.github.angelorosa.flashpaste")

        page = Adw.PreferencesPage()
        page.set_title("General")
        page.set_icon_name("preferences-system-symbolic")
        self.add(page)

        group = Adw.PreferencesGroup()
        group.set_title("Pastebin Integration")
        group.set_description("Configure integration with Pastebin.com")
        page.add(group)

        # API Key
        api_key_row = Adw.PasswordEntryRow()
        api_key_row.set_title("API Developer Key")
        self.settings.bind(
            "api-dev-key",
            api_key_row,
            "text",
            Gio.SettingsBindFlags.DEFAULT
        )
        group.add(api_key_row)

        # Default Privacy
        privacy_row = Adw.ComboRow()
        privacy_row.set_title("Default Privacy")
        model = Gtk.StringList.new(["Public", "Unlisted", "Private"])
        privacy_row.set_model(model)
        
        self.settings.bind(
            "default-privacy",
            privacy_row,
            "selected",
            Gio.SettingsBindFlags.DEFAULT
        )
        group.add(privacy_row)

        # Explicit Save Button (User Reassurance)
        save_row = Adw.ActionRow()
        save_btn = Gtk.Button(label="Save Settings")
        save_btn.set_valign(Gtk.Align.CENTER)
        save_btn.connect("clicked", self._on_save_clicked)
        save_row.add_suffix(save_btn)
        group.add(save_row)

    def _on_save_clicked(self, btn):
        # Settings are auto-saved by Gio.Settings binding, so we just provide feedback
        self.close()
