import os
from setuptools import find_packages, setup
import pathlib

here = pathlib.Path(__file__).parent
os.chdir(here)

icons = {
    "16": ['data/images/glogic-small.ico'],
    "96": ['data/images/glogic.png'],
    "48": ['data/images/glogic.ico'],
    "scalable": ['data/icons/scalable/glogic.svg']
}

os.system('chmod +777 data/org.astralco.glogic.desktop')
os.system('chmod +777 bin/glogic')

setup(
    name="glogic",
    version="3.0.0",
    author="Koichi Akabe ",
    author_email='<vbkaisetsu@gmail.com>',
    maintainer='Ekure Edem',
    maintainer_email="ekureedem480@gmail.com",
    description='A logic gate simulator for linux developed with Gtk and python',
    long_description=str(open('README.md').read()),
    long_description_content_type="text/markdown",
    license="GPL v3",
    keywords="logic circuit simulation simulate gates computers buffers",
    python_requires=">=3",
    scripts=["bin/glogic"],
    packages=['glogic', 'glogic.Components'],
    package_data={
        'glogic': [
            'images/glogic.ico', 
            'images/add-net.png', 
            'images/glogic.png', 
            'images/add-component.png', 
            'images/components', 
            'images/glogic-small.ico', 
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
        ("share/applications", ["data/org.astralco.glogic.desktop"]),
        ("share/icons/hicolor/96x96/apps", icons["96"]),
        ("share/icons/hicolor/48x48/apps", icons["48"]),
        ("share/icons/hicolor/16x16/apps", icons["16"]),
        ("share/icons/hicolor/scalable/apps", icons["scalable"]),
    ]
)
