import warnings

import typing
import collections
from collections import defaultdict
from collections.abc import (
    Iterable, Iterator, Mapping, MutableMapping, MutableSet, Reversible,
)
from odoo.tools.i18n import Sentinel, SENTINEL

K = typing.TypeVar('K')
T = typing.TypeVar('T')

from collections.abc import Callable, Collection, Sequence

#----------------------------------------------------------
# iterables
#----------------------------------------------------------
def flatten(list):
    """Flatten a list of elements into a unique list
    Author: Christophe Simonis (christophe@tinyerp.com)

    Examples::
    >>> flatten(['a'])
    ['a']
    >>> flatten('b')
    ['b']
    >>> flatten( [] )
    []
    >>> flatten( [[], [[]]] )
    []
    >>> flatten( [[['a','b'], 'c'], 'd', ['e', [], 'f']] )
    ['a', 'b', 'c', 'd', 'e', 'f']
    >>> t = (1,2,(3,), [4, 5, [6, [7], (8, 9), ([10, 11, (12, 13)]), [14, [], (15,)], []]])
    >>> flatten(t)
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    """
    warnings.warn(
        "deprecated since 18.0",
        category=DeprecationWarning,
        stacklevel=2,
    )
    r = []
    for e in list:
        if isinstance(e, (bytes, str)) or not isinstance(e, collections.abc.Iterable):
            r.append(e)
        else:
            r.extend(flatten(e))
    return r


def reverse_enumerate(lst: Sequence[T]) -> Iterator[tuple[int, T]]:
    """Like enumerate but in the other direction

    Usage::

        >>> a = ['a', 'b', 'c']
        >>> it = reverse_enumerate(a)
        >>> it.next()
        (2, 'c')
        >>> it.next()
        (1, 'b')
        >>> it.next()
        (0, 'a')
        >>> it.next()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        StopIteration
    """
    return zip(range(len(lst) - 1, -1, -1), reversed(lst))


def partition(pred: Callable[[T], bool], elems: Iterable[T]) -> tuple[list[T], list[T]]:
    """ Return a pair equivalent to:
    ``filter(pred, elems), filter(lambda x: not pred(x), elems)`` """
    yes: list[T] = []
    nos: list[T] = []
    for elem in elems:
        (yes if pred(elem) else nos).append(elem)
    return yes, nos


def topological_sort(elems: Mapping[T, Collection[T]]) -> list[T]:
    """ Return a list of elements sorted so that their dependencies are listed
    before them in the result.

    :param elems: specifies the elements to sort with their dependencies; it is
        a dictionary like `{element: dependencies}` where `dependencies` is a
        collection of elements that must appear before `element`. The elements
        of `dependencies` are not required to appear in `elems`; they will
        simply not appear in the result.

    :returns: a list with the keys of `elems` sorted according to their
        specification.
    """
    # the algorithm is inspired by [Tarjan 1976],
    # http://en.wikipedia.org/wiki/Topological_sorting#Algorithms
    result = []
    visited = set()

    def visit(n):
        if n not in visited:
            visited.add(n)
            if n in elems:
                # first visit all dependencies of n, then append n to result
                for it in elems[n]:
                    visit(it)
                result.append(n)

    for el in elems:
        visit(el)

    return result


def merge_sequences(*iterables: Iterable[T]) -> list[T]:
    """ Merge several iterables into a list. The result is the union of the
        iterables, ordered following the partial order given by the iterables,
        with a bias towards the end for the last iterable::

            seq = merge_sequences(['A', 'B', 'C'])
            assert seq == ['A', 'B', 'C']

            seq = merge_sequences(
                ['A', 'B', 'C'],
                ['Z'],                  # 'Z' can be anywhere
                ['Y', 'C'],             # 'Y' must precede 'C';
                ['A', 'X', 'Y'],        # 'X' must follow 'A' and precede 'Y'
            )
            assert seq == ['A', 'B', 'X', 'Y', 'C', 'Z']
    """
    # dict is ordered
    deps: defaultdict[T, list[T]] = defaultdict(list)  # {item: elems_before_item}
    for iterable in iterables:
        prev: T | Sentinel = SENTINEL
        for item in iterable:
            if prev is SENTINEL:
                deps[item]  # just set the default
            else:
                deps[item].append(prev)
            prev = item
    return topological_sort(deps)

def groupby(iterable: Iterable[T], key: Callable[[T], K] = lambda arg: arg) -> Iterable[tuple[K, list[T]]]:
    """ Return a collection of pairs ``(key, elements)`` from ``iterable``. The
        ``key`` is a function computing a key value for each element. This
        function is similar to ``itertools.groupby``, but aggregates all
        elements under the same key, not only consecutive elements.
    """
    groups = defaultdict(list)
    for elem in iterable:
        groups[key(elem)].append(elem)
    return groups.items()

def unique(it: Iterable[T]) -> Iterator[T]:
    """ "Uniquifier" for the provided iterable: will output each element of
    the iterable once.

    The iterable's elements must be hashahble.

    :param Iterable it:
    :rtype: Iterator
    """
    seen = set()
    for e in it:
        if e not in seen:
            seen.add(e)
            yield e


def submap(mapping: Mapping[K, T], keys: Iterable[K]) -> Mapping[K, T]:
    """
    Get a filtered copy of the mapping where only some keys are present.

    :param Mapping mapping: the original dict-like structure to filter
    :param Iterable keys: the list of keys to keep
    :return dict: a filtered dict copy of the original mapping
    """
    keys = frozenset(keys)
    return {key: mapping[key] for key in mapping if key in keys}

