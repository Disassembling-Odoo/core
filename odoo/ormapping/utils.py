# -*- coding: utf-8 -*-
import re
import sys

from odoo.exceptions import AccessError
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

regex_object_name = re.compile(r'^[a-z0-9_.]+$')

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

def first(records):
    """ Return the first record in ``records``, with the same prefetching. """
    return next(iter(records)) if len(records) > 1 else records

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
    strClz = 'odoo.ormapping.models.MetaModel'
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
    strClz = 'odoo.ormapping.models.BaseModel'
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