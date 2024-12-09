from __future__ import annotations

import warnings
import re
import typing
from typing import TYPE_CHECKING, Literal, Optional, Sequence

import babel
import babel.dates
from babel import lists
import enum

from .float_utils import float_round

if TYPE_CHECKING:
    import odoo.microkernel.api.api
    from collections.abc import Callable, Collection, Sequence
    from odoo.addons.base.models.res_lang import LangData

class Sentinel(enum.Enum):
    """Class for typing parameters with a sentinel as a default"""
    SENTINEL = -1

SENTINEL = Sentinel.SENTINEL

NON_BREAKING_SPACE = u'\N{NO-BREAK SPACE}'

XPG_LOCALE_RE = re.compile(
    r"""^
    ([a-z]+)      # language
    (_[A-Z\d]+)?  # maybe _territory
    # no support for .codeset (we don't use that in Odoo)
    (@.+)?        # maybe @modifier
    $""",
    re.VERBOSE,
)

def formatLang(
    env: odoo.api.Environment,
    value: float | typing.Literal[''],
    digits: int = 2,
    grouping: bool = True,
    monetary: bool | Sentinel = SENTINEL,
    dp: str | None = None,
    currency_obj=None,
    rounding_method: typing.Literal['HALF-UP', 'HALF-DOWN', 'HALF-EVEN', "UP", "DOWN"] = 'HALF-EVEN',
    rounding_unit: typing.Literal['decimals', 'units', 'thousands', 'lakhs', 'millions'] = 'decimals',
) -> str:
    """
    This function will format a number `value` to the appropriate format of the language used.

    :param Object env: The environment.
    :param float value: The value to be formatted.
    :param int digits: The number of decimals digits.
    :param bool grouping: Usage of language grouping or not.
    :param bool monetary: Usage of thousands separator or not.
        .. deprecated:: 13.0
    :param str dp: Name of the decimals precision to be used. This will override ``digits``
                   and ``currency_obj`` precision.
    :param Object currency_obj: Currency to be used. This will override ``digits`` precision.
    :param str rounding_method: The rounding method to be used:
        **'HALF-UP'** will round to the closest number with ties going away from zero,
        **'HALF-DOWN'** will round to the closest number with ties going towards zero,
        **'HALF_EVEN'** will round to the closest number with ties going to the closest
        even number,
        **'UP'** will always round away from 0,
        **'DOWN'** will always round towards 0.
    :param str rounding_unit: The rounding unit to be used:
        **decimals** will round to decimals with ``digits`` or ``dp`` precision,
        **units** will round to units without any decimals,
        **thousands** will round to thousands without any decimals,
        **lakhs** will round to lakhs without any decimals,
        **millions** will round to millions without any decimals.

    :returns: The value formatted.
    :rtype: str
    """
    if monetary is not SENTINEL:
        warnings.warn("monetary argument deprecated since 13.0", DeprecationWarning, 2)
    # We don't want to return 0
    if value == '':
        return ''

    if rounding_unit == 'decimals':
        if dp:
            digits = env['decimal.precision'].precision_get(dp)
        elif currency_obj:
            digits = currency_obj.decimal_places
    else:
        digits = 0

    rounding_unit_mapping = {
        'decimals': 1,
        'thousands': 10**3,
        'lakhs': 10**5,
        'millions': 10**6,
        'units': 1,
    }

    value /= rounding_unit_mapping[rounding_unit]

    rounded_value = float_round(value, precision_digits=digits, rounding_method=rounding_method)
    lang = env['res.lang'].browse(get_lang(env).id)
    formatted_value = lang.format(f'%.{digits}f', rounded_value, grouping=grouping)

    if currency_obj and currency_obj.symbol:
        arguments = (formatted_value, NON_BREAKING_SPACE, currency_obj.symbol)

        return '%s%s%s' % (arguments if currency_obj.position == 'after' else arguments[::-1])

    return formatted_value

