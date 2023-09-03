import os
from subprocess import call
import pathlib
import sys

pkg = 'ggate'
version='4.0.0-rc'
here = pathlib.Path(__file__).parent
email = 'ekureedem480@gmail.com'
full_name = 'Ekure Edem'

rules = f"""#!/usr/bin/make -f
export PYBUILD_NAME={pkg}
export PYBUILD_VERBOSE=1
export DH_VERBOSE=1
export DH_VERBOSE = 1
%:
	dh $@ --with python3 --buildsystem=pybuild"""

os.chdir(here)
tempdirs = [f'dist/{pkg}-{version}', f'{pkg}.egg-info']

call('python3 setup.py sdist'.split())

os.chdir(f'{here}/dist')

os.system(f'debmake -s -b ":py3" -e {email} -f "{full_name}" -p "{pkg}" -u "{version}" -a {pkg}-{version}.tar.gz')
os.chdir(f'{here}/dist/{pkg}-{version}')

print("\nEdit the following files \n")
print(f"{here}/dist/{pkg}-{version}/debian/control")
print(f"{here}/dist/{pkg}-{version}/debian/changelog")
print(f"{here}/dist/{pkg}-{version}/debian/README.Debian")

open(f'{here}/dist/{pkg}-{version}/debian/rules', 'w').write(rules)

def _clean():
    print("Cleaning.... \n")
    os.chdir(f'{here}')
    os.system('python3 setup.py clean')
    for dir in tempdirs:
        os.system(f'rm -rf {dir}')
    
    for file in os.listdir('dist'):
        if os.path.isfile(f'dist/{file}'):
            if not file.endswith('.tar.gz') and not file.endswith('.deb'):
                os.remove(f'dist/{file}')
        else:
            os.system(f'rm -rf dist/{file}')

tries = 0
while input("Are you done? [Y/N]: ").lower() != 'y' :
    if tries >= 10:
        print("Out of tries")
        _clean()
        sys.exit(1)
    tries += 1
print("\nBegining Build\n")
os.system(f'dpkg-buildpackage')
print("\nBuild over\n")

_clean()
