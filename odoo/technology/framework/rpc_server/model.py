
import logging
import threading
from functools import partial
from collections.abc import Mapping, Sequence

import odoo
from odoo.exceptions import UserError
from odoo.microkernel.modules.registry import Registry
from ..service import security
from ..service import retrying
from ...utils import lazy
from odoo.microkernel.ormapping import check_method_name

_logger = logging.getLogger(__name__)

def execute_cr(cr, uid, obj, method, *args, **kw):
    # clean cache etc if we retry the same transaction
    cr.reset()
    env = odoo.api.Environment(cr, uid, {})
    recs = env.get(obj)
    if recs is None:
        raise UserError(env._("Object %s doesn't exist", obj))
    result = retrying.retrying(partial(odoo.api.call_kw, recs, method, args, kw), env)
    # force evaluation of lazy values before the cursor is closed, as it would
    # error afterwards if the lazy isn't already evaluated (and cached)
    for l in _traverse_containers(result, lazy):
        _0 = l._value
    return result

def execute_kw(db, uid, obj, method, args, kw=None):
    return execute(db, uid, obj, method, *args, **kw or {})

def execute(db, uid, obj, method, *args, **kw):
    # TODO could be conditionnaly readonly as in _call_kw_readonly
    with Registry(db).cursor() as cr:
        check_method_name(method)
        res = execute_cr(cr, uid, obj, method, *args, **kw)
        if res is None:
            _logger.info('The method %s of the object %s can not return `None`!', method, obj)
        return res

def _traverse_containers(val, type_):
    """ Yields atoms filtered by specified ``type_`` (or type tuple), traverses
    through standard containers (non-string mappings or sequences) *unless*
    they're selected by the type filter
    """
    from odoo.microkernel.ormapping.models import BaseModel
    if isinstance(val, type_):
        yield val
    elif isinstance(val, (str, bytes, BaseModel)):
        return
    elif isinstance(val, Mapping):
        for k, v in val.items():
            yield from _traverse_containers(k, type_)
            yield from _traverse_containers(v, type_)
    elif isinstance(val, Sequence):
        for v in val:
            yield from _traverse_containers(v, type_)

def dispatch(method, params):
    db, uid, passwd = params[0], int(params[1]), params[2]
    security.check(db, uid, passwd, Registry)

    threading.current_thread().dbname = db
    threading.current_thread().uid = uid
    registry = Registry(db).check_signaling()
    with registry.manage_changes():
        if method == 'execute':
            res = retrying.execute(db, uid, *params[3:])
        elif method == 'execute_kw':
            res = retrying.execute_kw(db, uid, *params[3:])
        else:
            raise NameError("Method not available %s" % method)
    return res

dispatch_service_name = 'object'