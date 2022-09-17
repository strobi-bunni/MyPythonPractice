from collections import defaultdict
from itertools import groupby
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    overload,
)

KT = TypeVar("KT")
VT = TypeVar("VT")
T = TypeVar("T")
VT2 = TypeVar("VT2")


def _identity(x: T) -> T:
    """항등 함수"""
    return x


def group_value(d: Mapping[KT, VT], key: Callable[[VT], T] = None) -> Dict[T, Dict[KT, VT]]:
    """딕셔너리의 값을 키를 사용해서 묶는다

    Parameters
    ----------
    d: Mapping
        대상 딕셔너리
    key: Callable object : optional
        딕셔너리의 값을 받을 수 있는 함수. 반드시 Hashable한 값을 반환해야 한다. 기본값은 항등함수이다.

    Returns
    -------
    grouped_dict: dict
        값이 정렬된 딕셔너리.
        ``grouped_dict`` 의 키는 ``d`` 의 값을 받아서 ``key`` 함수로 처리한 결과이다.
        ``grouped_dict`` 의 값은 ``key`` 함수의 결과값에 따라 묶인 ``d``의 항목들이 저장된 딕셔너리이다.

    Examples
    --------
    >>> d1 = {1: 'a', 2: 'b', 3: 'a', 4: 'c', 5: 'b'}
    >>> for d_key, d_value, v in group_value(d1).items():
    ...     print(f'{{{d_key}: {d_value}}}')
    {'a': {1: 'a', 3: 'a'}}
    {'b': {2: 'b', 5: 'b'}}
    {'c': {4: 'c'}}
    >>> data = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake',
    ...         'horse', 'sheep', 'monkey', 'rooster', 'dog', 'pig']
    >>> d2 = dict(enumerate(data))
    >>> # 문자열의 길이대로 키를 묶는다.
    >>> for d_key, d_value in group_value(d2, key=len).items():
    ...     print(f'{{{d_key}: {d_value}}}')
    {2: {1: 'ox'}}
    {3: {0: 'rat', 10: 'dog', 11: 'pig'}}
    {5: {2: 'tiger', 5: 'snake', 6: 'horse', 7: 'sheep'}}
    {6: {3: 'rabbit', 4: 'dragon', 8: 'monkey'}}
    {7: {9: 'rooster'}}
    """
    if key is None:
        key = _identity
    items = sorted(d.items(), key=lambda x: key(x[1]))
    return {k: dict(g) for (k, g) in groupby(items, key=lambda x: key(x[1]))}


def merge_dict(d1: Mapping[KT, VT], d2: Mapping[KT, VT], merge_method: Callable[[VT, VT], VT] = None) -> Dict[KT, VT]:
    r"""딕셔너리를 합친다. merge_method에는 같은 키의 값을 합칠 함수를 정의한다.
    만약 merge_method가 정의되어 있지 않다면 d1의 값을 d2로 덮어씌우도록 동작한다.
    이는 Python 3.9에서 추가된 ``d1 | d2`` 문법과 같다.

    Parameters
    ----------
    d1 : Mapping
        첫 번째 딕셔너리
    d2 : Mapping
        두 번째 딕셔너리
    merge_method : Callable
        d1과 d2 모두 있는 키에 대해서 합칠 방법. 2변수 함수이다.
        기본값은 d2의 해당 키의 값을 반환하는 함수(``lambda x, y: y``)이다.

    Returns
    -------
    return_dict : dict
        합쳐진 딕셔너리

    Examples
    --------
    >>> dict1 = {'a': [1, 2], 'b': [3, 4, 5]}
    >>> dict2 = {'b': [3, 4, 5, 6], 'c': [6, 7, 8]}
    >>> merge_dict(dict1, dict2, (lambda x, y: x + y))
    {'a': [1, 2], 'b': [3, 4, 5, 3, 4, 5, 6], 'c': [6, 7, 8]}
    """
    if merge_method is None:
        merge_method = lambda x, y: y

    d1_copy: Dict[KT, VT] = dict(d1)
    for d2_key, d2_value in d2.items():
        if d2_key in d1_copy:
            d1_copy[d2_key] = merge_method(d1_copy[d2_key], d2_value)
        else:
            d1_copy[d2_key] = d2_value
    return d1_copy


