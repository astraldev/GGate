from os import path
from packaging.version import Version

# Determine if running from source checkout (run.py is adjacent to the parent directory of this file)
_parent_dir = path.dirname(path.dirname(path.abspath(__file__)))
RUNNING_FROM_SOURCE = path.isfile(path.join(_parent_dir, "run.py"))

if RUNNING_FROM_SOURCE:
    DATADIR = path.join(_parent_dir, "data")
    ICONDIR = path.join(DATADIR, "images")
    APP_PREFIX = "org.astralco.ggate.Dev"
else:
    DATADIR = "@pkgdatadir@"
    ICONDIR = path.join(DATADIR, "icons")
    APP_PREFIX = "@APP_PREFIX@"

VERSION = "@VERSION@"

compatibility = {
  "version": VERSION,
  "required": "2.6.0",
}

def is_compatible(target: str) -> int:
    if Version(target) < Version(compatibility["required"]):
        return -1 # Lower version needed
    elif Version(target) > Version(compatibility["version"]):
        return 1 # Higher version needed
    return 0

