# -*- coding: utf-8 -*-
import pkgutil
import os.path
__path__ = [
    os.path.abspath(path)
    for path in pkgutil.extend_path(__path__, __name__)
]

import contextlib
import threading

import werkzeug.local

_request_stack = werkzeug.local.LocalStack()

@contextlib.contextmanager
def borrow_request():
    """ Get the current request and unexpose it from the local stack. """
    req = _request_stack.pop()
    try:
        yield req
    finally:
        _request_stack.push(req)


#dispatch
#dispatch_service_name

rpc_dispatchers = {
    'common': '',
    'db': '',
    'object': '',
}

def dispatch_rpc(service_name, method, params):
    """
    Perform a RPC call.

    :param str service_name: either "common", "db" or "object".
    :param str method: the method name of the given service to execute
    :param Mapping params: the keyword arguments for method call
    :return: the return value of the called method
    :rtype: Any
    """
    from .rpc.common import dispatch as serviceDispatch
    from .rpc.db import dispatch as dbDispatch
    from .service.retrying import dispatch as objectDispatch
    rpc_dispatchers = {
        'common': serviceDispatch,
        'db': dbDispatch,
        'object': objectDispatch,
    }

    with borrow_request():
        threading.current_thread().uid = None
        threading.current_thread().dbname = None

        dispatch = rpc_dispatchers[service_name]
        return dispatch(method, params)