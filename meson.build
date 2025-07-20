project(
  'ggate',
  version: '5.0.0',
  meson_version: '>= 0.62.0',
  default_options: [
    'warning_level=2',
    'werror=false',
  ],
)

dependency('gtk4', version: '>= 4.18.0')
dependency('libadwaita-1', version: '>= 1.8.alpha')

gnome = import('gnome')
python = import('python')

py_installation = python.find_installation('python3',
  required: true,
  modules: [
    ['pycairo', '>= 1.27.0, < 2.0.0'],
    ['gi', '>= 3.52.3, < 4.0.0'],
    ['packaging', '>= 24.2, < 25.0'],
    ['igraph', '>= 0.11.9, < 0.12.0'],
    ['shapely', '== 2.1.1'],
  ]
)

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

profile = get_option('profile')
if profile == 'development'
  app_id = 'org.astralco.GGate.Dev'
  prefix = '/org/astralco/GGate/Dev'
elif profile == 'release'
  app_id = 'org.astralco.GGate'
  prefix = '/org/astralco/GGate'
endif

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('bindir', get_option('bindir'))

subdir('bin')
subdir('data/images')

# Install the entire ggate package recursively, excluding .pyc files
install_subdir('ggate',
  install_dir: py_installation.get_install_dir(),
  exclude_files: ['**/*.pyc', '**/__pycache__']
)

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)