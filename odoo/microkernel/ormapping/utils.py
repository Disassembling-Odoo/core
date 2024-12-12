# -*- coding: utf-8 -*-
import re
import sys

from odoo.exceptions import AccessError
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

#######################################################
# chenck if the given name is a valid model name
#######################################################
regex_alphanumeric = re.compile(r'^[a-z0-9_]+$')

def check_property_field_value_name(property_name):
    if not regex_alphanumeric.match(property_name) or len(property_name) > 512:
        raise ValueError(f"Wrong property field value name {property_name!r}.")

# match private methods, to prevent their remote invocation
regex_private = re.compile(r'^(_.*|init)$')

def check_method_name(name):
    """ Raise an ``AccessError`` if ``name`` is a private method name. """
    if regex_private.match(name):
        raise AccessError(_lt('Private methods (such as %s) cannot be called remotely.', name))

regex_object_name = re.compile(r'^[a-z0-9_.]+$')

def check_object_name(name):
    """ Check if the given name is a valid model name.

        The _name attribute in osv and osv_memory object is subject to
        some restrictions. This function returns True or False whether
        the given name is allowed or not.

        TODO: this is an approximation. The goal in this approximation
        is to disallow uppercase characters (in some places, we quote
        table/column names and in other not, which leads to this kind
        of errors:

            psycopg2.ProgrammingError: relation "xxx" does not exist).

        The same restriction should apply to both osv and osv_memory
        objects for consistency.

    """
    if regex_object_name.match(name) is None:
        return False
    return True

def raise_on_invalid_object_name(name):
    if not check_object_name(name):
        msg = "The _name attribute %s is not valid." % name
        raise ValueError(msg)

#######################################################
# company\origin utils
#######################################################
def origin_ids(ids):
    """ Return an iterator over the origin ids corresponding to ``ids``.
        Actual ids are returned as is, and ids without origin are not returned.
    """
    return ((id_ or id_.origin) for id_ in ids if (id_ or getattr(id_, "origin", None)))

def to_company_ids(companies):
    strClz = 'odoo.microkernel.ormapping.models.BaseModel'
    if isinstance(companies, get_definition_class(strClz)):
        return companies.ids
    elif isinstance(companies, (list, tuple, str)):
        return companies
    return [companies]

def check_company_domain_parent_of(self, companies):
    """ A `_check_company_domain` function that lets a record be used if either:
        - record.company_id = False (which implies that it is shared between all companies), or
        - record.company_id is a parent of any of the given companies.
    """
    if isinstance(companies, str):
        return ['|', ('company_id', '=', False), ('company_id', 'parent_of', companies)]

    companies = [id for id in to_company_ids(companies) if id]
    if not companies:
        return [('company_id', '=', False)]

    return [('company_id', 'in', [
        int(parent)
        for rec in self.env['res.company'].sudo().browse(companies)
        for parent in rec.parent_path.split('/')[:-1]
    ] + [False])]

def check_companies_domain_parent_of(self, companies):
    """ A `_check_company_domain` function that lets a record be used if
        any company in record.company_ids is a parent of any of the given companies.
    """
    if isinstance(companies, str):
        return [('company_ids', 'parent_of', companies)]

    companies = [id_ for id_ in to_company_ids(companies) if id_]
    if not companies:
        return []

    return [('company_ids', 'in', [
        int(parent)
        for rec in self.env['res.company'].sudo().browse(companies)
        for parent in rec.parent_path.split('/')[:-1]
    ])]

#######################################################
# Fixes the id fields in import and exports, and splits field paths on '/'.
#######################################################
def fix_import_export_id_paths(fieldname):
    """
    Fixes the id fields in import and exports, and splits field paths
    on '/'.

    :param str fieldname: name of the field to import/export
    :return: split field name
    :rtype: list of str
    """
    fixed_db_id = re.sub(r'([^/])\.id', r'\1/.id', fieldname)
    fixed_external_id = re.sub(r'([^/]):id', r'\1/id', fixed_db_id)
    return fixed_external_id.split('/')

#######################################################
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
#######################################################
def expand_ids(id0, ids):
    """ Return an iterator of unique ids from the concatenation of ``[id0]`` and
        ``ids``, and of the same kind (all real or all new).
    """
    yield id0
    seen = {id0}
    kind = bool(id0)
    for id_ in ids:
        if id_ not in seen and bool(id_) == kind:
            yield id_
            seen.add(id_)

def get_definition_class(strClz):
    list = strClz.rsplit('.', maxsplit=1)
    moduleName = list[0]
    className = list[1]
    if moduleName not in sys.modules:
        module = __import__(moduleName, fromlist=[className])
    else:
        module = sys.modules[moduleName]
    return getattr(module, className)

def is_definition_class(cls):
    """ Return whether ``cls`` is a model definition class. """
    strClz = 'odoo.microkernel.ormapping.models.MetaModel'
    return isinstance(cls, get_definition_class(strClz)) and getattr(cls, 'pool', None) is None

def determine(needle, records, *args):
    """ Simple helper for calling a method given as a string or a function.

    :param needle: callable or name of method to call on ``records``
    :param BaseModel records: recordset to call ``needle`` on or with
    :params args: additional arguments to pass to the determinant
    :returns: the determined value if the determinant is a method name or callable
    :raise TypeError: if ``records`` is not a recordset, or ``needle`` is not
                      a callable or valid method name
    """
    strClz = 'odoo.microkernel.ormapping.models.BaseModel'
    if not isinstance(records, get_definition_class(strClz)):
        raise TypeError("Determination requires a subject recordset")
    if isinstance(needle, str):
        needle = getattr(records, needle)
        if needle.__name__.find('__'):
            return needle(*args)
    elif callable(needle):
        if needle.__name__.find('__'):
            return needle(records, *args)

    raise TypeError("Determination requires a callable or method name")

def is_registry_class(cls):
    """ Return whether ``cls`` is a model registry class. """
    return getattr(cls, 'pool', None) is not None