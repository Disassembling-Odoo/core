# -*- coding: utf-8 -*-
'''
Database Operations
'''

import json
import logging
import os
import shutil
import re
import subprocess
import tempfile
import zipfile
from contextlib import closing

import psycopg2
from psycopg2.extensions import quote_ident
from decorator import decorator
from pytz import country_timezones

from odoo import SUPERUSER_ID
from odoo.exceptions import AccessDenied
import odoo.release
import odoo.tools

from ..conf import config
from ..utils import db_utils as DBUtils
from .sql import SQL
from .sql_db import db_connect

_logger = logging.getLogger(__name__)


class DatabaseExists(Warning):
    pass

def database_identifier(cr, name: str) -> SQL:
    """Quote a database identifier.

    Use instead of `SQL.identifier` to accept all kinds of identifiers.
    """
    name = quote_ident(name, cr._cnx)
    return SQL(name)

def check_db_management_enabled(method):
    def if_db_mgt_enabled(method, self, *args, **kwargs):
        if not odoo.conf.config['list_db']:
            _logger.error('Database management functions blocked, admin disabled database listing')
            raise AccessDenied()
        return method(self, *args, **kwargs)
    return decorator(if_db_mgt_enabled, method)

def available_db_list(force=False, host=None):
    """
    Get the list of available databases.

    :param bool force: See :func:`~odoo.technology.framework.list_dbs`:
    :param host: The Host used to replace %h and %d in the dbfilters
        regexp. Taken from the current request when omitted.
    :returns: the list of available databases
    :rtype: List[str]
    """
    try:
        dbs = odoo.technology.db.list_dbs(force)
    except psycopg2.OperationalError:
        return []
    return db_filter(dbs, host)

def db_filter(dbs, host=None):
    """
    Return the subset of ``dbs`` that match the dbfilter or the dbname
    server configuration. In case neither are configured, return ``dbs``
    as-is.

    :param Iterable[str] dbs: The list of database names to filter.
    :param host: The Host used to replace %h and %d in the dbfilters
        regexp. Taken from the current request when omitted.
    :returns: The original list filtered.
    :rtype: List[str]
    """

    if config['dbfilter']:
        #        host
        #     -----------
        # www.example.com:80
        #     -------
        #     domain
        host = host.partition(':')[0]
        if host.startswith('www.'):
            host = host[4:]
        domain = host.partition('.')[0]

        dbfilter_re = re.compile(
            config["dbfilter"].replace("%h", re.escape(host))
                              .replace("%d", re.escape(domain)))
        return [db for db in dbs if dbfilter_re.match(db)]

    if config['db_name']:
        # In case --db-filter is not provided and --database is passed, Odoo will
        # use the value of --database as a comma separated list of exposed databases.
        exposed_dbs = {db.strip() for db in config['db_name'].split(',')}
        return sorted(exposed_dbs.intersection(dbs))

    return list(dbs)


def list_dbs(force=False):
    if not odoo.conf.config['list_db'] and not force:
        raise AccessDenied()

    if not odoo.conf.config['dbfilter'] and odoo.conf.config['db_name']:
        # In case --db-filter is not provided and --database is passed, Odoo will not
        # fetch the list of databases available on the postgres server and instead will
        # use the value of --database as comma seperated list of exposed databases.
        res = sorted(db.strip() for db in odoo.conf.config['db_name'].split(','))
        return res

    chosen_template = odoo.conf.config['db_template']
    templates_list = tuple({'postgres', chosen_template})
    db = odoo.technology.db.db_connect('postgres')
    with closing(db.cursor()) as cr:
        try:
            cr.execute("select datname from pg_database where datdba=(select usesysid from pg_user where usename=current_user) and not datistemplate and datallowconn and datname not in %s order by datname", (templates_list,))
            return [name for (name,) in cr.fetchall()]
        except Exception:
            _logger.exception('Listing databases failed:')
            return []

def check_db_exist(db_name):
    ## Not True: in fact, check if connection to database is possible. The database may exists
    try:
        db = odoo.technology.db.db_connect(db_name)
        with db.cursor():
            return True
    except Exception:
        return False

