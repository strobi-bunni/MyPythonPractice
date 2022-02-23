from collections.abc import Callable, Mapping
from itertools import groupby
from typing import Optional, TypeVar, overload

KT = TypeVar('KT')
VT = TypeVar('VT')
T = TypeVar('T')
VT2 = TypeVar('VT2')


def _identity(x: T) -> T:
    """항등 함수
    """
    return x


def group_dict(d: Mapping[KT, VT], key: Callable[[VT], T] = None) -> dict[T, dict[KT, VT]]:
    """딕셔너리의 값을 키를 사용해서 묶는다

    Parameters
    ----------
    d: dict
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
    >>> for k, v in group_dict(d1).items():
    ...     print(f'{{{k}: {v}}}')
    {'a': {1: 'a', 3: 'a'}}
    {'b': {2: 'b', 5: 'b'}}
    {'c': {4: 'c'}}
    >>> data = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake',
    ...         'horse', 'sheep', 'monkey', 'rooster', 'dog', 'pig']
    >>> d2 = dict(enumerate(data))
    >>> # 문자열의 길이대로 키를 묶는다.
    >>> for k, v in group_dict(d2, key=len).items():
    ...     print(f'{{{k}: {v}}}')
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


def dict_merge(d1: Mapping[KT, VT], d2: Mapping[KT, VT], merge_method: Callable[[VT, VT], VT] = None) -> dict[KT, VT]:
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
    >>> d1 = {'a': [1, 2], 'b': [3, 4, 5]}
    >>> d2 = {'b': [3, 4, 5, 6], 'c': [6, 7, 8]}
    >>> dict_merge(d1, d2, (lambda x, y: x + y))
    {'a': [1, 2], 'b': [3, 4, 5, 3, 4, 5, 6], 'c': [6, 7, 8]}
    """
    if merge_method is None:
        merge_method = (lambda x, y: y)

    d1_copy: dict[KT, VT] = dict(d1)
    for d2_key, d2_value in d2.items():
        if d2_key in d1_copy:
            d1_copy[d2_key] = merge_method(d1_copy[d2_key], d2_value)
        else:
            d1_copy[d2_key] = d2_value
    return d1_copy


@overload
def dict_rename_key(target_dict: Mapping[KT, VT], oldkey: KT, newkey: KT) -> dict[KT, VT]: ...


@overload
def dict_rename_key(d: Mapping[KT, VT], **kwargs) -> dict[KT, VT]: ...


