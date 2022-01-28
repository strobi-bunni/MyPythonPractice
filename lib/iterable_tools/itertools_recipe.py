"""
ORIGINAL CODE FROM: Python Documentation
https://docs.python.org/3/library/itertools.html#itertools-recipes

Added some docstrings and type annotation.
"""
import collections
import itertools
import operator
import random
from collections.abc import Callable, Iterable, Iterator
from numbers import Number
from typing import Any, Optional, TypeVar, Union

T = TypeVar('T')
T_Other = TypeVar('T_Other')  # 대체 T


def all_equal(iterable: Iterable[T]) -> bool:
    """``iterable``의 모든 값들이 같은지의 여부를 반환한다.

    Parameters
    ----------
    iterable : Iterable object, yields any type ``T``
        반복 가능한 객체

    Returns
    -------
    are_all_equals : bool
        모든 값들이 같은지의 여부

    Examples
    --------
    >>> all_equal([1, 1, 1])
    True
    >>> all_equal([1, 2, 3])
    False
    """
    g = itertools.groupby(iterable)
    return next(g, True) and not next(g, False)


def consume(iterator: Iterator[T], n: Optional[int] = None) -> None:
    """이터레이터 ``iterator``의 처음 ``n``개를 건너뛴다.

    만약 ``n``이 생략된다면 이터레이터 전체 항목을 건너뛴다.

    Parameters
    ----------
    iterator : Iterator, yields any type ``T``
        이터레이터
    n : int, optional
        생략할 갯수. 만약 생략한다면 ``iterator`` 전체를 생략한다.

    Examples
    --------
    >>> ri = iter(range(10))
    >>> consume(ri, 3)
    >>> next(ri)
    3
    >>> next(ri)
    4
    >>> next(ri)
    5
    """
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(itertools.islice(iterator, n, n), None)


def dotproduct(vec1: Iterable[Number], vec2: Iterable[Number]) -> Number:
    """두 벡터의 내적을 구한다.

    내적은 두 벡터의 대응하는 값들을 곱해서 그 곱들을 합해서 구한다.

    Parameters
    ----------
    vec1 : Iterable of numbers
        첫 번째 벡터
    vec2 : Iterable of numbers
        두 번째 벡터

    Returns
    -------
    d : number
        두 벡터의 내적

    Notes
    -----
    만약 두 벡터의 길이가 다를 경우 짧은 쪽에 맞춰진다.

    Examples
    >>> dotproduct([1, 3, 5], [2, 4, 6])   # (1 * 2) + (3 * 4) + (5 * 6)
    44
    """
    return sum(map(operator.mul, vec1, vec2))


def first_true(iterable: Iterable[T], default=False, pred: Callable[[T], bool] = None):
    """``iterable``에서 처음으로 참인 값을 반환한다.

    만약 참인 값이 없다면 ``default``를 반환한다.

    만약 ``pred``가 None이 아닐 경우 처음으로 ``pred(item)``이 참인 값 ``item``을 반환한다.

    Notes
    -----
    이는 Short-circuit logic과 유사하다.

        first_true([a, b, c], x)   --> a or b or c or x
        first_true([a, b], x, f)   --> a if f(a) else b if f(b) else x
    """
    return next(filter(pred, iterable), default)


def flatten(list_of_lists: Iterable[Iterable[T]]) -> Iterator[T]:
    """중첩된 이터러블의 한 레벨을 합친다.

    Parameters
    ----------
    list_of_lists : Iterable of iterables
        반복 가능한 객체의 묶음

    Yields
    ------
    chains : itertools.chain
        반복 가능한 객체

    Examples
    --------
    >>> flatten([[1, 2, 3], [4, 5], [6, 7, 8]])
    [1, 2, 3, 4, 5, 6, 7, 8]
    """
    return itertools.chain.from_iterable(list_of_lists)