def create_empty_database(name):
    db = odoo.technology.db.db_connect('postgres')
    with closing(db.cursor()) as cr:
        chosen_template = odoo.conf.config['db_template']
        cr.execute("SELECT datname FROM pg_database WHERE datname = %s",
                   (name,), log_exceptions=False)
        if cr.fetchall():
            raise DatabaseExists("database %r already exists!" % (name,))
        else:
            # database-altering operations cannot be executed inside a transaction
            cr.rollback()
            cr._cnx.autocommit = True

            # 'C' collate is only safe with template0, but provides more useful indexes
            cr.execute(SQL(
                "CREATE DATABASE %s ENCODING 'unicode' %s TEMPLATE %s",
                database_identifier(cr, name),
                SQL("LC_COLLATE 'C'") if chosen_template == 'template0' else SQL(""),
                database_identifier(cr, chosen_template),
            ))

    # TODO: add --extension=trigram,unaccent
    try:
        db = odoo.technology.db.db_connect(name)
        with db.cursor() as cr:
            cr.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            if odoo.conf.config['unaccent']:
                cr.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
                # From PostgreSQL's point of view, making 'unaccent' immutable is incorrect
                # because it depends on external data - see
                # https://www.postgresql.org/message-id/flat/201012021544.oB2FiTn1041521@wwwmaster.postgresql.org#201012021544.oB2FiTn1041521@wwwmaster.postgresql.org
                # But in the case of Odoo, we consider that those data don't
                # change in the lifetime of a database. If they do change, all
                # indexes created with this function become corrupted!
                cr.execute("ALTER FUNCTION unaccent(text) IMMUTABLE")
    except psycopg2.Error as e:
        _logger.warning("Unable to create PostgreSQL extensions : %s", e)

    # restore legacy behaviour on pg15+
    try:
        db = odoo.technology.db.db_connect(name)
        with db.cursor() as cr:
            cr.execute("GRANT CREATE ON SCHEMA PUBLIC TO PUBLIC")
    except psycopg2.Error as e:
        _logger.warning("Unable to make public schema public-accessible: %s", e)

@check_db_management_enabled
def drop_db(db_name):
    if db_name not in list_dbs(True):
        return False
    odoo.microkernel.modules.registry.Registry.delete(db_name)
    odoo.technology.db.close_db(db_name)

    db = odoo.technology.db.db_connect('postgres')
    with closing(db.cursor()) as cr:
        # database-altering operations cannot be executed inside a transaction
        cr._cnx.autocommit = True
        _drop_conn(cr, db_name)

        try:
            cr.execute(SQL('DROP DATABASE %s', database_identifier(cr, db_name)))
        except Exception as e:
            _logger.info('DROP DB: %s failed:\n%s', db_name, e)
            raise Exception("Couldn't drop database %s: %s" % (db_name, e))
        else:
            _logger.info('DROP DB: %s', db_name)

    fs = odoo.conf.config.filestore(db_name)
    if os.path.exists(fs):
        shutil.rmtree(fs)
    return True

@check_db_management_enabled
def dump_db_manifest(cr):
    pg_version = "%d.%d" % divmod(cr._obj.connection.server_version / 100, 100)
    cr.execute("SELECT name, latest_version FROM ir_module_module WHERE state = 'installed'")
    modules = dict(cr.fetchall())
    manifest = {
        'odoo_dump': '1',
        'db_name': cr.dbname,
        'version': odoo.release.version,
        'version_info': odoo.release.version_info,
        'major_version': odoo.release.major_version,
        'pg_version': pg_version,
        'modules': modules,
    }
    return manifest

