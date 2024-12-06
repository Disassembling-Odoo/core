import typing
from collections.abc import Iterable, Iterator, Mapping, MutableMapping, MutableSet, Reversible
import hashlib
import hmac as hmac_lib

import datetime
import json
import base64

from .base_type import *


def hmac(env, scope, message, hash_function=hashlib.sha256):
    """Compute HMAC with `database.secret` config parameter as key.

    :param env: sudo environment to use for retrieving config parameter
    :param message: message to authenticate
    :param scope: scope of the authentication, to have different signature for the same
        message in different usage
    :param hash_function: hash function to use for HMAC (default: SHA-256)
    """
    if not scope:
        raise ValueError('Non-empty scope required')

    secret = env['ir.config_parameter'].get_param('database.secret')
    message = repr((scope, message))
    return hmac_lib.new(
        secret.encode(),
        message.encode(),
        hash_function,
    ).hexdigest()

consteq = hmac_lib.compare_digest

def hash_sign(env, scope, message_values, expiration=None, expiration_hours=None):
    """ Generate an urlsafe payload signed with the HMAC signature for an iterable set of data.
    This feature is very similar to JWT, but in a more generic implementation that is inline with out previous hmac implementation.

    :param env: sudo environment to use for retrieving config parameter
    :param scope: scope of the authentication, to have different signature for the same
        message in different usage
    :param message_values: values to be encoded inside the payload
    :param expiration: optional, a datetime or timedelta
    :param expiration_hours: optional, a int representing a number of hours before expiration. Cannot be set at the same time as expiration
    :return: the payload that can be used as a token
    """
    assert not (expiration and expiration_hours)
    assert message_values is not None

    if expiration_hours:
        expiration = datetime.datetime.now() + datetime.timedelta(hours=expiration_hours)
    else:
        if isinstance(expiration, datetime.timedelta):
            expiration = datetime.datetime.now() + expiration
    expiration_timestamp = 0 if not expiration else int(expiration.timestamp())
    message_strings = json.dumps(message_values)
    hash_value = hmac(env, scope, f'1:{message_strings}:{expiration_timestamp}', hash_function=hashlib.sha256)
    token = b"\x01" + expiration_timestamp.to_bytes(8, 'little') + bytes.fromhex(hash_value) + message_strings.encode()
    return base64.urlsafe_b64encode(token).decode().rstrip('=')

def verify_hash_signed(env, scope, payload):
    """ Verify and extract data from a given urlsafe  payload generated with hash_sign()

    :param env: sudo environment to use for retrieving config parameter
    :param scope: scope of the authentication, to have different signature for the same
        message in different usage
    :param payload: the token to verify
    :return: The payload_values if the check was successful, None otherwise.
    """

    token = base64.urlsafe_b64decode(payload.encode()+b'===')
    version = token[:1]
    if version != b'\x01':
        raise ValueError('Unknown token version')

    expiration_value, hash_value, message = token[1:9], token[9:41].hex(), token[41:].decode()
    expiration_value = int.from_bytes(expiration_value, byteorder='little')
    hash_value_expected = hmac(env, scope, f'1:{message}:{expiration_value}', hash_function=hashlib.sha256)

    if consteq(hash_value, hash_value_expected) and (expiration_value == 0 or datetime.datetime.now().timestamp() < expiration_value):
        message_values = json.loads(message)
        return message_values
    return None
