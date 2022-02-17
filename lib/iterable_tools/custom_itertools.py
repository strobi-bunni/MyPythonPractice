import itertools
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Any, Literal, TypeVar, Union

from .itertools_recipe import all_equal, consume, partition
from ..func_tools import deprecated, identity, invert_bool

T = TypeVar('T')
V = TypeVar('V')


def slice_items(iterable: Iterable[T], n: int) -> Iterator[Iterator[T]]:
    r"""``iterable``\의 각 값들을 ``n``\개씩 분할한다.

    Parameters
    ----------
    iterable : Iterable object, yields any type ``T``
        반복 가능한 객체
    n : int, must be positive value.
        ``iterable``\을 일정한 크기로 나눌 최대 크기

    Yields
    ------
    chunk : Iterator, yields any type ``T``
        반복 가능한 객체

    Exceptions
    ----------
    ValueError
        ``n <= 0``\일 경우

    Examples
    --------
    >>> list(map(tuple, slice_items(range(10), 4)))
    [(0, 1, 2, 3), (4, 5, 6, 7), (8, 9)]
    """
    if n <= 0:
        raise ValueError('n must be positive value')
    for _, group in itertools.groupby(enumerate(iterable), key=lambda x: x[0] // n):
        yield (x[1] for x in group)


def dowhile(pred: Callable[[T], bool], iterable: Iterable[T]) -> Iterator[T]:
    r"""``iterable``의 각각의 항목들을 산출한 뒤 ``pred``를 평가하여 False이면 산출을 중단한다.

    이는 산출 전 평가를 하는 ``filter``나 ``itertools.takewhile``과 다르다.

    Parameters
    ----------
    pred : Function-like, returns bool
        ``iterable``의 각각의 항목을 평가할 함수
    iterable : Iterable object, yields any type ``T``
        반복 가능한 객체

    Yields
    ------
    item : Any type ``T``
        ``pred``가 처음으로 False을 반환하는 값까지 반환된다.

    Notes
    -----
    이름은 C 언어에서의 ``do { ... } while (...);``구문에서 따왔다.

    Examples
    --------
    >>> from itertools import takewhile
    >>> list(takewhile(lambda x: x < 5, [1, 4, 6, 4, 1]))
    [1, 4]
    >>> list(dowhile(lambda x: x < 5, [1, 4, 6, 4, 1]))
    [1, 4, 6]
    """
    for item in iterable:
        yield item
        if not pred(item):
            break


def common_starts(*iterables: Iterable[T]) -> Iterator[T]:
    r"""여러 개의 반복 가능한 부분에서 공통된 시작 부분을 찾는다.

    Parameters
    ----------
    iterables : Multiple iterable object, yields any type ``T``
        추가로 입력할 수 있는 여러 개의 반복 가능한 객체

    Yields
    ------
    item : Any type ``T``
        공통된 시작 값

    Notes
    -----
    만약 ``iterables``이 하나일 경우 그 반복 가능한 객체의 모든 값을 산출한다.

    Examples
    --------
    >>> from itertools import count
    >>> list(common_starts(count(), range(5), [0, 1, 2, 3, 6, 12]))
    [0, 1, 2, 3]
    """
    if not iterables:
        raise ValueError('At least one iterable should given.')
    return (x[0] for x in itertools.takewhile(all_equal, zip(*iterables)))


def multi_sorted(iterable: Iterable[T], *criteria: tuple[Callable[[T], Any], bool]) -> list[T]:
    r"""리스트를 여러 기준에 맞춰서 정렬한다.

    기준 ``criterias``\은 튜플 (key, reverse)의 리스트로 표현한다.
    이 key, reverse는 ``__builtins__.sorted``\의 key, reverse 키워드 인자와 기능이 같다.

    기준 ``criteria``\는 앞의 기준이 우선적으로 적용된다.
    예를 들어 ``criteria = [(len, True), (str, False)]``\이면 우선적으로 ``len(x)``\를 기준으로 내림차순으로 정렬하며
    ``len(x)``\의 값이 같다면 ``str(x)``\를 기준으로 오름차순으로 정렬한다.

    Parameters
    ----------
    iterable : Iterable, yields any type T
        반복 가능한 객체
    criteria : Sequence of criteria
        '정렬할 기준'의 리스트

    Returns
    -------
    sorted_list : Sequence, contains any type T
        정렬된 객체

    Examples
    --------
    글자 길이대로 내림차순으로 정리하며, 글자 길이가 같다면 알파벳 순서대로 정렬하는 방법은 다음과 같다.

    >>> data = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake',
    ...         'horse', 'sheep', 'monkey', 'rooster', 'dog', 'pig']
    >>> multi_sorted(data, (len, True), (str.lower, False))
    ['rooster', 'dragon', 'monkey', 'rabbit', 'horse', 'sheep', 'snake', 'tiger', 'dog', 'pig', 'rat', 'ox']
    """
    if not criteria:
        return sorted(iterable)
    else:
        items = list(iterable)
        for key, reverse in reversed(criteria):
            items.sort(key=key, reverse=reverse)
        return items


def skipper(pred: Callable[[T, T], bool], iterable: Iterable[T]) -> Iterator[T]:
    r"""과거에 나온 값과 비교해서 조건을 만족하는 값만을 산출한다.

    첫 항목을 '기준값'으로 정한 다음 산출한다.
    이후 ``Iterable``\의 항목을 차례대로 순회한다.(이 때 얻는 값을 순회결과값이라 하겠다.)
    기준값과 순회결과값을 함수 ``pred``\를 사용해 비교해서 True이면 순회결과값을 새 기준점으로 잡은 다음
    순회결과값을 산출한다. 이후 ``iterable``\의 항목을 다시 순회하기 시작한다.
    이 작업은 ``iterable``\이 모두 소진될 때까지 건너뛴다.

    -----

    예를 들어 ``pred = operator.gt``, `iterable = [1, 3, 0, 5, 4]``\이라 하자.
    그럼 ``skipper(pred, iterable)``\은 다음과 같은 식으로 동작한다.

    1. 우선 ``iterable``\의 첫 항목(1)을 산출한다. 또한 기준값을 이 첫 항목으로 잡는다.
       기준값: 1
       산출 결과: 1
    2. ``iterable``\의 다음 항목(3)을 가져온다.
       기준값: 1, 순회결과값: 3이므로 ``pred(기준값, 순회결과값) == True``\이다.
       따라서 순회결과값을 새 기준값으로 설정하고 산출한다.
       기준값: 3
       산출 결과: 1, 3
    3. ``iterable``\의 다음 항목(0)을 가져온다.
       기준값: 3, 순회결과값: 0이므로 ``pred(기준값, 순회결과값) == False``\이다.
       따라서 기준값을 그대로 유지하고 순회결과값을 산출하지 않는다.
       기준값: 3
       산출 결과: 1, 3
    4. `iterable``\의 다음 항목(5)을 가져온다.
       기준값: 3, 순회결과값: 5이므로 ``pred(기준값, 순회결과값) == True``\이다.
       따라서 순회결과값을 새 기준값으로 설정하고 산출한다.
       기준값: 5
       산출 결과: 1, 3, 5
    5. ``iterable``\의 다음 항목(4)을 가져온다.
       기준값: 5, 순회결과값: 4이므로 ``pred(기준값, 순회결과값) == False``\이다.
       따라서 기준값을 그대로 유지하고 순회결과값을 산출하지 않는다.
       기준값: 5
       산출 결과: 1, 3, 5
    6. ``iterable``\의 모든 항목이 산출되었으므로 종료한다.

    이 함수에 ``Skipper``\라는 이름이 붙은 이유는 과거에 나온 값과 비교해서
    조건을 만족하면 값을 산출하고 조건을 만족하지 않는다면 조건을 만족하는 값이 나올 때까지
    이터러블의 값을 산출하는 작업을 '건너뛰는' 동작을 하기 때문이다.

    Parameters
    ----------
    pred : Callable object
        비교에 사용될 2변수 함수. 똑같은 타입의 인자를 입력받아 bool 값을 반환한다.
    iterable : Iterable object
        반복 가능한 객체

    Yields
    ------
    items : Any type
        조건을 만족하는 값

    Examples
    --------
    다음은 수열에서 과거에 나왔던 숫자보다 큰 숫자만을 산출하는 예제이다.

    >>> from operator import lt
    >>> list(skipper(lt, [3, 1, 4, 1, 5, 9, 2, 6, 5]))
    [3, 4, 5, 9]
    """
    it = iter(iterable)
    ref = next(it)
    yield ref
    while True:
        try:
            next_item = next(it)
            if pred(ref, next_item):
                ref = next_item
                yield ref
            else:
                continue
        except StopIteration:
            break


@deprecated(instead='itertools.islice(iterable, n, None, start_index)')
def every_nth(iterable: Iterable[T], n: int, start_index: int = 0):
    r"""이터러블의 매 ``n``번째 값을 산출한다.

    Parameters
    ----------
    iterable : Iterable object
        반복 가능한 객체
    n : int
        몇 번째마다 산출할 지 값
    start_index : int, optional
        시작 인덱스

    Yields
    ------
    items : Any type
        매 n번째 값
        
    Exceptions
    ----------
    ValueError
        n <= 0일 때
        start_index < 0일 때

    Examples
    --------
    >>> a = list(range(20))
    >>> list(every_nth(a, 3))   # a[0], a[3], a[6], ...
    [0, 3, 6, 9, 12, 15, 18]
    >>> list(every_nth(a, 3, 10))   # a[10], a[13], a[16], ...
    [10, 13, 16, 19]
    """
    if n <= 0:
        raise ValueError('n must be positive value.')
    if start_index < 0:
        raise ValueError('start_index must be non-negative value')

    it = iter(iterable)
    # 처음 start_index개 항목 스킵
    consume(it, start_index)
    return (value for (index, value) in enumerate(it) if not index % n)


def iterate(func: Callable[..., T], a_0: T, *args, **kwargs) -> Iterator[T]:
    r"""a_(n+1) = func(a_n, *args, **kwargs) 형식의 점화식이 주어질 때 a_0, a_1, a_2, ...를 산출한다.

    Parameters
    ----------
    func : Callable object
        실행할 함수
    a_0 : Any type
        초기 값
    args
        추가로 전달할 인수
    kwargs
        추가로 전달할 키워드 인수

    Yields
    ------
    a_n : Any type
        연쇄적으로 실행되는 함수의 값

    Examples
    --------
    다음은 초기값이 1, 등비가 2인 등비수열을 구하는 예시이다.

    >>> def double(x):
    ...     return x * 2
    ...
    >>> it = iterate(double, 1)
    >>> [next(it) for _ in range(10)]
    [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]

    다음은 초기값이 1, 등차가 2인 등차수열을 구하는 예시이다.

    >>> from operator import add
    >>> it = iterate(add, 1, 2)
    >>> [next(it) for _ in range(10)]
    [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    """
    a_n = a_0
    while True:
        yield a_n
        a_n = func(a_n, *args, **kwargs)


def pairs(iterable: Iterable[T]) -> Iterator[list[Union[tuple[T, T], tuple[T]]]]:
    r"""yields all combination of pairing items.

    >>> for pair in pairs(range(6)):
    ...     print(pair)
    [(0, 1), (2, 3), (4, 5)]
    [(0, 1), (2, 4), (3, 5)]
    [(0, 1), (2, 5), (3, 4)]
    [(0, 2), (1, 3), (4, 5)]
    [(0, 2), (1, 4), (3, 5)]
    ...
    """
    items = list(iterable)
    # Stop Condition
    if not items:
        yield []

    # Handling odd number of items(recursive)
    if len(items) % 2:
        for i in range(len(items) - 1, -1, -1):
            last_items = items[0:i] + items[i + 1:]
            for group in pairs(last_items):
                yield group + [(items[i],)]
    # Handling even number of items(recursive)
    else:
        for i in range(1, len(items)):
            last_items = items[1:i] + items[i + 1:]
            for group in pairs(last_items):
                yield [(items[0], items[i])] + group


def get_duplicate_items(items: Iterable[T], key: Callable[[T], Any] = None):
    r"""중복된 항목을 찾는다.

    만약 key가 지정되어 있다면 items의 각 항목에 대해서 key 함수를 적용한 결과가
    중복되는 항목들을 찾는다.

    Parameters
    ----------
    items : Iterable
        항목들
    key : Callable object
        중복 결과를 찾기 위해 적용할 1변수 함수

    Returns
    -------
    d : dict
        중복된 결과가 저장된 딕셔너리

    Example
    -------
    다음은 문자열에서 중복된 문자를 찾는 예시이다.

    >>> s = 'hello world'
    >>> for duplicated_item in get_duplicate_items(s).items():
    ...     print(duplicated_item)
    ('l', ['l', 'l', 'l'])
    ('o', ['o', 'o'])

    다음은 문자열에서 대소문자를 구분하지 않고 중복된 글자를 찾는 예시이다.

    >>> s = 'AbcdaefbGBhd'
    >>> for duplicated_item in get_duplicate_items(s, key=str.lower).items():
    ...     print(duplicated_item)
    ('a', ['A', 'a'])
    ('b', ['b', 'b', 'B'])
    ('d', ['d', 'd'])
    """
    sorted_items = sorted(items, key=key)
    return {k: list_g for (k, g) in itertools.groupby(sorted_items, key=key) if len(list_g := list(g)) >= 2}


def get_sorted_order(items: Iterable[T], key: Callable[[T], Any] = None) -> int:
    r"""리스트의 정렬 상태를 구한다.

    Parameters
    ----------
    items : Iterable
        항목들
    key : Callable object
        정렬의 기준이 될 함수

    Returns
    -------
    sorted_order : int
        정렬 여부에 따라 다음과 같은 정수값을 반환한다.
        * 1 : 항목들이 오름차순으로 정렬됨
        * 0 : 항목들이 정렬되지 않음
        * -1 : 항목들이 내림차순으로 정렬됨

    Examples
    --------
    >>> get_sorted_order(range(10))
    1
    >>> get_sorted_order(range(10, 0, -1))
    -1
    >>> get_sorted_order([1, 3, 2, 4, 3, 5])
    0

    Notes
    -----
    항목의 갯수가 0개 혹은 1개인 이터레이터들, 혹은 모든 항목이 같은 이터레이터는 항상 정렬 결과로 1을 반환한다.

    >>> get_sorted_order([])
    1
    >>> get_sorted_order([1])
    1
    >>> get_sorted_order([1, 1, 1, 1, 1])
    1
    """
    items_list = list(items)
    items_sorted = sorted(items_list, key=key)
    if items_list == items_sorted:
        return 1
    elif items_list == items_sorted[::-1]:
        return -1
    else:
        return 0


def index_pred(items: Sequence[T], pred: Callable[[T], Any] = bool, fallback_value=None) -> int:
    """items의 각 항목에 대해서 pred를 적용한 값이 처음으로 True인 값의 인덱스를 반환한다.

    Parameters
    ----------
    items : Sequence
        반복 가능한 객체
    pred : Callable
        일변수 함수
    fallback_value : Any
        만약에 값을 찾지 못했을 시 대신 반환할 값

    Returns
    -------
    index : int
        첫 번째로 True인 값의 인덱스, 만약 없으면서 fallback_value가 정해졌다면 fallback_value를 반환하며,
        fallback_value=None이면 ValueError 예외를 일으킨다.

    Exceptions
    ----------
    ValueError
        값이 없으면서도 fallback_value가 정해지지 않았을 경우

    Examples
    --------
    >>> index_pred([0, 1, 0, 0, 1])   # 첫 번째 True인 값의 위치
    1
    >>> index_pred([1, 2, 3, 4, 5, 6, 7], lambda num: num % 3 == 0)   # 첫 3의 배수의 위치
    2
    >>> index_pred([1, 2, 3, 4, 5, 6], lambda num: num % 10 == 0)
    Traceback (most recent call last):
      ...
    ValueError: First truthy value not found
    >>> index_pred([1, 2, 3, 4, 5, 6], lambda num: num % 10 == 0, fallback_value=-1)
    -1
    """
    truthy_values = [bool(pred(x)) for x in items]
    if any(truthy_values):
        return truthy_values.index(True)
    elif fallback_value:
        return fallback_value
    else:
        raise ValueError('First truthy value not found')


def lstrip(iterable: Iterable[T], pred: Callable[[T], Any] = bool) -> Iterator[T]:
    """iterable에서 pred를 실행한 값이 False가 되는 선행 항목들을 제거한다.

    Parameters
    ----------
    iterable : Iterable
        이터러블
    pred : Callable
        실행할 함수

    Returns
    -------
    lstrip_iterable: Iterable
        선행 False 항목들이 제거된 이터러블

    Examples
    --------
    >>> list(lstrip([0, 0, 1, 2, 3, 0, 0, 4]))
    [1, 2, 3, 0, 0, 4]
    >>> list(lstrip([None, None, 1, 2, None, 0, 3, 4], lambda x: isinstance(x, int)))
    [1, 2, None, 0, 3, 4]
    """
    return itertools.dropwhile(invert_bool(pred), iterable)


def rstrip(iterable: Iterable[T], pred: Callable[[T], Any] = bool) -> Iterator[T]:
    """iterable에서 pred를 실행한 값이 False가 되는 후행 항목들을 제거한다.

    Parameters
    ----------
    iterable : Iterable
        이터러블
    pred : Callable
        실행할 함수

    Returns
    -------
    rstrip_iterable: Iterable
        후행 False 항목들이 제거된 이터러블

    Examples
    --------
    >>> list(lstrip([1, 2, 0, 0, 3, 4, 0, 0]))
    [1, 2, 0, 0, 3, 4]
    >>> list(lstrip([1, 2, None, 0, 3, 4, None, None], lambda x: isinstance(x, int)))
    [1, 2, None, 0, 3, 4]
    """
    cache: list[T] = []
    for item in iterable:
        if pred(item):
            yield from cache
            cache.clear()
            yield item
        else:
            cache.append(item)


def strip(iterable: Iterable[T], pred: Callable[[T], Any] = bool) -> Iterator[T]:
    """iterable에서 pred를 실행한 값이 False가 되는 선행 및 후행 항목들을 제거한다.

    Parameters
    ----------
    iterable : Iterable
        이터러블
    pred : Callable
        실행할 함수

    Returns
    -------
    strip_iterable: Iterable
        선행 및 후행 False 항목들이 제거된 이터러블

    Examples
    --------
    >>> list(lstrip([0, 0, 1, 2, 0, 0, 3, 4, 0, 0]))
    [1, 2, 0, 0, 3, 4]
    >>> list(lstrip([None, None, 1, 2, None, 0, 3, 4, None, None], lambda x: isinstance(x, int)))
    [1, 2, None, 0, 3, 4]
    """
    return lstrip(rstrip(iterable, pred), pred)  # noqa # lstrip의 반환타입이 Iterable[T]이므로 억제시켜도 된다


def group_by_interval(iterable: Iterable[T], interval_size, offset: T = 0,
                      include_empty_index=False) -> Iterator[tuple[T, list[T]]]:
    r"""항목들을 구간에 맞춰서 분류한다.

    각 항목들이 구간 ``[interval * n + offset, interval * (n + 1) + offset)`` (``n``\는 정수) 안에 포함된다고 할 때
    ``n`` 값이 같은 항목들은 같은 구간에 들어간다.

    예를 들어 ``interval=5``, ``offset=2``\일 때 ``[0, 1, 2, 3, 4, 5, 12, 14, 16, 25]``\을 구간에 맞춰서 분류하면
    다음과 같다.

    ::

        n == -1일 때 구간 [-3, 2) 안에 있는 항목들 : [0, 1]
        n == 0일 때 구간 [2, 7) 안에 있는 항목들 : [2, 3, 4, 5]
        n == 2일 때 구간 [12, 17) 안에 있는 항목들 : [12, 14, 16]
        n == 4일 때 구간 [22, 27) 안에 있는 항목들 : [25]

    Parameters
    ----------
    iterable : Iterable of type T
        항목들
    interval_size : Type S
        구간의 크기
    offset : Type T : Optional
        구간의 시작 지점
    include_empty_index : bool : Optional
        빈 구간을 출력할지 여부

    Yields
    ------
    interval_starts : T
        구간의 시작 지점
    items : List of T
        구간별로 분류된 항목들

    Examples
    --------
    다음은 위의 설명된 내용대로 항목들을 ``5n+2`` \구간에 맞춰서 분류한다.

    >>> items = [0, 1, 2, 3, 4, 5, 12, 14, 16, 25]
    >>> for k, g in group_by_interval(iterable, 5, 2):
    ...     print(k, g)
    -3 [0, 1]
    2 [2, 3, 4, 5]
    12 [12, 14, 16]
    22 [25]

    다음은 중간의 빈 구간을 포함해서 분류된 항목들을 출력한다.

    >>> items = [0, 1, 2, 3, 4, 5, 12, 14, 16, 25]
    >>> for k, g in group_by_interval(iterable, 5, 2, include_empty_index=True):
    ...     print(k, g)
    -3 [0, 1]
    2 [2, 3, 4, 5]
    7 []
    12 [12, 14, 16]
    17 []
    22 [25]
    """
    # 우선 값들을 순서대로 정렬한다.
    sorted_items: list[T] = sorted(iterable)
    # 만약에 빈 항목들이라면 빈 이터레이터를 반환
    if not sorted_items:
        return iter([])

    # itertools.groupby를 사용해서 그룹으로 나눈다.
    groups: Iterator[tuple[int, Iterator[T]]] = itertools.groupby(sorted_items,
                                                                  key=lambda x: (x - offset) // interval_size)

    # iterable의 각 항목들에 해당되는 인덱스의 최솟값과 최댓값을 구한다.
    minimum_index: int = int((sorted_items[0] - offset) // interval_size)
    maximum_index: int = int((sorted_items[-1] - offset) // interval_size)
    index_range_iterator: Iterator[int] = iter(range(minimum_index, maximum_index + 1))  # 최소, 최대 포함

    for index, group in groups:
        # 만약에 include_empty_index == True이면 이전에 출력하지 못한 중간의 빈 그룹들을 출력한다.
        while (full_index := next(index_range_iterator)) < index:
            if include_empty_index:
                yield full_index * interval_size + offset, []
        yield index * interval_size + offset, list(group)


def sort_by_specific_order(items: Iterable[T], orders: Sequence[V], key: Callable[[T], V] = None, reverse: bool = False,
                           if_not_found: Literal['strict', 'ignore', 'before', 'after'] = 'strict') -> list[T]:
    r"""항목들을 정해진 순서에 맞춰서 정렬한다.

    항목들의 순서가 월(``['Jan', 'Feb', 'Mar', ...]``) 혹은 직급(``['사장', '부장', '과장', ...]``) 과 같이
    특정 순서로 지정되었을 때 유용하다.

    Parameters
    ----------
    items : Iterable of T
        항옥들
    orders : Sequence of V
        정렬할 순서
    key : Callable : ``(T) -> V`` : Optional
        items의 각 항목들에서 orders에 해당되는 값을 추출하기 위한 함수. 기본값은 항등함수이다.
    reverse : bool : Optional
        역순으로 정렬할지 여부. 기본값은 False이다.
    if_not_found : ``{'strict', 'ignore', 'before', 'after'}`` : Optional
        만약의 items에서 order에 해당되는 값을 찾지 못했을 때 처리 방법.

        * strict는 IndexError 오류를 발생한다.
        * ignore는 없는 항목을 제외한다.
        * before는 없는 항목들을 맨 앞에 위치한다.
        * after는 없는 항목들을 맨 뒤에 위치한다.

    Returns
    -------
    sorted_items : list of T
        정렬된 항목들

    Examples
    --------
    다음은 항목들을 월 순서대로 정렬하는 예제이다.

    >>> months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    ...           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    >>> days = [('Jan', 12), ('Sep', 14), ('May', 27), ('Mar', 30), ('Oct', 5)]
    >>> sort_by_specific_order(days, months, key=lambda x: x[0])
    [('Jan', 12), ('Mar', 30), ('May', 27), ('Sep', 14), ('Oct', 5)]

    다음은 항목들을 월 순서대로 역순으로 정렬하되, 없는 항목들을 맨 뒤에 위치시킨다.

    >>> months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    ...           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    >>> days = [('Jan', 12), ('Sep', 14), ('Dog', 1), ('May', 27),
    ...         ('Mar', 30), ('Oct', 5), ('Cat', 35)]
    >>> sort_by_specific_order(days, months, key=lambda x: x[0], reverse=True, if_not_found='after')
    [('Oct', 5), ('Sep', 14), ('May', 27), ('Mar', 30), ('Jan', 12), ('Dog', 1), ('Cat', 35)]
    """
    if key is None:
        key = identity

    items_not_in, items_in = partition(lambda x: key(x) in orders, items)
    items_not_in = list(items_not_in)

    if if_not_found == 'strict' and items_not_in:
        raise IndexError(f'Invalid item: {items_not_in[0]}')
    sorted_items = sorted(items_in, key=lambda x: orders.index(key(x)), reverse=reverse)
    if if_not_found == 'ignore':
        return sorted_items
    elif if_not_found == 'before':
        return items_not_in + sorted_items
    else:
        return sorted_items + items_not_in


def iterable_with_callback(iterable: Iterable[T], callback: Callable[[int, T], None],
                           call_at: Literal['before', 'after'] = 'before') -> Iterator[T]:
    """이터러블의 값들을 그대로 Pass-through해서 산출하고, 산출된 값에 대해서 callback 함수를 실행한다.

    Parameters
    ----------
    iterable : Iterable of T
        이터러블
    callback : Callable object, ``(int, T) -> None``
        이터러블의 각각의 값들에 대해서 실행할 함수.
        첫 번째 인자는 이터러블의 항목 번호이며(0-based) 두번째는 이터러블의 값이다.
    call_at : {'before', 'after'}
        callback을 실행할 시점. 'before'이면 값을 산출하기 전에 callback을 실행하며,
        'after'이면 값을 산출한 후에 callback을 실행한다. 기본값은 'before'이다.

    Yields
    ------
    value : T
        이터러블에서 산출된 값

    Examples
    --------
    다음 코드는 매 3의 배수 항목마다 정해진 메세지로 출력을 한다.

    >>> def notify_every_three(i, item):
    ...     if i % 3 == 0:
    ...         print(f'Item #{i} : {item}')
    >>> for num in iterable_with_callback(range(10), notify_every_three):
    ...     print(num)
    Item #0 : 0
    0
    1
    2
    Item #3 : 3
    3
    4
    5
    Item #6 : 6
    6
    7
    8
    Item #9 : 9
    9
    """
    for i, item in enumerate(iterable):
        if call_at == 'before':
            callback(i, item)
        yield item
        if call_at == 'after':
            callback(i, item)


__all__ = ['common_starts', 'dowhile', 'every_nth', 'get_duplicate_items', 'get_sorted_order', 'group_by_interval',
           'index_pred', 'iterable_with_callback', 'iterate', 'lstrip', 'multi_sorted', 'pairs', 'rstrip', 'skipper',
           'slice_items', 'sort_by_specific_order', 'strip']