@overload
def rename_key(target_dict: Mapping[KT, VT], oldkey: KT, newkey: KT) -> Dict[KT, VT]:
    ...


@overload
def rename_key(d: Mapping[KT, VT], **kwargs) -> Dict[KT, VT]:
    ...


def rename_key(target_dict: Mapping[KT, VT], oldkey: KT = None, newkey: KT = None, **kwargs) -> Dict[KT, VT]:
    r"""딕셔너리의 oldkey에 해당되는 키를 newkey로 바꾼다.

    혹은 kwargs에 oldkey1=newkey1 식으로 지정할 수도 있다.

    Parameters
    ----------
    target_dict : Mapping
        딕셔너리
    oldkey : Any
        이전 키
    newkey : Any
        바꾼 이후의 키
    kwargs
        바꾸기 전 키와 바꾼 후의 키 매핑

    Returns
    -------
    renamed_dict : dict
        키 이름이 바뀐 딕셔너리

    Examples
    --------
    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> rename_key(target_dict, 'a', 'd')
    {'d': 1, 'b': 2, 'c': 3}
    >>> rename_key(target_dict, b='d', c='e')
    {'a': 1, 'd': 2, 'e': 3}
    """
    if (oldkey is None) ^ (newkey is None):
        raise ValueError("Both oldkey and newkey should be null, or not null.")
    elif oldkey is not None:
        rename_mapping: Dict[KT, KT] = {oldkey: newkey}
    else:
        rename_mapping: Dict[KT, KT] = kwargs

    return rename_key_with_mapping(target_dict, rename_mapping)


def rename_key_with_mapping(target_dict: Mapping[KT, VT], rename_mapping: Mapping[KT, KT]) -> Dict[KT, VT]:
    r"""딕셔너리의 키를 주어진 {oldkey: newkey} 매핑에 따라 바꾼다.

    Parameters
    ----------
    target_dict : Mapping
        딕셔너리
    rename_mapping : Mapping
        {이전 키: 이후 키} 매핑

    Returns
    -------
    renamed_dict : dict
        키 이름이 바뀐 딕셔너리

    Examples
    --------
    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> rename_key(target_dict, {'b': 'd', 'c':'e'})
    {'a': 1, 'd': 2, 'e': 3}
    """
    return {(rename_mapping[k] if k in rename_mapping else k): v for (k, v) in target_dict.items()}


def dict_gets(d: Mapping[KT, VT], *keys: KT, default: VT = None) -> VT:
    """딕셔너리에서 keys의 각 키가 있는지 확인하며, 맨 처음 찾은 키의 값을 반환한다.

    Parameters
    ----------
    d : Mapping
        대상 딕셔너리
    keys : KT
        키들
    default : VT
        해당 키가 모두 없을 때 출력할 값

    Returns
    -------
    value : VT
        keys의 각 key에 대해 처음으로 나온 값. 만약 딕셔너리에 keys의 모든 키가 없으면 default 값을 반환한다.

    Examples
    --------
    >>> my_dict = {'a': 1, 'b': 2, 'c': 3}
    >>> dict_gets(my_dict, 'b', 'c', 'd')  # *keys의 키 중 처음으로 my_dict에 있는 키는 'b', 따라서 my_dict['b'] 반환
    2
    >>> dict_gets(my_dict, 'e', 'f', default=10)  # my_dict에 *keys의 키들이 전부 없다. 따라서 default 반환
    10

    Notes
    -----
    이 함수는 dict.get 메서드를 여러 번 사용하는 경우를 줄이기 위해 만들었다.

    >>> my_dict = {'a': 1, 'b': 2, 'c': 3}
    >>> # dict_gets(my_dict, 'b', 'c', 'd', default=10) is equivalent to:
    >>> my_dict.get('b', my_dict.get('c', my_dict.get('d', 10)))
    2
    """
    for key in keys:
        if key in d:
            return d[key]
    return default