def get_lang(env: odoo.api.Environment, lang_code: str | None = None) -> LangData:
    """
    Retrieve the first lang object installed, by checking the parameter lang_code,
    the context and then the company. If no lang is installed from those variables,
    fallback on english or on the first lang installed in the system.

    :param env:
    :param str lang_code: the locale (i.e. en_US)
    :return LangData: the first lang found that is installed on the system.
    """
    langs = [code for code, _ in env['res.lang'].get_installed()]
    lang = 'en_US' if 'en_US' in langs else langs[0]
    if lang_code and lang_code in langs:
        lang = lang_code
    elif (context_lang := env.context.get('lang')) in langs:
        lang = context_lang
    elif (company_lang := env.user.with_context(lang='en_US').company_id.partner_id.lang) in langs:
        lang = company_lang
    return env['res.lang']._get_data(code=lang)

def get_iso_codes(lang: str) -> str:
    if lang.find('_') != -1:
        if lang.split('_')[0] == lang.split('_')[1].lower():
            lang = lang.split('_')[0]
    return lang

def babel_locale_parse(lang_code: str | None) -> babel.Locale:
    if lang_code:
        try:
            return babel.Locale.parse(lang_code)
        except Exception:  # noqa: BLE001
            pass
    try:
        return babel.Locale.default()
    except Exception:  # noqa: BLE001
        return babel.Locale.parse("en_US")


def format_list(
    env: odoo.api.Environment,
    lst: Sequence[str],
    style: Literal["standard", "standard-short", "or", "or-short", "unit", "unit-short", "unit-narrow"] = "standard",
    lang_code: Optional[str] = None,
) -> str:
    """
    Format the items in `lst` as a list in a locale-dependent manner with the chosen style.

    The available styles are defined by babel according to the Unicode TR35-49 spec:
    * standard:
      A typical 'and' list for arbitrary placeholders.
      e.g. "January, February, and March"
    * standard-short:
      A short version of an 'and' list, suitable for use with short or abbreviated placeholder values.
      e.g. "Jan., Feb., and Mar."
    * or:
      A typical 'or' list for arbitrary placeholders.
      e.g. "January, February, or March"
    * or-short:
      A short version of an 'or' list.
      e.g. "Jan., Feb., or Mar."
    * unit:
      A list suitable for wide units.
      e.g. "3 feet, 7 inches"
    * unit-short:
      A list suitable for short units
      e.g. "3 ft, 7 in"
    * unit-narrow:
      A list suitable for narrow units, where space on the screen is very limited.
      e.g. "3′ 7″"

    See https://www.unicode.org/reports/tr35/tr35-49/tr35-general.html#ListPatterns for more details.

    :param env: the current environment.
    :param lst: the sequence of items to format into a list.
    :param style: the style to format the list with.
    :param lang_code: the locale (i.e. en_US).
    :return: the formatted list.
    """
    locale = babel_locale_parse(lang_code or get_lang(env).code)
    # Some styles could be unavailable for the chosen locale
    if style not in locale.list_patterns:
        style = "standard"
    return lists.format_list(lst, style, locale)


def py_to_js_locale(locale: str) -> str:
    """
    Converts a locale from Python to JavaScript format.

    Most of the time the conversion is simply to replace _ with -.
    Example: fr_BE → fr-BE

    Exception: Serbian can be written in both Latin and Cyrillic scripts
    interchangeably, therefore its locale includes a special modifier
    to indicate which script to use.
    Example: sr@latin → sr-Latn

    BCP 47 (JS):
        language[-extlang][-script][-region][-variant][-extension][-privateuse]
        https://www.ietf.org/rfc/rfc5646.txt
    XPG syntax (Python):
        language[_territory][.codeset][@modifier]
        https://www.gnu.org/software/libc/manual/html_node/Locale-Names.html

    :param locale: The locale formatted for use on the Python-side.
    :return: The locale formatted for use on the JavaScript-side.
    """
    match_ = XPG_LOCALE_RE.match(locale)
    if not match_:
        return locale
    language, territory, modifier = match_.groups()
    subtags = [language]
    if modifier == "@Cyrl":
        subtags.append("Cyrl")
    elif modifier == "@latin":
        subtags.append("Latn")
    if territory:
        subtags.append(territory.removeprefix("_"))
    return "-".join(subtags)
