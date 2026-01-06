# FlashPaste

FlashPaste is a lightweight, native Linux application designed for managing temporary text snippets. It acts as a "mental cache," allowing you to quickly store text that you need to use shortly.

**Golden Rule:** Snippets in the Inbox expire and are automatically deleted after 24 hours. To save a snippet permanently, you can publish it to Pastebin directly from the app.

![FlashPaste Screenshot](https://raw.githubusercontent.com/angelorosa/flashpaste/main/screenshot.png)

## Features

- **Temporary Inbox**: Store text snippets that auto-expire after 24 hours.
- **Pastebin Integration**: Publish snippets to Pastebin.com with a single click.
- **History**: View your published snippets and easily open their links.
- **Native UI**: Built with GTK4 and LibAdwaita for a modern GNOME look.
- **Privacy**: Supports Public and Unlisted pastes (Guest mode supports Unlisted only).

## Installation

### .deb Package (Ubuntu/Debian)

1. Download the latest release from the Releases page.
2. Install via terminal:
   ```bash
   sudo apt install ./flashpaste_X.X.X_all.deb
   ```

### Dependencies
- Python 3.11+
- GTK4
- LibAdwaita
- python3-requests

## Usage

1. **Add Snippet**: Click the `+` button or paste text into the app.
2. **Copy**: Click the copy icon to copy content to clipboard.
3. **Publish**: Click the cloud upload icon to send to Pastebin.
4. **Configure**: Go to Preferences to set your Pastebin API Dev Key (required for publishing).
   - Get your key here: [https://pastebin.com/doc_api](https://pastebin.com/doc_api)

## Development

### Requirements
- meson
- ninja-build
- flatpak-builder (optional)

### Building locally
```bash
meson setup builddir
meson compile -C builddir
meson install -C builddir
```

### Building .deb
```bash
./build_deb.sh
```

## License

MIT License
