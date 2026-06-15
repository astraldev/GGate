#!/bin/sh
# Emit __pycache__ dirs relative to the first arg, for meson's
# install_subdir exclude_directories property.

# enter the package dir meson passed as $1, or exit quietly if it's missing
cd "$1" 2>/dev/null || exit 0

# list every __pycache__ dir, stripping the leading "./" so paths stay relative
find . -type d -name '__pycache__' | sed 's|^\./||'
