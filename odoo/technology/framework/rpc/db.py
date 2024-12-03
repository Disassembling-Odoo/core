# -*- coding: utf-8 -*-
import base64
import logging
import os
import tempfile
from contextlib import closing
from xml.etree import ElementTree as ET

import psycopg2
from psycopg2.extensions import quote_ident
from decorator import decorator
from pytz import country_timezones

import odoo
import odoo.release
import odoo.exceptions
import odoo.tools
import odoo.technology.db
from odoo.technology.db import check_db_management_enabled, create_empty_database
from odoo import SUPERUSER_ID
from odoo.technology.utils import db_utils as DBUtils

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# Master password required
#----------------------------------------------------------

# This should be moved to odoo.modules.db, along side initialize().
def _initialize_db(id, db_name, demo, lang, user_password, login='admin', country_code=None, phone=None):
    try:
        db = odoo.technology.db.db_connect(db_name)
        with closing(db.cursor()) as cr:
            # TODO this should be removed as it is done by Registry.new().
            odoo.modules.db.initialize(cr)
            odoo.conf.config['load_language'] = lang
            cr.commit()

        registry = odoo.modules.registry.Registry.new(db_name, demo, None, update_module=True)

        with closing(registry.cursor()) as cr:
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})

            if lang:
                modules = env['ir.module.module'].search([('state', '=', 'installed')])
                modules._update_translations(lang)

            if country_code:
                country = env['res.country'].search([('code', 'ilike', country_code)])[0]
                env['res.company'].browse(1).write({'country_id': country_code and country.id, 'currency_id': country_code and country.currency_id.id})
                if len(country_timezones.get(country_code, [])) == 1:
                    users = env['res.users'].search([])
                    users.write({'tz': country_timezones[country_code][0]})
            if phone:
                env['res.company'].browse(1).write({'phone': phone})
            if '@' in login:
                env['res.company'].browse(1).write({'email': login})

            # update admin's password and lang and login
            values = {'password': user_password, 'lang': lang}
            if login:
                values['login'] = login
                emails = odoo.tools.email_split(login)
                if emails:
                    values['email'] = emails[0]
            env.ref('base.user_admin').write(values)

            cr.commit()
    except Exception as e:
        _logger.exception('CREATE DATABASE failed:')

@check_db_management_enabled
def exp_create_database(db_name, demo, lang, user_password='admin', login='admin', country_code=None, phone=None):
    """ Similar to exp_create but blocking."""
    _logger.info('Create database `%s`.', db_name)
    create_empty_database(db_name)
    _initialize_db(id, db_name, demo, lang, user_password, login, country_code, phone)
    return True

def exp_duplicate_database(db_original_name, db_name, neutralize_database=False):
    return odoo.technology.db.duplicate_db(db_original_name, db_name, neutralize_database)

def exp_drop(db_name):
    return odoo.technology.db.drop_db(db_name)

@check_db_management_enabled
def exp_dump(db_name, format):
    with tempfile.TemporaryFile(mode='w+b') as t:
        odoo.technology.db.dump_db(db_name, t, format)
        t.seek(0)
        return base64.b64encode(t.read()).decode()

@check_db_management_enabled
def dump_db_manifest(cr):
    return odoo.technology.db.dump_db_manifest(cr)

def dump_db(db_name, stream, backup_format='zip'):
    return odoo.technology.db.dump_db(db_name, stream, backup_format)

@check_db_management_enabled
def exp_restore(db_name, data, copy=False):
    def chunks(d, n=8192):
        for i in range(0, len(d), n):
            yield d[i:i+n]
    data_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        for chunk in chunks(data):
            data_file.write(base64.b64decode(chunk))
        data_file.close()
        odoo.technology.db.restore_db(db_name, data_file.name, copy=copy)
    finally:
        os.unlink(data_file.name)
    return True

def exp_rename(old_name, new_name):
    return odoo.technology.db.rename_db(old_name, new_name)

@check_db_management_enabled
def exp_change_admin_password(new_password):
    odoo.conf.config.set_admin_password(new_password)
    odoo.conf.config.save(['admin_passwd'])
    return True

@check_db_management_enabled
def exp_migrate_databases(databases):
    for db in databases:
        _logger.info('migrate database %s', db)
        odoo.conf.config['update']['base'] = True
        odoo.modules.registry.Registry.new(db, force_demo=False, update_module=True)
    return True

#----------------------------------------------------------
# No master password required
#----------------------------------------------------------

@odoo.tools.mute_logger('odoo.technology.db')
def exp_db_exist(db_name):
    return odoo.technology.db.check_db_exist(db_name)

def exp_list(document=False):
    if not odoo.conf.config['list_db']:
        raise odoo.exceptions.AccessDenied()
    return odoo.technology.db.list_dbs()

def exp_list_lang():
    return odoo.tools.misc.scan_languages()

def exp_list_countries():
    list_countries = []
    root = ET.parse(os.path.join(odoo.conf.config['root_path'], 'addons/base/data/res_country_data.xml')).getroot()
    for country in root.find('data').findall('record[@model="res.country"]'):
        name = country.find('field[@name="name"]').text
        code = country.find('field[@name="code"]').text
        list_countries.append([code, name])
    return sorted(list_countries, key=lambda c: c[1])

def exp_server_version():
    """ Return the version of the server
        Used by the client to verify the compatibility with its own version
    """
    return odoo.release.version

#----------------------------------------------------------
# db service dispatch
#----------------------------------------------------------

def dispatch(method, params):
    g = globals()
    exp_method_name = 'exp_' + method
    if method in ['db_exist', 'list', 'list_lang', 'server_version']:
        return g[exp_method_name](*params)
    elif exp_method_name in g:
        passwd = params[0]
        params = params[1:]
        DBUtils.check_super(passwd)
        return g[exp_method_name](*params)
    else:
        raise KeyError("Method not found: %s" % method)

dispatch_service_name = 'db'