icon_files = [
  # Components
  'components/7seg.svg',
  'components/adder.svg',
  'components/counter.svg',
  'components/dff.svg',
  'components/jkff.svg',
  'components/pipo.svg',
  'components/piso.svg',
  'components/rsff.svg',
  'components/sipo.svg',
  'components/siso.svg',
  'components/tff.svg',

  # Actions
  'actions/flip-horizontal.svg',
  'actions/flip-vertical.svg',
  'actions/rotate-left.svg',
  'actions/rotate-right.svg',
]

resources_xml = configure_file(
  output: 'resources.xml',
  command: [
    py_installation,
    meson.project_source_root() / 'build-aux/generate-resources-xml.py',
    '--prefix', gresource_prefix,
    '--output', '@OUTPUT@',
    '--source-dir', meson.current_source_dir()
  ]
)

ggate_resources = gnome.compile_resources(
  'ggate-resources',
  resources_xml,
  source_dir: [meson.current_source_dir(), meson.current_source_dir() / '..'],
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

install_subdir('actions',  install_dir: pkgdatadir / 'icons')
install_subdir('components',  install_dir: pkgdatadir / 'icons')
install_subdir('../themes', install_dir: pkgdatadir)