icon_files = [
  # Components
  '7seg.svg',
  'adder.svg',
  'counter.svg',
  'dff.svg',
  'jkff.svg',
  'pipo.svg',
  'piso.svg',
  'rsff.svg',
  'sipo.svg',
  'siso.svg',
  'timer.svg',

  # Actions
  'flip-horizontal.svg',
  'flip-vertical.svg',
  'rotate-left.svg',
  'rotate-right.svg',
]

icon_files_xml = []
foreach file: icon_files
  icon_files_xml += '<file preprocess="xml-stripblanks">' + file + '</file>'
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