def left_join(d1: Mapping[KT, VT], d2: Mapping[KT, VT2], default=None) -> Dict[KT, Tuple[VT, Optional[VT2]]]:
    r"""{d1의 키: (d1의 값, d1의 키에 매칭되는 d2의 값)} 딕셔너리를 제작한다.

    만약에 d1의 키에 매칭되는 d2의 값이 없다면 해당 값은 default로 대체된다.

    이는 SQL의 LEFT JOIN 키워드와 유사하다.

    Parameters
    ----------
    d1 : Mapping
        키의 원본이 되는 딕셔너리
    d2 : Mapping
        병합할 대상 딕셔너리
    default : Any
        d1의 키가 d2에 없을 때 d2의 값 대신 사용할 값

    Returns
    -------
    new_d : dict
        병합된 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> b = {'c': 10, 'd': 20, 'e': 30, 'f': 40}
    >>> left_join(a, b))
    {'a': (1, None), 'b': (2, None), 'c': (3, 10), 'd': (4, 20)}
    """
    return {k: (v, d2.get(k, default)) for (k, v) in d1.items()}


def right_join(d1: Mapping[KT, VT], d2: Mapping[KT, VT2], default=None) -> Dict[KT, Tuple[Optional[VT], VT2]]:
    r"""{d2의 키: (d2의 키에 매칭되는 d1의 값, d2의 값)} 딕셔너리를 제작한다.

    만약에 d2의 키에 매칭되는 d1의 값이 없다면 해당 값은 default로 대체된다.

    이는 SQL의 RIGHT JOIN 키워드와 유사하다.

    Parameters
    ----------
    d1 : Mapping
        병합할 대상 딕셔너리
    d2 : Mapping
        키의 원본이 되는 딕셔너리
    default : Any
        d2의 키가 d1에 없을 때 d1의 값 대신 사용할 값

    Returns
    -------
    new_d : dict
        병합된 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> b = {'c': 10, 'd': 20, 'e': 30, 'f': 40}
    >>> right_join(a, b))
    {'c': (3, 10), 'd': (4, 20), 'e': (None, 30), 'f': (None, 40)}
    """
    return {k: (d1.get(k, default), v2) for (k, v2) in d2.items()}


def full_outer_join(
        d1: Mapping[KT, VT], d2: Mapping[KT, VT2], default=None
) -> Dict[KT, Tuple[Optional[VT], Optional[VT2]]]:
    """{d1와 d2에 공통으로 있는 키: (매칭되는 d1의 값, 매칭되는 d2의 값)} 딕셔너리를 제작한다.

    만약에 d1의 키에 매칭되는 d2의 값이 없거나, d2의 키에 매칭되는 d1의 값이 해당 값이 없다면 해당 값은 default로 대체된다.

    이는 SQL의 FULL OUTER JOIN 키워드와 유사하다.

    Parameters
    ----------
    d1 : Mapping
        키의 원본이 되는 딕셔너리
    d2 : Mapping
        병합할 대상 딕셔너리
    default : Any
        d1의 키가 d2에 없거나, d2의 키가 d1에 없을 때 해당 딕셔너리의 값 대신 사용할 값

    Returns
    -------
    new_d : dict
        병합된 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> b = {'c': 10, 'd': 20, 'e': 30, 'f': 40}
    >>> full_outer_join(a, b)
    {'a': (1, None), 'b': (2, None), 'c': (3, 10), 'd': (4, 20), 'e': (None, 30), 'f': (None, 40)}
    """
    d = left_join(d1, d2, default=default)
    for k, v in d2.items():
        if k not in d:
            d[k] = (default, v)
    return d


