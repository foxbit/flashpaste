from gi.repository import Gtk, Adw, Gio, GLib, Gdk
from .preferences import PreferencesWindow
from .database import DatabaseManager
from .pastebin_client import PastebinClient
import threading

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="FlashPaste")
        self.db = DatabaseManager()
        self.settings = Gio.Settings.new("io.github.angelorosa.flashpaste")

        # Bind window size
        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)

        # Main content structure
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        self.toolbar_view = Adw.ToolbarView()
        self.toast_overlay.set_child(self.toolbar_view)

        # Header Bar
        header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(header_bar)

        # Menu Button
        menu_model = Gio.Menu()
        menu_model.append("Preferences", "app.preferences")
        menu_model.append("About", "app.about")
        
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(menu_model)
        header_bar.pack_end(menu_button)

        # Add Button
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.connect("clicked", self._on_add_clicked)
        add_btn.set_tooltip_text("Add new snippet")
        header_bar.pack_start(add_btn)

        # View Switcher Title
        self.view_stack = Adw.ViewStack()
        
        switcher_title = Adw.ViewSwitcherTitle()
        switcher_title.set_stack(self.view_stack)
        header_bar.set_title_widget(switcher_title)

        # Bottom Bar (for mobile)
        switcher_bar = Adw.ViewSwitcherBar()
        switcher_bar.set_stack(self.view_stack)
        self.toolbar_view.add_bottom_bar(switcher_bar)
        
        # Link title to bar visibility
        switcher_title.bind_property(
            "title-visible", 
            switcher_bar, 
            "reveal", 
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.INVERT_BOOLEAN
        )

        # Tab 1: Inbox
        self.inbox_list = Gtk.ListBox()
        self.inbox_list.add_css_class("boxed-list")
        self.inbox_list.set_selection_mode(Gtk.SelectionMode.NONE)
        
        # Use ScrolledWindow directly without StatusPage
        inbox_scrolled = self._create_scrolled(self.inbox_list)
        
        self.view_stack.add_titled_with_icon(
            inbox_scrolled,
            "inbox",
            "Inbox",
            "edit-paste-symbolic"
        )

        # Tab 2: Published
        self.published_list = Gtk.ListBox()
        self.published_list.add_css_class("boxed-list")
        self.published_list.set_selection_mode(Gtk.SelectionMode.NONE)

        published_scrolled = self._create_scrolled(self.published_list)

        self.view_stack.add_titled_with_icon(
            published_scrolled,
            "published",
            "Published",
            "cloud-upload-symbolic"
        )

        # Start cleanup timer
        GLib.timeout_add_seconds(60, self._cleanup_expired_wrapper)
        
        self._refresh_data()

    def _create_scrolled(self, widget):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        # Add some padding around the list
        clamp = Adw.Clamp()
        clamp.set_maximum_size(800)
        clamp.set_margin_top(12)
        clamp.set_margin_bottom(12)
        clamp.set_margin_start(12)
        clamp.set_margin_end(12)
        clamp.set_child(widget)
        scrolled.set_child(clamp)
        return scrolled

    def _on_add_clicked(self, btn):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="New Snippet",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("add", "Add")
        dialog.set_default_response("add")
        dialog.set_close_response("cancel")

        # Text Area
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(200)
        scrolled.set_propagate_natural_height(True)
        
        text_view = Gtk.TextView()
        text_view.set_monospace(True) # Better for code snippets
        scrolled.set_child(text_view)
        box.append(scrolled)
        
        dialog.set_extra_child(box)

        def response_cb(dialog, response):
            if response == "add":
                buffer = text_view.get_buffer()
                content = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
                if content.strip():
                    print(f"Adding snippet: {content[:20]}...")
                    self.db.add_snippet(content)
                    self._refresh_data()
                else:
                    print("Empty content, not adding.")
            dialog.close()

        dialog.connect("response", response_cb)
        dialog.present()

    def _refresh_data(self):
        print("Refreshing data...")
        # Clear lists
        self.inbox_list.remove_all()
        self.published_list.remove_all()

        # Load Inbox
        inbox = self.db.get_snippets(is_published=False)
        print(f"Found {len(inbox)} inbox items")
        for s in inbox:
            self.inbox_list.append(self._create_row(s, is_inbox=True))

        # Load Published
        published = self.db.get_snippets(is_published=True)
        print(f"Found {len(published)} published items")
        for s in published:
            self.published_list.append(self._create_row(s, is_inbox=False))

    def _create_row(self, snippet, is_inbox):
        row = Adw.ActionRow()
        content = snippet['content']
        # Preview first 2 lines
        preview = "\n".join(content.splitlines()[:2])
        row.set_title(preview if len(preview) < 50 else preview[:50] + "...")
        row.set_subtitle(snippet['created_at'])

        # Buttons
        if is_inbox:
            pub_btn = Gtk.Button(icon_name="cloud-upload-symbolic")
            pub_btn.add_css_class("flat")
            pub_btn.set_tooltip_text("Publish to Pastebin")
            pub_btn.connect("clicked", lambda b: self._on_publish(snippet))
            row.add_suffix(pub_btn)

        copy_btn = Gtk.Button(icon_name="edit-copy-symbolic")
        copy_btn.add_css_class("flat")
        copy_btn.set_tooltip_text("Copy to Clipboard")
        copy_btn.connect("clicked", lambda b: self._copy_to_clipboard(snippet))
        row.add_suffix(copy_btn)

        del_btn = Gtk.Button(icon_name="user-trash-symbolic")
        del_btn.add_css_class("flat")
        del_btn.set_tooltip_text("Delete")
        del_btn.connect("clicked", lambda b: self._delete_snippet(snippet['id']))
        row.add_suffix(del_btn)

        if not is_inbox:
             # Add link button/subtitle for URL
             row.set_subtitle(f"{snippet['created_at']} • {snippet['pastebin_url']}")

        return row

    def _copy_to_clipboard(self, snippet):
        clipboard = self.get_display().get_clipboard()
        if snippet['is_published']:
            clipboard.set(snippet['pastebin_url'])
            text = "URL copied to clipboard"
        else:
            clipboard.set(snippet['content'])
            text = "Content copied to clipboard"
        
        self.toast_overlay.add_toast(Adw.Toast.new(text))

    def _delete_snippet(self, sid):
        self.db.delete_snippet(sid)
        self._refresh_data()

    def _on_publish(self, snippet):
        api_key = self.settings.get_string("api-dev-key")
        if not api_key:
            self.toast_overlay.add_toast(Adw.Toast.new("Please configure API Key in Preferences"))
            return

        privacy = self.settings.get_int("default-privacy")
        
        def publish_thread():
            try:
                url = PastebinClient.publish(api_key, snippet['content'], privacy)
                GLib.idle_add(self._on_publish_success, snippet['id'], url)
            except Exception as e:
                GLib.idle_add(self._on_publish_error, str(e))

        threading.Thread(target=publish_thread, daemon=True).start()

    def _on_publish_success(self, sid, url):
        self.db.mark_published(sid, url)
        self._refresh_data()
        self.toast_overlay.add_toast(Adw.Toast.new(f"Published: {url}"))

    def _on_publish_error(self, error_msg):
        self.toast_overlay.add_toast(Adw.Toast.new(f"Error: {error_msg}"))

    def _cleanup_expired_wrapper(self):
        count = self.db.cleanup_expired()
        if count > 0:
            self._refresh_data()
            self.toast_overlay.add_toast(Adw.Toast.new(f"Cleaned up {count} expired snippets"))
        return True # Continue timer

from gi.repository import GObject
