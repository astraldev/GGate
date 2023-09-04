import os
from setuptools import setup
import pathlib
import ggate

here = pathlib.Path(__file__).parent
help_translations = []
translations = []
pkg_name = 'ggate'
base = 'data/help'
help_files = []

os.chdir(here)

for root, folders, files in os.walk(base):
    for folder in folders:
        if root+'/'+folder not in help_translations:
            help_translations.append(root+'/'+folder)
    if root == base:
        for folder in folders:
            translations.append(folder)

for folder in help_translations:
    if folder.split('/')[1] in translations:
        parts = list(folder.split('/'))
        parts.insert(2, pkg_name)
        parts = ['share'] + parts
        fd = "/".join(parts)
        help_files.append((fd, [folder+'/'+x for x in os.listdir(folder) if os.path.isfile(folder+'/'+x)]))

icons = {
    "16": ['data/images/ggate-small.ico'],
    "96": ['data/images/ggate.png'],
    "48": ['data/images/ggate.ico'],
    "scalable": ['data/icons/scalable/ggate.svg'],

    "mime": {
        '16': ['data/images/mime/16x16/text-glc.png'],
        '32': ['data/images/mime/32x32/text-glc.png'],
        '24': ['data/images/mime/24x24/text-glc.png'],
        '48': ['data/images/mime/48x48/text-glc.png'],
        '256': ['data/images/mime/256x256/text-glc.png'],

        '64': ['data/images/mime/64x64/text-glc.png'],
        '96': ['data/images/mime/96x96/text-glc.png'],
        '128':['data/images/mime/128x128/text-glc.png'],
        '512': ['data/images/mime/512x512/text-glc.png']
    }
}

mime_sizes = {
    'yaru': ['16', '32', '24', '48', '256']
}

mimes = []
for sizes in icons['mime'].keys():
    mimes.append((f'share/icons/hicolor/{sizes}x{sizes}/mimetypes', icons['mime'][sizes]))
    if sizes in mime_sizes['yaru']:
        mimes.append((f'share/icons/Yaru/{sizes}x{sizes}/mimetypes', icons['mime'][sizes]))

os.system(f'chmod +777 {here}/data/org.astralco.ggate.desktop')
os.system(f'chmod +777 {here}/bin/ggate')

setup(
    name="ggate",
    version=ggate.__version__,
    author="Koichi Akabe ",
    author_email='vbkaisetsu@gmail.com',
    maintainer='Ekure Edem',
    maintainer_email="ekureedem480@gmail.com",
    description='A logic gate simulator for linux developed with Gtk and python',
    long_description=str(open('README.md').read()),
    long_description_content_type="text/markdown",
    license="GPL v3",
    keywords="logic circuit simulation simulate gates computers buffers",
    python_requires=">=3",
    scripts=['bin/ggate'],
    packages=['ggate', 'ggate.Components'],
    package_data={
        'ggate': [
            'images/ggate.ico', 
            'images/add-net.png', 
            'images/ggate.png', 
            'images/add-component.png', 
            'images/components', 
            'images/ggate-small.ico', 
            'images/components/piso.png', 
            'images/components/siso.png', 
            'images/components/gnd.png', 
            'images/components/dff.png', 
            'images/components/tribuff.png', 
            'images/components/or.png', 
            'images/components/osc.png', 
            'images/components/vdd.png', 
            'images/components/probe.png', 
            'images/components/and.png', 
            'images/components/rsff.png', 
            'images/components/counter.png', 
            'images/components/text.png', 
            'images/components/led.png', 
            'images/components/sipo.png', 
            'images/components/nand.png', 
            'images/components/7seg.png', 
            'images/components/pipo.png', 
            'images/components/not.png', 
            'images/components/tff.png', 
            'images/components/nor.png', 
            'images/components/jkff.png', 
            'images/components/adder.png', 
            'images/components/xor.png', 
            'images/components/sw.png'
        ]
    },
    data_files=[
        *help_files,
        *mimes,
        ("share/applications", ["data/org.astralco.ggate.desktop"]),
        ("share/mime/packages", ["data/ggate.xml"]),
        ("share/icons/hicolor/96x96/apps", icons["96"]),
        ("share/icons/hicolor/48x48/apps", icons["48"]),
        ("share/icons/hicolor/16x16/apps", icons["16"]),
        ("share/icons/hicolor/scalable/apps", icons["scalable"]),
    ]
)
