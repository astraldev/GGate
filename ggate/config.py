from os import path
from packaging.version import Version

DATADIR = '/'.join(__file__.split("/")[:-1]) + '/'
VERSION = "5.0.0"
APP_PREFIX = "org.astralco.GGate"

# True when running from a source checkout (run.py is adjacent to the ggate package)
RUNNING_FROM_SOURCE = path.isfile(path.join(path.dirname(path.dirname(__file__)), "run.py"))

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
