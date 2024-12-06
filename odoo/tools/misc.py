# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""
Miscellaneous tools used by Odoo.
"""
from __future__ import annotations

import collections
import csv

import itertools
import logging
import os
import re
import sys
import traceback
import typing
import unicodedata
import warnings
from collections.abc import Iterable, Iterator, Mapping, MutableMapping, MutableSet, Reversible
from contextlib import ContextDecorator, contextmanager
from difflib import HtmlDiff
from functools import reduce, wraps
from itertools import islice, groupby as itergroupby
from operator import itemgetter

import babel
import babel.dates
import markupsafe
import pytz
from lxml import etree, objectify
from .i18n import get_lang

import odoo
import odoo.addons
# get_encodings, ustr and exception_to_unicode were originally from tools.misc.
# There are moved to loglevels until we refactor tools.
from odoo.loglevels import exception_to_unicode, get_encodings, ustr  # noqa: F401

from ..technology.conf import config
from .float_utils import float_round
from .which import which

K = typing.TypeVar('K')
T = typing.TypeVar('T')
if typing.TYPE_CHECKING:
    from collections.abc import Callable, Collection, Sequence
    from odoo.api import Environment
    from odoo.addons.base.models.res_lang import LangData

    P = typing.TypeVar('P')

__all__ = [
    'SKIPPED_ELEMENT_TYPES',
    'Reverse',
    'clean_context',
    'discardattr',
    'exception_to_unicode',
    'find_in_path',
    'format_amount',
    'get_encodings',
    'get_iso_codes',
    'html_escape',
    'human_size',
    'is_list_of',
    'mod10r',
    'remove_accents',
    'replace_exceptions',
    'split_every',
    'str2bool',
    'street_split',
    'ustr',
]

_logger = logging.getLogger(__name__)

# List of etree._Element subclasses that we choose to ignore when parsing XML.
# We include the *Base ones just in case, currently they seem to be subclasses of the _* ones.
SKIPPED_ELEMENT_TYPES = (etree._Comment, etree._ProcessingInstruction, etree.CommentBase, etree.PIBase, etree._Entity)

# Configure default global parser
etree.set_default_parser(etree.XMLParser(resolve_entities=False))
default_parser = etree.XMLParser(resolve_entities=False, remove_blank_text=True)
default_parser.set_element_class_lookup(objectify.ObjectifyElementClassLookup())
objectify.set_default_parser(default_parser)



#----------------------------------------------------------
# Subprocesses
#----------------------------------------------------------

def find_in_path(name):
    path = os.environ.get('PATH', os.defpath).split(os.pathsep)
    if config.get('bin_path') and config['bin_path'] != 'None':
        path.append(config['bin_path'])
    return which(name, path=os.pathsep.join(path))

try:
    import xlwt

    # add some sanitization to respect the excel sheet name restrictions
    # as the sheet name is often translatable, can not control the input
    class PatchedWorkbook(xlwt.Workbook):
        def add_sheet(self, name, cell_overwrite_ok=False):
            # invalid Excel character: []:*?/\
            name = re.sub(r'[\[\]:*?/\\]', '', name)

            # maximum size is 31 characters
            name = name[:31]
            return super(PatchedWorkbook, self).add_sheet(name, cell_overwrite_ok=cell_overwrite_ok)

    xlwt.Workbook = PatchedWorkbook

except ImportError:
    xlwt = None

try:
    import xlsxwriter

    # add some sanitization to respect the excel sheet name restrictions
    # as the sheet name is often translatable, can not control the input
    class PatchedXlsxWorkbook(xlsxwriter.Workbook):

        # TODO when xlsxwriter bump to 0.9.8, add worksheet_class=None parameter instead of kw
        def add_worksheet(self, name=None, **kw):
            if name:
                # invalid Excel character: []:*?/\
                name = re.sub(r'[\[\]:*?/\\]', '', name)

                # maximum size is 31 characters
                name = name[:31]
            return super(PatchedXlsxWorkbook, self).add_worksheet(name, **kw)

    xlsxwriter.Workbook = PatchedXlsxWorkbook

except ImportError:
    xlsxwriter = None


def get_iso_codes(lang: str) -> str:
    if lang.find('_') != -1:
        if lang.split('_')[0] == lang.split('_')[1].lower():
            lang = lang.split('_')[0]
    return lang


def scan_languages() -> list[tuple[str, str]]:
    """ Returns all languages supported by OpenERP for translation

    :returns: a list of (lang_code, lang_name) pairs
    :rtype: [(str, unicode)]
    """
    try:
        # read (code, name) from languages in base/data/res.lang.csv
        with file_open('base/data/res.lang.csv') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            fields = next(reader)
            code_index = fields.index("code")
            name_index = fields.index("name")
            result = [
                (row[code_index], row[name_index])
                for row in reader
            ]
    except Exception:
        _logger.error("Could not read res.lang.csv")
        result = []

    return sorted(result or [('en_US', u'English')], key=itemgetter(1))


def mod10r(number: str) -> str:
    """
    Input number : account or invoice number
    Output return: the same number completed with the recursive mod10
    key
    """
    codec=[0,9,4,6,8,2,7,1,3,5]
    report = 0
    result=""
    for digit in number:
        result += digit
        if digit.isdigit():
            report = codec[ (int(digit) + report) % 10 ]
    return result + str((10 - report) % 10)


def str2bool(s: str, default: bool | None = None) -> bool:
    # allow this (for now?) because it's used for get_param
    if type(s) is bool:
        return s  # type: ignore

    if not isinstance(s, str):
        warnings.warn(
            f"Passed a non-str to `str2bool`: {s}",
            DeprecationWarning,
            stacklevel=2,
        )

        if default is None:
            raise ValueError('Use 0/1/yes/no/true/false/on/off')
        return bool(default)

    s = s.lower()
    if s in ('y', 'yes', '1', 'true', 't', 'on'):
        return True
    if s in ('n', 'no', '0', 'false', 'f', 'off'):
        return False
    if default is None:
        raise ValueError('Use 0/1/yes/no/true/false/on/off')
    return bool(default)


def human_size(sz: float | str) -> str | typing.Literal[False]:
    """
    Return the size in a human readable format
    """
    if not sz:
        return False
    units = ('bytes', 'Kb', 'Mb', 'Gb', 'Tb')
    if isinstance(sz, str):
        sz=len(sz)
    s, i = float(sz), 0
    while s >= 1024 and i < len(units)-1:
        s /= 1024
        i += 1
    return "%0.2f %s" % (s, units[i])


@typing.overload
def split_every(n: int, iterable: Iterable[T]) -> Iterator[tuple[T, ...]]:
    ...


@typing.overload
def split_every(n: int, iterable: Iterable[T], piece_maker: type[Collection[T]]) -> Iterator[Collection[T]]:
    ...


@typing.overload
def split_every(n: int, iterable: Iterable[T], piece_maker: Callable[[Iterable[T]], P]) -> Iterator[P]:
    ...


def split_every(n: int, iterable: Iterable[T], piece_maker=tuple):
    """Splits an iterable into length-n pieces. The last piece will be shorter
       if ``n`` does not evenly divide the iterable length.

       :param int n: maximum size of each generated chunk
       :param Iterable iterable: iterable to chunk into pieces
       :param piece_maker: callable taking an iterable and collecting each
                           chunk from its slice, *must consume the entire slice*.
    """
    iterator = iter(iterable)
    piece = piece_maker(islice(iterator, n))
    while piece:
        yield piece
        piece = piece_maker(islice(iterator, n))


def discardattr(obj: object, key: str) -> None:
    """ Perform a ``delattr(obj, key)`` but without crashing if ``key`` is not present. """
    try:
        delattr(obj, key)
    except AttributeError:
        pass

# ---------------------------------------------
# String management
# ---------------------------------------------


# Inspired by http://stackoverflow.com/questions/517923
def remove_accents(input_str: str) -> str:
    """Suboptimal-but-better-than-nothing way to replace accented
    latin letters by an ASCII equivalent. Will obviously change the
    meaning of input_str and work only for some cases"""
    if not input_str:
        return input_str
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join(c for c in nkfd_form if not unicodedata.combining(c))


class unquote(str):
    """A subclass of str that implements repr() without enclosing quotation marks
       or escaping, keeping the original string untouched. The name come from Lisp's unquote.
       One of the uses for this is to preserve or insert bare variable names within dicts during eval()
       of a dict's repr(). Use with care.

       Some examples (notice that there are never quotes surrounding
       the ``active_id`` name:

       >>> unquote('active_id')
       active_id
       >>> d = {'test': unquote('active_id')}
       >>> d
       {'test': active_id}
       >>> print d
       {'test': active_id}
    """
    __slots__ = ()

    def __repr__(self):
        return self


def stripped_sys_argv(*strip_args):
    """Return sys.argv with some arguments stripped, suitable for reexecution or subprocesses"""
    strip_args = sorted(set(strip_args) | set(['-s', '--save', '-u', '--update', '-i', '--init', '--i18n-overwrite']))
    assert all(config.parser.has_option(s) for s in strip_args)
    takes_value = dict((s, config.parser.get_option(s).takes_value()) for s in strip_args)

    longs, shorts = list(tuple(y) for _, y in itergroupby(strip_args, lambda x: x.startswith('--')))
    longs_eq = tuple(l + '=' for l in longs if takes_value[l])

    args = sys.argv[:]

    def strip(args, i):
        return args[i].startswith(shorts) \
            or args[i].startswith(longs_eq) or (args[i] in longs) \
            or (i >= 1 and (args[i - 1] in strip_args) and takes_value[args[i - 1]])

    return [x for i, x in enumerate(args) if not strip(args, i)]

def clean_context(context: dict[str, typing.Any]) -> dict[str, typing.Any]:
    """ This function take a dictionary and remove each entry with its key
    starting with ``default_``
    """
    return {k: v for k, v in context.items() if not k.startswith('default_')}


#----------------------------------------------------------
# iterables
#----------------------------------------------------------
class ReversedIterable(Reversible[T], typing.Generic[T]):
    """ An iterable implementing the reversal of another iterable. """
    __slots__ = ['iterable']

    def __init__(self, iterable: Reversible[T]):
        self.iterable = iterable

    def __iter__(self):
        return reversed(self.iterable)

    def __reversed__(self):
        return iter(self.iterable)

class Reverse(object):
    """ Wraps a value and reverses its ordering, useful in key functions when
    mixing ascending and descending sort on non-numeric data as the
    ``reverse`` parameter can not do piecemeal reordering.
    """
    __slots__ = ['val']

    def __init__(self, val):
        self.val = val

    def __eq__(self, other): return self.val == other.val
    def __ne__(self, other): return self.val != other.val

    def __ge__(self, other): return self.val <= other.val
    def __gt__(self, other): return self.val < other.val
    def __le__(self, other): return self.val >= other.val
    def __lt__(self, other): return self.val > other.val

class replace_exceptions(ContextDecorator):
    """
    Hide some exceptions behind another error. Can be used as a function
    decorator or as a context manager.

    .. code-block:

        @route('/super/secret/route', auth='public')
        @replace_exceptions(AccessError, by=NotFound())
        def super_secret_route(self):
            if not request.session.uid:
                raise AccessError("Route hidden to non logged-in users")
            ...

        def some_util():
            ...
            with replace_exceptions(ValueError, by=UserError("Invalid argument")):
                ...
            ...

    :param exceptions: the exception classes to catch and replace.
    :param by: the exception to raise instead.
    """
    def __init__(self, *exceptions, by):
        if not exceptions:
            raise ValueError("Missing exceptions")

        wrong_exc = next((exc for exc in exceptions if not issubclass(exc, Exception)), None)
        if wrong_exc:
            raise TypeError(f"{wrong_exc} is not an exception class.")

        self.exceptions = exceptions
        self.by = by

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None and issubclass(exc_type, self.exceptions):
            if isinstance(self.by, type) and exc_value.args:
                # copy the message
                raise self.by(exc_value.args[0]) from exc_value
            else:
                raise self.by from exc_value


html_escape = markupsafe.escape


def format_decimalized_number(number: float, decimal: int = 1) -> str:
    """Format a number to display to nearest metrics unit next to it.

    Do not display digits if all visible digits are null.
    Do not display units higher then "Tera" because most people don't know what
    a "Yotta" is.

    ::

        >>> format_decimalized_number(123_456.789)
        123.5k
        >>> format_decimalized_number(123_000.789)
        123k
        >>> format_decimalized_number(-123_456.789)
        -123.5k
        >>> format_decimalized_number(0.789)
        0.8
    """
    for unit in ['', 'k', 'M', 'G']:
        if abs(number) < 1000.0:
            return "%g%s" % (round(number, decimal), unit)
        number /= 1000.0
    return "%g%s" % (round(number, decimal), 'T')


def format_decimalized_amount(amount: float, currency=None) -> str:
    """Format an amount to display the currency and also display the metric unit
    of the amount.

    ::

        >>> format_decimalized_amount(123_456.789, env.ref("base.USD"))
        $123.5k
    """
    formated_amount = format_decimalized_number(amount)

    if not currency:
        return formated_amount

    if currency.position == 'before':
        return "%s%s" % (currency.symbol or '', formated_amount)

    return "%s %s" % (formated_amount, currency.symbol or '')


def format_amount(env: Environment, amount: float, currency, lang_code: str | None = None) -> str:
    fmt = "%.{0}f".format(currency.decimal_places)
    lang = env['res.lang'].browse(get_lang(env, lang_code).id)

    formatted_amount = lang.format(fmt, currency.round(amount), grouping=True)\
        .replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')

    pre = post = u''
    if currency.position == 'before':
        pre = u'{symbol}\N{NO-BREAK SPACE}'.format(symbol=currency.symbol or '')
    else:
        post = u'\N{NO-BREAK SPACE}{symbol}'.format(symbol=currency.symbol or '')

    return u'{pre}{0}{post}'.format(formatted_amount, pre=pre, post=post)


def get_diff(data_from, data_to, custom_style=False, dark_color_scheme=False):
    """
    Return, in an HTML table, the diff between two texts.

    :param tuple data_from: tuple(text, name), name will be used as table header
    :param tuple data_to: tuple(text, name), name will be used as table header
    :param tuple custom_style: string, style css including <style> tag.
    :param bool dark_color_scheme: true if dark color scheme is used
    :return: a string containing the diff in an HTML table format.
    """
    def handle_style(html_diff, custom_style, dark_color_scheme):
        """ The HtmlDiff lib will add some useful classes on the DOM to
        identify elements. Simply append to those classes some BS4 ones.
        For the table to fit the modal width, some custom style is needed.
        """
        to_append = {
            'diff_header': 'bg-600 text-center align-top px-2',
            'diff_next': 'd-none',
        }
        for old, new in to_append.items():
            html_diff = html_diff.replace(old, "%s %s" % (old, new))
        html_diff = html_diff.replace('nowrap', '')
        colors = ('#7f2d2f', '#406a2d', '#51232f', '#3f483b') if dark_color_scheme else (
            '#ffc1c0', '#abf2bc', '#ffebe9', '#e6ffec')
        html_diff += custom_style or '''
            <style>
                .modal-dialog.modal-lg:has(table.diff) {
                    max-width: 1600px;
                    padding-left: 1.75rem;
                    padding-right: 1.75rem;
                }
                table.diff { width: 100%%; }
                table.diff th.diff_header { width: 50%%; }
                table.diff td.diff_header { white-space: nowrap; }
                table.diff td { word-break: break-all; vertical-align: top; }
                table.diff .diff_chg, table.diff .diff_sub, table.diff .diff_add {
                    display: inline-block;
                    color: inherit;
                }
                table.diff .diff_sub, table.diff td:nth-child(3) > .diff_chg { background-color: %s }
                table.diff .diff_add, table.diff td:nth-child(6) > .diff_chg { background-color: %s }
                table.diff td:nth-child(3):has(>.diff_chg, .diff_sub) { background-color: %s }
                table.diff td:nth-child(6):has(>.diff_chg, .diff_add) { background-color: %s }
            </style>
        ''' % colors
        return html_diff

    diff = HtmlDiff(tabsize=2).make_table(
        data_from[0].splitlines(),
        data_to[0].splitlines(),
        data_from[1],
        data_to[1],
        context=True,  # Show only diff lines, not all the code
        numlines=3,
    )
    return handle_style(diff, custom_style, dark_color_scheme)

ADDRESS_REGEX = re.compile(r'^(.*?)(\s[0-9][0-9\S]*)?(?: - (.+))?$', flags=re.DOTALL)
def street_split(street):
    match = ADDRESS_REGEX.match(street or '')
    results = match.groups('') if match else ('', '', '')
    return {
        'street_name': results[0].strip(),
        'street_number': results[1].strip(),
        'street_number2': results[2],
    }


def is_list_of(values, type_: type) -> bool:
    """Return True if the given values is a list / tuple of the given type.

    :param values: The values to check
    :param type_: The type of the elements in the list / tuple
    """
    return isinstance(values, (list, tuple)) and all(isinstance(item, type_) for item in values)


def has_list_types(values, types: tuple[type, ...]) -> bool:
    """Return True if the given values have the same types as
    the one given in argument, in the same order.

    :param values: The values to check
    :param types: The types of the elements in the list / tuple
    """
    return (
        isinstance(values, (list, tuple)) and len(values) == len(types)
        and all(itertools.starmap(isinstance, zip(values, types)))
    )


def get_flag(country_code: str) -> str:
    """Get the emoji representing the flag linked to the country code.

    This emoji is composed of the two regional indicator emoji of the country code.
    """
    return "".join(chr(int(f"1f1{ord(c)+165:02x}", base=16)) for c in country_code)
