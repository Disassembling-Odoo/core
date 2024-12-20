# -*- coding: utf-8 -*-
# ruff: noqa: E402, F401
# Part of Odoo. See LICENSE file for full copyright and licensing details.

""" OpenERP core library."""

# ----------------------------------------------------------
# odoo must be a namespace package for odoo.addons to become one too
# https://packaging.python.org/guides/packaging-namespace-packages/
# ----------------------------------------------------------
import pkgutil
import os.path
__path__ = [
    os.path.abspath(path)
    for path in pkgutil.extend_path(__path__, __name__)
]

import sys
MIN_PY_VERSION = (3, 10)
MAX_PY_VERSION = (3, 12)
assert sys.version_info > MIN_PY_VERSION, f"Outdated python version detected, Odoo requires Python >= {'.'.join(map(str, MIN_PY_VERSION))} to run."

# ----------------------------------------------------------
# Shortcuts
# ----------------------------------------------------------
# The hard-coded super-user id (a.k.a. administrator, or root user).
SUPERUSER_ID = 1


def registry(database_name=None):
    """
    Return the model registry for the given database, or the database mentioned
    on the current thread. If the registry does not exist yet, it is created on
    the fly.
    """
    import warnings  # noqa: PLC0415
    warnings.warn("Use directly odoo.microkernel.modules.registry.Registry", DeprecationWarning, 2)
    if database_name is None:
        import threading
        database_name = threading.current_thread().dbname
    return microkernel.modules.registry.Registry(database_name)


# ----------------------------------------------------------
# Import tools to patch code and libraries
# required to do as early as possible for evented and timezone
# ----------------------------------------------------------
from . import _monkeypatches
_monkeypatches.patch_all()


# ----------------------------------------------------------
# Imports
# ----------------------------------------------------------
from . import tools
from . import technology
from .technology import conf
from .technology import cli

from . import upgrade  # this namespace must be imported first
from . import loglevels
from . import release
from . import addons

# ----------------------------------------------------------
# Model classes, fields, api decorators, and translations
# ----------------------------------------------------------
from odoo.tools.translate import _, _lt

# ----------------------------------------------------------
# Other imports, which may require stuff from above
# ----------------------------------------------------------
from . import microkernel