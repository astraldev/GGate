import os
from subprocess import call
import pathlib
from metadata import *

here = pathlib.Path(__file__).parent.parent

rules = f"""#!/usr/bin/make -f
export PYBUILD_NAME={package}
export PYBUILD_VERBOSE=1
export DH_VERBOSE=1
export DH_VERBOSE = 1
%:
	dh $@ --with python3 --buildsystem=pybuild

"""

os.chdir(here)
tempdirs = [f'dist/{package}-{version}', f'{package}.egg-info']


def main():
    print("Starting...")
    call('python3 setup.py sdist'.split())
    os.chdir(f'{here}/dist')

    print(license)

    os.system(
        f'debmake -s -b ":py3" -e {email} -r {revision} -f "{full_name}" -p "{package}" -u "{version}" -a {package}-{version}.tar.gz')
    os.chdir(f'{here}/dist/{package}-{version}')

    open(f'{here}/dist/{package}-{version}/debian/rules', 'w').write(rules)
    open(f"{here}/dist/{package}-{version}/debian/README.Debian",
         "w").write(readme_debian)
    
    open(f"{here}/dist/{package}-{version}/debian/changelog",
         "w").write(parsed_changelog)
    
    copyright = get_copyright_file(
        open(f"{here}/dist/{package}-{version}/debian/copyright", "r").read())
    open(f"{here}/dist/{package}-{version}/debian/copyright", "w").write(copyright)

    control = get_control_file(
        open(f"{here}/dist/{package}-{version}/debian/control", "r").read())
    open(f"{here}/dist/{package}-{version}/debian/control", "w").write(control)

    print("\nBegining Build\n")
    os.system(f'debuild')
    print("\nBuild over\n")

def _clean():
    print("Cleaning....")
    os.chdir(f'{here}')
    os.system('python3 setup.py clean')
    for dir in tempdirs:
        os.system(f'rm -rf {dir}')

    for file in os.listdir('dist'):
        if os.path.isfile(f'dist/{file}'):
            if file.endswith('.build'):
                os.remove(f'dist/{file}')
        else:
            os.system(f'rm -rf dist/{file}')




if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        _clean()
        print("Done")
    else:
        main()
        _clean()
        print("Done")