def grouper(iterable: Iterable[T], n: int, fillvalue: T_Other = None) -> Iterable[Iterable[Union[T, T_Other]]]:
    """이터러블을 고정된 길이의 묶음으로 나눈다. 이 때 길이가 맞지 않을 경우 fillvalue로 채운다.

    Parameters
    ----------
    iterable : Iterable object
        반복 가능한 객체
    n : int
        묶음의 길이
    fillvalue : Any type, optional
        길이가 맞지 않을 경우 채울 값, 기본값은 None이다

    Yields
    ------
    chunk : zip_longest
        반복 가능한 객체

    Examples
    --------
    >>> ' '.join(''.join(chunk) for chunk in grouper('ABCDEFG', 3, 'x'))
    'ABC DEF Gxx'
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def iter_except(func: Callable[[], T], exception: Exception, first=None) -> Iterator[T]:
    """ Call a function repeatedly until an exception is raised.

    Converts a call-until-exception interface to an iterator interface.
    Like builtins.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.

    Examples:
        iter_except(functools.partial(heappop, h), IndexError)   # priority queue iterator
        iter_except(d.popitem, KeyError)                         # non-blocking dict iterator
        iter_except(d.popleft, IndexError)                       # non-blocking deque iterator
        iter_except(q.get_nowait, Queue.Empty)                   # loop over a producer Queue
        iter_except(s.pop, KeyError)                             # non-blocking set iterator

    """
    try:
        if first is not None:
            yield first()  # For database APIs needing an initial cast to db.first()
        while True:
            yield func()
    except exception:
        pass


def ncycles(iterable: Iterable[T], n: int) -> Iterator[T]:
    """Returns the sequence elements n times"""
    return itertools.chain.from_iterable(itertools.repeat(tuple(iterable), n))


def nth(iterable: Iterable[T], n: int, default: T_Other = None) -> Union[T, T_Other]:
    """Returns the nth item or a default value"""
    return next(itertools.islice(iterable, n, None), default)


def padnone(iterable: Iterable[T]) -> Iterator[Union[T, None]]:
    """Returns the sequence elements and then returns None indefinitely.

    Useful for emulating the behavior of the built-in map() function.
    """
    return itertools.chain(iterable, itertools.repeat(None))


def pairwise(iterable: Iterable[T]) -> Iterator[tuple[T, T]]:
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def partition(pred: Callable[[T], Any], iterable: Iterable[T]) -> tuple[Iterator[T], Iterator[T]]:
    """Use a predicate to partition entries into false entries and true entries"""
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = itertools.tee(iterable)
    return itertools.filterfalse(pred, t1), filter(pred, t2)


def powerset(iterable: Iterable[T]) -> Iterator[Iterator[T]]:
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))


def quantify(iterable: Iterable[T], pred: Callable[[T], bool] = bool) -> int:
    """Count how many times the predicate is true"""
    return sum(map(pred, iterable))


def random_combination(iterable: Iterable[T], r: int, rand: random.Random = None) -> tuple[T, ...]:
    """Random selection from itertools.combinations(iterable, r)"""
    if rand is None:
        rand = random.Random()
    pool: tuple[T, ...] = tuple(iterable)
    n = len(pool)
    indices: list[int] = sorted(rand.sample(range(n), r))
    return tuple(pool[i] for i in indices)


def random_combination_with_replacement(iterable: Iterable[T], r: int, rand: random.Random = None) -> tuple[T, ...]:
    """Random selection from itertools.combinations_with_replacement(iterable, r)"""
    pool: tuple[T, ...] = tuple(iterable)
    n = len(pool)
    indices: list[int] = sorted(rand.randrange(n) for _ in range(r))
    return tuple(pool[i] for i in indices)


def random_permutation(iterable: Iterable[T], r=None, rand: random.Random = None) -> tuple[T, ...]:
    """Random selection from itertools.permutations(iterable, r)"""
    if rand is None:
        rand = random.Random()
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(rand.sample(pool, r))


def random_product(*args: Iterable[T], repeat: int = 1, rand: random.Random = None) -> tuple[T, ...]:
    """Random selection from itertools.product(*args, **kwds)"""
    if rand is None:
        rand = random.Random()
    pools = [tuple(pool) for pool in args] * repeat
    return tuple(rand.choice(pool) for pool in pools)


def repeatfunc(func: Callable[[Any], T], times: int = None, *args) -> Iterator[T]:
    """Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)
    """
    if times is None:
        return itertools.starmap(func, itertools.repeat(args))
    return itertools.starmap(func, itertools.repeat(args, times))


def roundrobin(*iterables: Iterable[T]) -> Iterable[T]:
    """roundrobin('ABC', 'D', 'EF') --> A D E B F C"""
    # Recipe credited to George Sakkis
    num_active = len(iterables)
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next_item in nexts:
                yield next_item()
        except StopIteration:
            # Remove the iterator we just exhausted from the cycle.
            num_active -= 1
            nexts = itertools.cycle(itertools.islice(nexts, num_active))


def tabulate(func: Callable[[int], T], start: int = 0) -> Iterator[T]:
    """Return func(0), func(1), ..."""
    return map(func, itertools.count(start))


def tail(n: int, iterable: Iterable[T]) -> Iterator[T]:
    """Return an iterator over the last n items
    tail(3, 'ABCDEFG') --> E F G
    """
    return iter(collections.deque(iterable, maxlen=n))


def take(n: int, iterable: Iterable[T]) -> list[T]:
    """Return first n items of the iterable as a list"""
    return list(itertools.islice(iterable, n))


def unique_everseen(iterable: Iterable[T], key: Callable[[T], Any] = None) -> Iterator[T]:
    """List unique elements, preserving order. Remember all elements ever seen.
    unique_everseen('AAAABBBCCDAABBB') --> A B C D
    unique_everseen('ABBCcAD', str.lower) --> A B C D
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def unique_justseen(iterable: Iterable[T], key: Callable[[T], Any] = None) -> Iterator[T]:
    """List unique elements, preserving order. Remember only the element just seen.
    unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    unique_justseen('ABBCcAD', str.lower) --> A B C A D
    """
    return map(next, map(operator.itemgetter(1), itertools.groupby(iterable, key)))
