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

icon_files_xml = []
foreach file: icon_files
  icon_files_xml += '<file preprocess="xml-stripblanks">' + file + '</file>'
endforeach

# Collect theme JSON filenames from ../themes/ to bundle into the gresource
theme_files_list = run_command(
  'sh', '-c', 'for f in "$0"/*.json; do [ -e "$f" ] && basename "$f"; done',
  meson.project_source_root() / 'data/themes',
  check: true
).stdout().strip().split('\n')

theme_files_xml = []
foreach basename: theme_files_list
  if basename != ''
    # alias keeps the resource path clean (<prefix>/<basename>); disk path is ../themes via source_dir
    theme_files_xml += '<file alias="' + basename + '">themes/' + basename + '</file>'
  endif
endforeach

resources_xml = configure_file(
  input: 'resources.xml.in',
  output: 'resources.xml',
  configuration: {
    'ICON_FILES': '\n    '.join(icon_files_xml),
    'THEME_FILES': '\n    '.join(theme_files_xml),
    'PREFIX': gresource_prefix,
  }
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