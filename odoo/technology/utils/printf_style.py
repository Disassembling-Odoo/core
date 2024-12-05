from collections.abc import Mapping

def named_to_positional_printf(string: str, args: Mapping) -> tuple[str, tuple]:
    """ Convert a named printf-style format string with its arguments to an
    equivalent positional format string with its arguments. This implementation
    does not support escaped ``%`` characters (``"%%"``).
    """
    if '%%' in string:
        raise ValueError(f"Unsupported escaped '%' in format string {string!r}")
    pargs = _PrintfArgs(args)
    return string % pargs, tuple(pargs.values)


class _PrintfArgs:
    """ Helper object to turn a named printf-style format string into a positional one. """
    __slots__ = ('mapping', 'values')

    def __init__(self, mapping):
        self.mapping: Mapping = mapping
        self.values: list = []

    def __getitem__(self, key):
        self.values.append(self.mapping[key])
        return "%s"