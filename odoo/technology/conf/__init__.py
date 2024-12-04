# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

""" Library-wide configuration variables.

It is in mainly unprocessed form, e.g. addons_path is a string with
commas-separated paths. The aim is to have code related to configuration
(command line parsing, configuration file loading and saving, ...) 
in this module and provide real Python variables, e.g. addons_paths 
is really a list of paths.
"""

from .config import config, configmanager, _get_default_datadir, addons_paths, server_wide_modules