def inner_join(d1: Mapping[KT, VT], d2: Mapping[KT, VT2]) -> Dict[KT, Tuple[VT, VT2]]:
    """{d1와 d2에 공통으로 있는 키: (매칭되는 d1의 값, 매칭되는 d2의 값)} 딕셔너리를 제작한다.

    이는 SQL의 INNER JOIN 키워드와 유사하다.

    Parameters
    ----------
    d1 : Mapping
        첫 번째 딕셔너리
    d2 : Mapping
        두 번째 딕셔너리

    Returns
    -------
    new_d : dict
        병합된 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> b = {'c': 10, 'd': 20, 'e': 30, 'f': 40}
    >>> inner_join(a, b)
    {'c': (3, 10), 'd': (4, 20)}
    """
    return {k: (v, d2[k]) for (k, v) in d1.items() if k in d2}


def find_with_value(d: Mapping[KT, VT], value: VT, default=None) -> KT:
    """딕셔너리에서 키에 대응하는 값이 value인 첫 키를 찾는다.

    Parameters
    ----------
    d : Mapping
        대상 딕셔너리
    value : Any
        찾을 값
    default : Any : Optional
        만약에 값을 찾지 못했을 경우 대신 반환할 값

    Returns
    -------
    key : Any
        찾은 키

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> find_with_value(a, 4)
    'd'
    """
    for (k, v) in d.items():
        if v == value:
            return k
    return default


def findall_with_value(d: Mapping[KT, VT], value: VT) -> List[KT]:
    """딕셔너리에서 키에 대응하는 값이 value인 모든 키들을 찾는다.

    Parameters
    ----------
    d : Mapping
        대상 딕셔너리
    value : Any
        찾을 값

    Returns
    -------
    key : Any
        찾은 키들

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 3}
    >>> find_with_value(a, 3)
    ['c', 'e']
    """
    return [k for (k, v) in d.items() if v == value]


def find_with_value_pred(d: Mapping[KT, VT], pred: Callable[[VT], Any] = bool, default=None) -> KT:
    """딕셔너리에서 값이 pred를 만족하는 첫 키를 찾는다.

    Parameters
    ----------
    d : Mapping
        대상 딕셔너리
    pred : Callable
        값의 조건으로 사용할 함수. 생략 시 bool을 사용한다.
    default : Any : Optional
        만약에 값을 찾지 못했을 경우 대신 반환할 값

    Returns
    -------
    key : Any
        찾은 키

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> find_with_value_pred(a, lambda x: x >= 3)
    'c'
    """
    for (k, v) in d.items():
        if pred(v):
            return k
    return default


def findall_with_value_pred(d: Mapping[KT, VT], pred: Callable[[VT], Any] = bool) -> List[KT]:
    """딕셔너리에서 값이 pred를 만족하는 모든 키들을 찾는다.

    Parameters
    ----------
    d : Mapping
        대상 딕셔너리
    pred : Callable
        값의 조건으로 사용할 함수. 생략 시 bool을 사용한다.

    Returns
    -------
    key : Any
        찾은 키들

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 3}
    >>> findall_with_value_pred(a, lambda x: x >= 3)
    ['c', 'd', 'e']
    """
    return [k for (k, v) in d.items() if pred(v)]


