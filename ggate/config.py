# -*- coding: utf-8; indent-tabs-mode: t; tab-width: 4 -*-
from packaging.version import Version

DATADIR = '/'.join(__file__.split("/")[:-1]) + '/'
VERSION = "4.0.0"

compatibility = {
  "version": VERSION,
  "required": "2.6.0",
}

def is_compatible(target: str) -> int:
    print(target, compatibility["required"])
    if Version(target) < Version(compatibility["required"]):
        return -1 # Lower version needed
    elif Version(target) > Version(compatibility["version"]):
        return 1 # Higher version needed
    return 0