def dict_rename_key(target_dict: Mapping[KT, VT], oldkey: KT = None, newkey: KT = None, **kwargs) -> dict[KT, VT]:
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
    >>> dict_rename_key(target_dict, 'a', 'd')
    {'d': 1, 'b': 2, 'c': 3}
    >>> dict_rename_key(target_dict, b='d', c='e')
    {'a': 1, 'd': 2, 'e': 3}
    """
    if (oldkey is None) ^ (newkey is None):
        raise ValueError('Both oldkey and newkey should be null, or not null.')
    elif oldkey is not None:
        rename_mapping: dict[KT, KT] = {oldkey: newkey}
    else:
        rename_mapping: dict[KT, KT] = kwargs

    return dict_rename_key_with_mapping(target_dict, rename_mapping)


def dict_rename_key_with_mapping(target_dict: Mapping[KT, VT], rename_mapping: Mapping[KT, KT]) -> dict[KT, VT]:
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
    >>> dict_rename_key(target_dict, {'b': 'd', 'c':'e'})
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
    value = default
    for key in keys:
        if key in d:
            value = d[key]
            break
    return value


def left_join(d1: Mapping[KT, VT], d2: Mapping[KT, VT2]) -> dict[KT, tuple[VT, Optional[VT2]]]:
    r"""{d1의 키: (d1의 값, d1의 키에 매칭되는 d2의 값)} 딕셔너리를 제작한다.

    만약에 d1의 키에 매칭되는 d2의 값이 없다면 해당 값은 None으로 대체된다.

    이는 SQL의 LEFT JOIN 키워드와 유사하다.

    Parameters
    ----------
    d1 : Dict
        키의 원본이 되는 딕셔너리
    d2 : Dict
        병합할 대상 딕셔너리

    Returns
    -------
    new_d : Dict
        병합된 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> b = {'c': 10, 'd': 20, 'e': 30, 'f': 40}
    >>> left_join(a, b))
    {'a': (1, None), 'b': (2, None), 'c': (3, 10), 'd': (4, 20)}
    """
    return {k: (v, d2.get(k)) for (k, v) in d1.items()}


def right_join(d1: Mapping[KT, VT], d2: Mapping[KT, VT2]) -> dict[KT, tuple[Optional[VT], VT2]]:
    r"""{d2의 키: (d1의 값, d2의 키에 매칭되는 d1의 값)} 딕셔너리를 제작한다.

    만약에 d2의 키에 매칭되는 d1의 값이 없다면 해당 값은 None으로 대체된다.

    이는 SQL의 RIGHT JOIN 키워드와 유사하다.

    Parameters
    ----------
    d1 : Dict
        병합할 대상 딕셔너리
    d2 : Dict
        키의 원본이 되는 딕셔너리

    Returns
    -------
    new_d : Dict
        병합된 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> b = {'c': 10, 'd': 20, 'e': 30, 'f': 40}
    >>> right_join(a, b))
    {'c': (3, 10), 'd': (4, 20), 'e': (None, 30), 'f': (None, 40)}
    """
    return {k: (d1.get(k), v2) for (k, v2) in d2.items()}


def full_outer_join(d1: Mapping[KT, VT], d2: Mapping[KT, VT2]) -> dict[KT, tuple[Optional[VT], Optional[VT2]]]:
    """{d1 및 d2의 키: (매칭되는 d1의 값, 매칭되는 d2의 값)} 딕셔너리를 제작한다.

    만약에 d1의 키에 매칭되는 d2의 값이 없거나, d2의 키에 매칭되는 d1의 값이 해당 값이 없다면 해당 값은 None으로 대체된다.

    이는 SQL의 FULL OUTER JOIN 키워드와 유사하다.

    Parameters
    ----------
    d1 : Dict
        키의 원본이 되는 딕셔너리
    d2 : Dict
        병합할 대상 딕셔너리

    Returns
    -------
    new_d : Dict
        병합된 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> b = {'c': 10, 'd': 20, 'e': 30, 'f': 40}
    >>> full_outer_join(a, b)
    {'a': (1, None), 'b': (2, None), 'c': (3, 10), 'd': (4, 20), 'e': (None, 30), 'f': (None, 40)}
    """
    d = left_join(d1, d2)
    for k, v in d2.items():
        if k not in d:
            d[k] = (None, v)
    return d


def inner_join(d1: Mapping[KT, VT], d2: Mapping[KT, VT2]) -> dict[KT, tuple[VT, VT2]]:
    """{d1와 d2에 공통으로 있는 키: (매칭되는 d1의 값, 매칭되는 d2의 값)} 딕셔너리를 제작한다.

    이는 SQL의 INNER JOIN 키워드와 유사하다.

    Parameters
    ----------
    d1 : Dict
        첫 번째 딕셔너리
    d2 : Dict
        두 번째 딕셔너리

    Returns
    -------
    new_d : Dict
        병합된 딕셔너리

    Examples
    --------
    >>> a = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    >>> b = {'c': 10, 'd': 20, 'e': 30, 'f': 40}
    >>> inner_join(a, b)
    {'c': (3, 10), 'd': (4, 20)}
    """
    return {k: (v, d2[k]) for (k, v) in d1.items() if k in d2}


__all__ = ['dict_gets', 'dict_merge', 'dict_rename_key', 'dict_rename_key_with_mapping', 'full_outer_join',
           'group_dict', 'inner_join', 'left_join', 'right_join']
