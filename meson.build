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
  app_id = 'org.astralco.ggate.Dev'
  gresource_prefix = '/org/astralco/ggate/Dev'
elif profile == 'release'
  app_id = 'org.astralco.ggate'
  gresource_prefix = '/org/astralco/ggate'
endif

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('bindir', get_option('bindir'))
conf.set('pkgdatadir', pkgdatadir)
conf.set('APP_PREFIX', app_id)

# Configure and install config.py to python installation directory
configure_file(
  input: 'ggate/config.py',
  output: 'config.py',
  configuration: conf,
  install: true,
  install_dir: py_installation.get_install_dir() / 'ggate'
)

# Configure and install desktop file
desktop_conf = configuration_data()
desktop_conf.set('APP_ID', app_id)
configure_file(
  input: 'data/org.astralco.ggate.desktop.in',
  output: app_id + '.desktop',
  configuration: desktop_conf,
  install: true,
  install_dir: get_option('datadir') / 'applications'
)

# Configure and install AppStream metadata
metainfo_conf = configuration_data()
metainfo_conf.set('APP_ID', app_id)
configure_file(
  input: 'data/org.astralco.ggate.metainfo.xml.in',
  output: app_id + '.metainfo.xml',
  configuration: metainfo_conf,
  install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

# Install MIME package description
install_data('data/ggate.xml',
  install_dir: get_option('datadir') / 'mime' / 'packages'
)

# Install scalable application icon (renamed to app_id)
install_data('data/images/scalable/ggate.svg',
  rename: app_id + '.svg',
  install_dir: get_option('datadir') / 'icons' / 'hicolor' / 'scalable' / 'apps'
)

# Install sized application icons (renamed to app_id)
icon_sizes = ['16', '24', '32', '48', '64', '96', '128', '256', '512']
foreach size : icon_sizes
  install_data('data/images/apps' / (size + 'x' + size) / 'ggate.png',
    rename: app_id + '.png',
    install_dir: get_option('datadir') / 'icons' / 'hicolor' / (size + 'x' + size) / 'apps'
  )
endforeach

# Install MIME type icons (using standard name text-glc.png)
foreach size : icon_sizes
  install_data('data/images/mime' / (size + 'x' + size) / 'text-glc.png',
    install_dir: get_option('datadir') / 'icons' / 'hicolor' / (size + 'x' + size) / 'mimetypes'
  )
  if size in ['16', '24', '32', '48', '256']
    install_data('data/images/mime' / (size + 'x' + size) / 'text-glc.png',
      install_dir: get_option('datadir') / 'icons' / 'Yaru' / (size + 'x' + size) / 'mimetypes'
    )
  endif
endforeach

# Install help manual
install_subdir('data/help/C',
  install_dir: get_option('datadir') / 'help' / 'ggate',
  strip_directory: false
)

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

# Install the entire ggate package recursively, excluding .pyc and unconfigured config.py
install_subdir('ggate',
  install_dir: py_installation.get_install_dir(),
  exclude_directories: exclude_pycache_dirs,
  exclude_files: ['*.pyc', 'config.py']
)

# Update desktop/icon caches only when not building inside a sandbox (Flatpak/Snap)
if not get_option('prefix').startswith('/app') and not get_option('prefix').startswith('/snap')
  gnome.post_install(
    glib_compile_schemas: true,
    gtk_update_icon_cache: true,
    update_desktop_database: find_program('update-desktop-database', required: false).found(),
  )
endif