import os
from subprocess import call
import pathlib

pkg = 'glogic'
version='3.0.0'
here = pathlib.Path(__file__).parent

tempdirs = ['deb_dist', f'{pkg}.egg-info']

call('python3 setup.py --command-packages=stdeb.command sdist_dsc --compat 11 --with-python3 True'.split())
os.chdir(f'deb_dist/{pkg}-{version}')
os.system(f'dpkg-buildpackage -rfakeroot -uc -us')

print("Cleaning.... \n\n")

os.system('python3 setup.py clean')

os.system('cd ..')
db_file = [f'deb_dist/{x}' for x in os.listdir('../') if x.endswith('.deb')][0]
os.chdir(here)
os.system(f"mv {db_file} {here}/dist/{db_file.split('/')[-1]} ")
for dir in tempdirs:
    os.system(f'rm -rf {dir}')

#os.system()

        