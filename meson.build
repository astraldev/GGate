project(
  'ggate',
  version: '5.0.0',
  meson_version: '>= 1.4.0',
  default_options: [
    'warning_level=2',
    'werror=false',
  ],
)

dependency('pygobject-3.0')
dependency('gtk4', version: '>= 4.16.0')
dependency('libadwaita-1', version: '>= 1.6.8')

gnome = import('gnome')
python = import('python')

py_installation = python.find_installation('python3',
  modules: ['gi', 'cairo', 'packaging', 'igraph', 'shapely']
)

py_installation.dependency()

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

profile = get_option('profile')
if profile == 'development'
  app_id = 'org.astralco.GGate.Dev'
  gresource_prefix = '/org/astralco/GGate/Dev'
elif profile == 'release'
  app_id = 'org.astralco.GGate'
  gresource_prefix = '/org/astralco/GGate'
endif

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('bindir', get_option('bindir'))
conf.set('pkgdatadir', pkgdatadir)

subdir('bin')
subdir('data/images')

exclude_pycache_dirs = []
foreach d : run_command(
  find_program('sh'),
  files('build-aux/meson-exclude-pycache.sh'),
  'ggate',
  check: true
).stdout().strip().split('\n')
  if d != ''
    exclude_pycache_dirs += d
  endif
endforeach

# Install the entire ggate package recursively, excluding .pyc files
install_subdir('ggate',
  install_dir: py_installation.get_install_dir(),
  exclude_directories: exclude_pycache_dirs,
  exclude_files: ['*.pyc']
)

# Update desktop/icon caches only when not building inside a sandbox (Flatpak/Snap)
if not get_option('prefix').startswith('/app') and not get_option('prefix').startswith('/snap')
  gnome.post_install(
    glib_compile_schemas: true,
    gtk_update_icon_cache: true,
    update_desktop_database: true,
  )
endif