def swap_key_and_value(
        d: Mapping[KT, VT], duplicate_handler: Literal["strict", "first", "last"] = "first"
) -> Dict[VT, KT]:
    """딕셔너리의 키와 값을 서로 뒤바꾼다.

    Parameters
    ----------
    d : Mapping
        대상 딕셔너리
    duplicate_handler : {'strict', 'first', 'last'}
        중복된 값이 있을 때 처리법. 기본값은 first이다.

        - strict는 KeyError를 반환
        - first는 처음 등장하는 값 반환
        - last는 마지막 등장하는 값 반환

    Returns
    -------
    d : dict
        키와 값을 뒤바꾼 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 2, 'e': 4, 'f': 3}
    >>> swap_key_and_value(a)
    {1: 'a', 2: 'b', 3: 'c', 4: 'e'}
    >>> swap_key_and_value(a, 'last')
    {1: 'a', 2: 'd', 3: 'f', 4: 'e'}
    >>> swap_key_and_value(a, 'strict')
    Traceback (most recent call last):
      ...
    KeyError: duplicated key
    """
    grouped: DefaultDict[VT, List[KT]] = defaultdict(list)
    for k, v in d.items():
        grouped[v].append(k)

    if duplicate_handler == "first":
        return {v: k[0] for (v, k) in grouped.items()}
    elif duplicate_handler == "last":
        return {v: k[-1] for (v, k) in grouped.items()}
    # duplicate_handler == 'strict'
    elif any((len(k) >= 2) for k in grouped.values()):
        raise KeyError("duplicated key")
    else:
        return {v: k[0] for (v, k) in grouped.items()}


def chain_dict(d1: Mapping[KT, VT], d2: Mapping[VT, VT2], default=None) -> Dict[KT, VT2]:
    """딕셔너리 d1의 값을 딕셔너리 d2의 키로 매핑해서, 딕셔너리 d1과 d2를 연결한 딕셔너리를 반환한다.

    Parameters
    ----------
    d1 : Mapping
        첫 번째 딕셔너리
    d2 : Mapping
        두 번째 딕셔너리
    default : Any
        d1의 값을 d2에서 찾지 못했을 때, d2의 값으로 대신 반환할 값

    Returns
    -------
    d : dict
        연결한 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 2, 'e': 4, 'f': 3}
    >>> b = {1: 10, 2: 20, 3: 30}
    >>> chain_dict(a, b)
    {'a': 10, 'b': 20, 'c': 30, 'd': 20, 'e': None, 'f': 30}
    """
    return {k: d2.get(v, default) for (k, v) in d1.items()}


def flatten_items(d: Mapping[KT, Iterable[VT]]) -> Iterator[Tuple[KT, VT]]:
    """딕셔너리의 값이 이터러블로 되어 있을 때, 값의 이터러블을 풀어서 (키, 각각의 값)을 산출한다.

    Parameters
    ----------
    d : Mapping
        딕셔너리, 값은 이터러블이다.

    Yields
    ------
    k : Any
        딕셔너리 키
    v : Any
        딕셔너리 값 이터러블의 각각의 값

    Examples
    --------
    >>> a = {'a': [1, 2, 3], 'b': [3, 4, 5]}
    >>> for item in flatten_items(a):
    ...     print(item)
    ('a', 1)
    ('a', 2)
    ('a', 3)
    ('b', 3)
    ('b', 4)
    ('b', 5)
    """
    for k, vs in d.items():
        for v in vs:
            yield k, v


def squeeze_dict(d: Mapping[KT, Optional[VT]]) -> Dict[KT, VT]:
    """딕셔너리에서 값이 None인 항목을 지운다.

    Parameters
    ----------
    d : Mapping
        딕셔너리

    Returns
    -------
    return_d : dict
        값이 None인 항목을 제거한 딕셔너리

    Examples
    --------
    >>> d = {'a': 1, 'b': None, 'c': 5, 'd': 4, 'e': None}
    >>> squeeze_dict(d)
    {'a': 1, 'c': 5, 'd': 4}
    """
    return {k: v for (k, v) in d.items() if v is not None}


__all__ = [
    "chain_dict",
    "dict_gets",
    "find_with_value",
    "find_with_value_pred",
    "findall_with_value",
    "findall_with_value_pred",
    "flatten_items",
    "full_outer_join",
    "group_value",
    "inner_join",
    "left_join",
    "merge_dict",
    "rename_key",
    "rename_key_with_mapping",
    "right_join",
    "squeeze_dict",
    "swap_key_and_value",
]
