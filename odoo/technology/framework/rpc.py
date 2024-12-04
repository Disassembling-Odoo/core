# -*- coding: utf-8 -*-
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

rpc_dispatchers = {
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
    with borrow_request():
        threading.current_thread().uid = None
        threading.current_thread().dbname = None

        dispatch = rpc_dispatchers[service_name]
        return dispatch(method, params)
    
def _load_rpc_server():
    import inspect
    from . import rpc_server as RPCService
    for pInspect in inspect.getmembers(RPCService):
        p = pInspect[1]
        if inspect.ismodule(p):
            rpc_dispatchers[p.dispatch_service_name] = p.dispatch

_load_rpc_server()