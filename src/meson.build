pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'src'

python_sources = [
  'main.py',
  'window.py',
  'preferences.py',
  'database.py',
  'pastebin_client.py',
  '__init__.py',
]

install_data(python_sources, install_dir: moduledir)

conf = configuration_data()
conf.set('PYTHON', find_program('python3').full_path())
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'flashpaste.in',
  output: 'flashpaste',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)
