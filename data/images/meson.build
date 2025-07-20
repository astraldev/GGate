icon_files = files(
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
)

icon_files_xml = []
foreach file: icon_files
  icon_files_xml += '<file preprocess="xml-stripblanks">' + file.full_path() + '</file>'
endforeach

resources_xml = configure_file(
  input: 'resources.xml.in',
  output: 'resources.xml',
  configuration: {
    'ICON_FILES': '\n    '.join(icon_files_xml),
    'PREFIX': prefix,
  }
)

ggate_resources = gnome.compile_resources(
  'ggate-resources',
  resources_xml,
  source_dir: meson.current_source_dir(),
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

install_subdir('icons/components',  install_dir: pkgdatadir)
install_subdir('icons/actions',  install_dir: pkgdatadir)