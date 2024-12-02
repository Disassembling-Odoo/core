# -*- coding: utf-8 -*-
import os
import re

from odoo.tools.misc import which
from odoo.exceptions import ValidationError

regex_pg_name = re.compile(r'^[a-z_][a-z0-9_$]*$', re.I)

def check_pg_name(name):
    """ Check whether the given name is a valid PostgreSQL identifier name. """
    if not regex_pg_name.match(name):
        raise ValidationError("Invalid characters in table name %r" % name)
    if len(name) > 63:
        raise ValidationError("Table name %r is too long" % name)

def find_pg_tool(name):
    path = None
    if config['pg_path'] and config['pg_path'] != 'None':
        path = config['pg_path']
    try:
        return which(name, path=path)
    except IOError:
        raise Exception('Command `%s` not found.' % name)

def exec_pg_environ(config):
    """
    Force the database PostgreSQL environment variables to the database
    configuration of Odoo.

    Note: On systems where pg_restore/pg_dump require an explicit password
    (i.e.  on Windows where TCP sockets are used), it is necessary to pass the
    postgres user password in the PGPASSWORD environment variable or in a
    special .pgpass file.

    See also http://www.postgresql.org/docs/8.4/static/libpq-envars.html
    """
    env = os.environ.copy()
    if config['db_host']:
        env['PGHOST'] = config['db_host']
    if config['db_port']:
        env['PGPORT'] = str(config['db_port'])
    if config['db_user']:
        env['PGUSER'] = config['db_user']
    if config['db_password']:
        env['PGPASSWORD'] = config['db_password']
    return env