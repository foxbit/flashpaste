project('flashpaste', 'c',
  version : '0.1.6',
  meson_version : '>= 0.59.0',
  default_options : ['warning_level=2', 'werror=false', 'c_std=c11',],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

# Runtime dependencies handled by package manager, skipping build-time pkg-config check
# dependency('gtk4', version: '>= 4.10.0')
# dependency('libadwaita-1', version: '>= 1.5.0')
# dependency('pygobject-3.0', version: '>= 3.46.0')

subdir('data')
subdir('src')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
