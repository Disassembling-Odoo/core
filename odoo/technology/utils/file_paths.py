import os
import typing
import tempfile
from contextlib import ContextDecorator, contextmanager

import odoo
import odoo.addons
from odoo.technology.conf import config

# ----------------------------------------------------------
# File paths
# ----------------------------------------------------------
def file_path(file_path: str, filter_ext: tuple[str, ...] = ('',), temporary_paths: list | tuple | None = None) -> str:
    """Verify that a file exists under a known `addons_path` directory and return its full path.

    Examples::

    >>> file_path('hr')
    >>> file_path('hr/static/description/icon.png')
    >>> file_path('hr/static/description/icon.png', filter_ext=('.png', '.jpg'))

    :param str file_path: absolute file path, or relative path within any `addons_path` directory
    :param list[str] filter_ext: optional list of supported extensions (lowercase, with leading dot)
    :param temporary_paths: temporary_paths = env.transaction._Transaction__file_open_tmp_paths if env else ()
    :return: the absolute path to the file
    :raise FileNotFoundError: if the file is not found under the known `addons_path` directories
    :raise ValueError: if the file doesn't have one of the supported extensions (`filter_ext`)
    """
    root_path = os.path.abspath(config['root_path'])
    temporary_paths = temporary_paths if temporary_paths else ()
    addons_paths = [*odoo.addons.__path__, root_path, *temporary_paths]
    is_abs = os.path.isabs(file_path)
    normalized_path = os.path.normpath(os.path.normcase(file_path))

    if filter_ext and not normalized_path.lower().endswith(filter_ext):
        raise ValueError("Unsupported file: " + file_path)

    # ignore leading 'addons/' if present, it's the final component of root_path, but
    # may sometimes be included in relative paths
    if normalized_path.startswith('addons' + os.sep):
        normalized_path = normalized_path[7:]

    for addons_dir in addons_paths:
        # final path sep required to avoid partial match
        parent_path = os.path.normpath(os.path.normcase(addons_dir)) + os.sep
        fpath = (normalized_path if is_abs else
                 os.path.normpath(os.path.normcase(os.path.join(parent_path, normalized_path))))
        if fpath.startswith(parent_path) and os.path.exists(fpath):
            return fpath

    raise FileNotFoundError("File not found: " + file_path)


def file_open(name: str, mode: str = "r", filter_ext: tuple[str, ...] = (), temporary_paths: list | tuple | None = None):
    """Open a file from within the addons_path directories, as an absolute or relative path.

    Examples::

        >>> file_open('hr/static/description/icon.png')
        >>> file_open('hr/static/description/icon.png', filter_ext=('.png', '.jpg'))
        >>> with file_open('/opt/odoo/addons/hr/static/description/icon.png', 'rb') as f:
        ...     contents = f.read()

    :param name: absolute or relative path to a file located inside an addon
    :param mode: file open mode, as for `open()`
    :param list[str] filter_ext: optional list of supported extensions (lowercase, with leading dot)
    :param temporary_paths: temporary_paths = env.transaction._Transaction__file_open_tmp_paths if env else ()
    :return: file object, as returned by `open()`
    :raise FileNotFoundError: if the file is not found under the known `addons_path` directories
    :raise ValueError: if the file doesn't have one of the supported extensions (`filter_ext`)
    """
    path = file_path(name, filter_ext=filter_ext, temporary_paths=temporary_paths)
    if os.path.isfile(path):
        if 'b' not in mode:
            # Force encoding for text mode, as system locale could affect default encoding,
            # even with the latest Python 3 versions.
            # Note: This is not covered by a unit test, due to the platform dependency.
            #       For testing purposes you should be able to force a non-UTF8 encoding with:
            #         `sudo locale-gen fr_FR; LC_ALL=fr_FR.iso8859-1 python3 ...'
            # See also PEP-540, although we can't rely on that at the moment.
            return open(path, mode, encoding="utf-8")
        return open(path, mode)
    raise FileNotFoundError("Not a file: " + name)
