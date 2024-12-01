# -*- coding: utf-8 -*-

"""
This is the bottom layer, which can be named: basic technology layer. It 
is a layer that serves to build the entire Odoo system from the bottom up.
This layer mainly uses technical encapsulation to shield technical details
and provide the most basic capabilities, including:
    1. Command line tools
    2. Configuration management
    3. Request and response framework
    4. Database connection
    5. Cache
    6. Adjustable capabilities
"""
import sys


# Command line tools
from .cli import *

# Configuration management
'''
In order to facilitate easy access to configuration at all levels, we consider
exposing the configuration namespace to the outermost layer.
'''
from .conf import *
# sys.modules['odoo.conf'] = conf

# Request and response framework
from .framework import *

# Database connection
from .db import *

# Cache
from .cache import *
# sys.modules['odoo.cache'] = cache

# Adjustable capabilities
from .adjustable import *
# sys.modules['odoo.adjustable'] = adjustable