@check_db_management_enabled
def dump_db(db_name, stream, backup_format='zip'):
    """Dump database `db` into file-like object `stream` if stream is None
    return a file object with the dump """

    _logger.info('DUMP DB: %s format %s', db_name, backup_format)

    cmd = [DBUtils.find_pg_tool('pg_dump', odoo.conf.config), '--no-owner', db_name]
    env = DBUtils.exec_pg_environ(odoo.conf.config)

    if backup_format == 'zip':
        with tempfile.TemporaryDirectory() as dump_dir:
            filestore = odoo.conf.config.filestore(db_name)
            if os.path.exists(filestore):
                shutil.copytree(filestore, os.path.join(dump_dir, 'filestore'))
            with open(os.path.join(dump_dir, 'manifest.json'), 'w') as fh:
                db = odoo.technology.db.db_connect(db_name)
                with db.cursor() as cr:
                    json.dump(dump_db_manifest(cr), fh, indent=4)
            cmd.insert(-1, '--file=' + os.path.join(dump_dir, 'dump.sql'))
            subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
            if stream:
                odoo.tools.osutil.zip_dir(dump_dir, stream, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
            else:
                t=tempfile.TemporaryFile()
                odoo.tools.osutil.zip_dir(dump_dir, t, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
                t.seek(0)
                return t
    else:
        cmd.insert(-1, '--format=c')
        stdout = subprocess.Popen(cmd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE).stdout
        if stream:
            shutil.copyfileobj(stdout, stream)
        else:
            return stdout

@check_db_management_enabled
def restore_db(db, dump_file, copy=False, neutralize_database=False):
    assert isinstance(db, str)
    if check_db_exist(db):
        _logger.warning('RESTORE DB: %s already exists', db)
        raise Exception("Database already exists")

    _logger.info('RESTORING DB: %s', db)
    create_empty_database(db)

    filestore_path = None
    with tempfile.TemporaryDirectory() as dump_dir:
        if zipfile.is_zipfile(dump_file):
            # v8 format
            with zipfile.ZipFile(dump_file, 'r') as z:
                # only extract known members!
                filestore = [m for m in z.namelist() if m.startswith('filestore/')]
                z.extractall(dump_dir, ['dump.sql'] + filestore)

                if filestore:
                    filestore_path = os.path.join(dump_dir, 'filestore')

            pg_cmd = 'psql'
            pg_args = ['-q', '-f', os.path.join(dump_dir, 'dump.sql')]

        else:
            # <= 7.0 format (raw pg_dump output)
            pg_cmd = 'pg_restore'
            pg_args = ['--no-owner', dump_file]

        r = subprocess.run(
            [DBUtils.find_pg_tool(pg_cmd, odoo.conf.config), '--dbname=' + db, *pg_args],
            env=DBUtils.exec_pg_environ(odoo.conf.config),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        if r.returncode != 0:
            raise Exception("Couldn't restore database")

        registry = odoo.microkernel.modules.registry.Registry.new(db)
        with registry.cursor() as cr:
            env = odoo.microkernel.api.Environment(cr, SUPERUSER_ID, {})
            if copy:
                # if it's a copy of a database, force generation of a new dbuuid
                env['ir.config_parameter'].init(force=True)
            if neutralize_database:
                odoo.microkernel.modules.neutralize.neutralize_database(cr)

            if filestore_path:
                filestore_dest = env['ir.attachment']._filestore()
                shutil.move(filestore_path, filestore_dest)

    _logger.info('RESTORE DB: %s', db)

@check_db_management_enabled
def rename_db(old_name, new_name):
    odoo.microkernel.modules.registry.Registry.delete(old_name)
    odoo.technology.db.close_db(old_name)

    db = odoo.technology.db.db_connect('postgres')
    with closing(db.cursor()) as cr:
        # database-altering operations cannot be executed inside a transaction
        cr._cnx.autocommit = True
        _drop_conn(cr, old_name)
        try:
            cr.execute(SQL('ALTER DATABASE %s RENAME TO %s', database_identifier(cr, old_name), database_identifier(cr, new_name)))
            _logger.info('RENAME DB: %s -> %s', old_name, new_name)
        except Exception as e:
            _logger.info('RENAME DB: %s -> %s failed:\n%s', old_name, new_name, e)
            raise Exception("Couldn't rename database %s to %s: %s" % (old_name, new_name, e))

    old_fs = odoo.conf.config.filestore(old_name)
    new_fs = odoo.conf.config.filestore(new_name)
    if os.path.exists(old_fs) and not os.path.exists(new_fs):
        shutil.move(old_fs, new_fs)
    return True

@check_db_management_enabled
def duplicate_db(db_original_name, db_name, neutralize_database=False):
    _logger.info('Duplicate database `%s` to `%s`.', db_original_name, db_name)
    odoo.technology.db.close_db(db_original_name)
    db = odoo.technology.db.db_connect('postgres')
    with closing(db.cursor()) as cr:
        # database-altering operations cannot be executed inside a transaction
        cr._cnx.autocommit = True
        _drop_conn(cr, db_original_name)
        cr.execute(SQL(
            "CREATE DATABASE %s ENCODING 'unicode' TEMPLATE %s",
            database_identifier(cr, db_name),
            database_identifier(cr, db_original_name),
        ))

    registry = odoo.microkernel.modules.registry.Registry.new(db_name)
    with registry.cursor() as cr:
        # if it's a copy of a database, force generation of a new dbuuid
        env = odoo.microkernel.api.Environment(cr, SUPERUSER_ID, {})
        env['ir.config_parameter'].init(force=True)
        if neutralize_database:
            odoo.microkernel.modules.neutralize.neutralize_database(cr)

    from_fs = odoo.conf.config.filestore(db_original_name)
    to_fs = odoo.conf.config.filestore(db_name)
    if os.path.exists(from_fs) and not os.path.exists(to_fs):
        shutil.copytree(from_fs, to_fs)
    return True

def list_db_incompatible(databases):
    """"Check a list of databases if they are compatible with this version of Odoo

        :param databases: A list of existing Postgresql databases
        :return: A list of databases that are incompatible
    """
    incompatible_databases = []
    server_version = '.'.join(str(v) for v in odoo.release.version_info[:2])
    for database_name in databases:
        with closing(db_connect(database_name).cursor()) as cr:
            if odoo.technology.db.table_exists(cr, 'ir_module_module'):
                cr.execute("SELECT latest_version FROM ir_module_module WHERE name=%s", ('base',))
                base_version = cr.fetchone()
                if not base_version or not base_version[0]:
                    incompatible_databases.append(database_name)
                else:
                    # e.g. 10.saas~15
                    local_version = '.'.join(base_version[0].split('.')[:2])
                    if local_version != server_version:
                        incompatible_databases.append(database_name)
            else:
                incompatible_databases.append(database_name)
    for database_name in incompatible_databases:
        # release connection
        odoo.technology.db.close_db(database_name)
    return incompatible_databases


def _drop_conn(cr, db_name):
    # Try to terminate all other connections that might prevent
    # dropping the database
    try:
        # PostgreSQL 9.2 renamed pg_stat_activity.procpid to pid:
        # http://www.postgresql.org/docs/9.2/static/release-9-2.html#AEN110389
        pid_col = 'pid' if cr._cnx.server_version >= 90200 else 'procpid'

        cr.execute("""SELECT pg_terminate_backend(%(pid_col)s)
                      FROM pg_stat_activity
                      WHERE datname = %%s AND
                            %(pid_col)s != pg_backend_pid()""" % {'pid_col': pid_col},
                   (db_name,))
    except Exception:
        pass