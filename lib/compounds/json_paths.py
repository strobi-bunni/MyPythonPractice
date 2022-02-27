import re
from typing import Dict, List, Optional, Sequence, Union

T_JSON_Primitive = Union[str, bool, None, int, float]
T_JSON_Types = Union[T_JSON_Primitive, 'T_JSON_Container']
T_JSON_List = List[T_JSON_Types]
T_JSON_Object = Dict[str, T_JSON_Types]
T_JSON_Container = Union[T_JSON_List, T_JSON_Object]


# 리스트에 항목을 추가한다는 뜻의 전용 싱글톤
class NewListItemSingleton:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NewListItemSingleton, cls).__new__(cls)
        return cls.instance  # noqa

    def __repr__(self):
        return 'NewListItemSingleton()'


NEW_LIST_ITEM = NewListItemSingleton()  # keys에 이게 있으면 리스트에 새 항목을 만든다.
NEW_LIST_SYMBOL = '+'
JSON_OBJECT_SEP = '.'
re_interger = re.compile(r'^[+\-]?\d+$')


def _is_primitive(item: T_JSON_Object) -> bool:
    return isinstance(item, int) \
           or isinstance(item, float) \
           or isinstance(item, str) \
           or isinstance(item, bool) \
           or item is None


def get_json_tree_item(data: T_JSON_Container, *keys: Union[str, int], default=None, strict=False) -> T_JSON_Types:
    r"""JSON 데이터에서 해당 경로의 값을 본다.

    Parameters
    ----------
    data : Any
        JSON 파일에서 가져온 데이터
    keys : str or int
        각 단계별 키
    default : Any : Optional
        값을 가져오지 못했을 시 대신 가져올 값. 기본값은 none이다. strict=False일 때만 동작한다.
    strict : bool : Optional
        값을 가져오지 못할 시 예외 처리할 지 여부. 기본값은 False이다.

    Returns
    -------
    value : Any
        가져온 값

    Examples
    --------
    >>> d = {'a': 1, 'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> get_json_tree_item(d, 'a')   # d['a']
    1
    >>> get_json_tree_item(d, 'b')   # d['b']
    [2, 3, 4]
    >>> get_json_tree_item(d, 'b', 2)   # d['b'][2]
    4
    >>> get_json_tree_item(d, 'c')   # d['c']
    {'d': 'hello', 'e': 'world'}
    >>> get_json_tree_item(d, 'c', 'd')   # d['c']['d']
    'hello'
    >>> get_json_tree_item(d, 'c', 'f', 0)   # d['c']['f'][0]
    True
    >>> get_json_tree_item(d, 'c', 'g', 'h')   # d['c']['g']['h']   # d['c']['g']는 없으므로 default=None을 반환
    None

    Notes
    -----
    get_json_tree_item(data, key0, key1, key2)는 data[key0][key1][key2]와 비슷하나,
    중간에 없는 값이 있을 경우 None을 대신 반환하기 때문에 Null-safety 처리가 간단하다.

    위의 예시에서 ``get_json_tree_item(d, 'c', 'g', 0)``\을 예외 처리를 한다고 할 경우
    ``d.get('c', {}).get('g', {}).get('h', None)``\으로 대신 쓸 수 있다.
    """
    # 종료 조건: keys가 없으면 그대로를 반환
    if not keys:
        return data

    # keys에서 첫 값은 인덱스를 찾을 때 쓰고, 마지막 값들은 재귀할 때 쓴다.
    keys_head, *keys_tail = keys

    # 딕셔너리(Python) / 객체(JSON)
    if isinstance(data, dict):
        if keys_head in data:
            return get_json_tree_item(data[keys_head], *keys_tail, default=default, strict=strict)
        elif strict:
            raise KeyError(f'Key not found: {keys_head}')
        else:
            return default

    # 리스트(Python) / 배열(JSON)
    elif isinstance(data, list):
        # Non-strict일 시 작업?
        # 리스트의 인덱스는 숫자여야만 한다.
        if strict and not isinstance(keys_head, int):
            raise KeyError(f'Invalid key type for list: {keys_head} is not a int')
        # 리스트의 인덱스가 값을 벗어나는지 여부
        if strict and not (-len(data) <= keys_head < len(data)):  # 음수 인덱스 고려
            raise IndexError(f'Index out of range: {keys_head}')

        return get_json_tree_item(data[keys_head], *keys_tail, default=default, strict=strict)

    # 기본 자료형
    elif strict:
        raise ValueError(f'Excessive key for primitive type: {keys_head}')
    else:
        return default


def _prepare_container_for_dict(data: dict, keys_head: Union[str, int],
                                keys_tail: Sequence[Union[str, int]]) -> None:
    if keys_tail[0] is NEW_LIST_ITEM:
        data[keys_head] = []
    else:
        data[keys_head] = {}


def _prepare_container_for_list(data: list, keys_head: Optional[Union[str, int]],
                                keys_tail: Sequence[Union[str, int]]) -> None:
    new_container = [] if keys_tail[0] is NEW_LIST_ITEM else {}
    if keys_head is None:
        data.append(new_container)
    else:
        data[keys_head] = new_container


def set_json_tree_item(data: T_JSON_Container, *keys: Union[str, int, NewListItemSingleton], value=None) -> None:
    r"""JSON 데이터에서 해당 경로의 값을 추가하거나 변경한다.

    Parameters
    ----------
    data : Any
        JSON 파일에서 가져온 데이터
    keys : str or int or NEW_LIST_ITEM
        각 단계별 키. 만약 리스트에 값을 추가하려고 한다면 ``NEW_LIST_ITEM``\을 사용한다.
    value : Any : Optional
        해당 경로에 설정할 값

    Examples
    --------
    >>> d = {'a': 1, 'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> set_json_tree_item(d, 'a', value=10)   # d['a'] = 10
    >>> print(d)
    {'a': 10, 'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> set_json_tree_item(d, 'b', NEW_LIST_ITEM, value=5)   # d['b'].append(5)
    >>> print(d)
    {'a': 10, 'b': [2, 3, 4, 5], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> set_json_tree_item(d, 'c', 'f', 0, value=None)   # d['b']['f'][0] = None
    >>> print(d)
    {'a': 10, 'b': [2, 3, 4, 5], 'c': {'d': 'hello', 'e': 'world', 'f': [True, 0]}}
    >>> set_json_tree_item(d, 'a', NEW_LIST_ITEM, NEW_LIST_ITEM, 'x', value=5)
    >>> print(d)
    {'a': [[{'x': 5}]], 'b': [2, 3, 4, 5], 'c': {'d': 'hello', 'e': 'world', 'f': [True, 0]}}
    """
    # 종료 조건: key가 없으면 아무것도 하지 않는다.
    if not keys:
        return

    # keys에서 첫 값은 인덱스를 찾을 때 쓰고, 마지막 값들은 재귀할 때 쓴다.
    keys_head, *keys_tail = keys

    # 딕셔너리(Python) / 객체(JSON)
    if isinstance(data, dict):
        # 꼬리 유무로 판단하는 것이 좋을 듯.
        # 꼬리가 없다면 최종적으로 값을 넣는다.
        if not keys_tail:
            data[keys_head] = value
        # 새 컨테이너를 만드는 조건
        # 1. 꼬리가 있지만 머리가 없다
        # 2. 꼬리가 있지만 data의 머리에 해당되는 값이 원시자료형이다
        else:
            if keys_head not in data or _is_primitive(data[keys_head]):
                _prepare_container_for_dict(data, keys_head, keys_tail)
            set_json_tree_item(data[keys_head], *keys_tail, value=value)

    elif isinstance(data, list):
        # 꼬리 유무로 판단하는 것이 좋을 듯.
        if not keys_tail:
            # 꼬리가 없다면:
            if keys_head is NEW_LIST_ITEM:
                # 새 항목을 만든다고 할 때(리스트는 딕셔너리와는 다르게 자동으로 항목을 추가하지 않는다)
                data.append(value)
            elif isinstance(keys_head, int) and (-len(data) <= keys_head < len(data)):
                data[keys_head] = value
            else:
                # 유효한 인덱스가 아니면 에러 처리
                raise IndexError(f'Invalid index {keys_head} for list {data}')
        else:
            # 꼬리가 있다면
            if keys_head is NEW_LIST_ITEM:
                # 꼬리가 있으면서 현재 리스트에 새 항목을 만든다 -> 리스트에 새 컨테이너를 추가한다.
                _prepare_container_for_list(data, None, keys_tail)
                set_json_tree_item(data[-1], *keys_tail, value=value)
            elif isinstance(keys_head, int) and (-len(data) <= keys_head < len(data)):
                # 꼬리가 있으면서 머리가 유효한 리스트 인덱스다:
                if _is_primitive(data[keys_head]):
                    # 만약에 원시타입이면 새 컨테이너를 만들고 재귀한다
                    _prepare_container_for_list(data, keys_head, keys_tail)
                set_json_tree_item(data[keys_head], *keys_tail, value=value)
            else:
                # 유효한 인덱스가 아니면 에러 처리
                raise IndexError(f'Invalid index {keys_head} for list {data}')

    else:
        raise ValueError(f'{data} is primitive type, not a container.')


def delete_json_tree_item(data: T_JSON_Container, *keys: Union[str, int], strict=False) -> None:
    r"""JSON 데이터에서 해당 경로의 값을 지운다.

    Parameters
    ----------
    data : Any
        JSON 파일에서 가져온 데이터
    keys : str or int
        각 단계별 키
    strict : bool : Optional
        값을 가져오지 못할 시 예외 처리할 지 여부. 기본값은 False이다.

    Examples
    --------
    >>> d = {'a': 1, 'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> delete_json_tree_item(d, 'a')   # del d['a']
    >>> print(d)
    {'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> delete_json_tree_item(d, 'b', -1)   # del d['b'][-1]
    >>> print(d)
    {'b': [2, 3], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> delete_json_tree_item(d, 'c', 'f')   # d['b']['f'][0] = None
    >>> print(d)
    {'b': [2, 3], 'c': {'d': 'hello', 'e': 'world'}
    """
    # 종료 조건: key가 없으면 아무것도 하지 않는다.
    if not keys:
        return

    # keys에서 첫 값은 인덱스를 찾을 때 쓰고, 마지막 값들은 재귀할 때 쓴다.
    keys_head, *keys_tail = keys

    if isinstance(data, dict):
        # 만약에 꼬리가 없다면: 머리에 해당되는 값을 지운다.
        if not keys_tail:
            data.pop(keys_head, None)
        elif keys_head in data:
            # 만약에 꼬리가 있다면 꼬리에 해당되는 값을 지운다.
            delete_json_tree_item(data[keys_head], *keys_tail)
        elif strict:
            raise KeyError(f'Key {keys_head} not found')
    elif isinstance(data, list):
        # 만약에 꼬리가 없다면: 머리에 해당되는 값을 지운다.
        if not keys_tail:
            if isinstance(keys_head, int) and (-len(data) <= keys_head < len(data)):
                data.pop(keys_head)
            elif strict:
                raise KeyError(f'Invalid index')

        else:
            # 만약에 꼬리가 있다면 꼬리에 해당되는 값을 지운다.
            if isinstance(keys_head, int) and (-len(data) <= keys_head < len(data)):
                delete_json_tree_item(data[keys_head], *keys_tail)
            elif strict:
                raise KeyError(f'Invalid index')

    else:
        raise ValueError('Cannot delete primitive value')


def tokenize_json_path(s: str):
    return_tokens: List[Union[NewListItemSingleton, int, str]] = []
    if not s:
        return return_tokens
    parts = s.split(JSON_OBJECT_SEP)
    for part in parts:
        if part == NEW_LIST_SYMBOL:
            return_tokens.append(NEW_LIST_ITEM)
        elif re_interger.match(part):
            return_tokens.append(int(part))
        else:
            return_tokens.append(part)
    return return_tokens


def get_json_item(data, json_path='', default=None, strict=False):
    r"""이 함수는 ``get_json_tree_item``\의 간단한 버전이다. Javascript-style으로 JSON 내의 객체 값을 가져올 수 있다.

    키의 구분은 ``.``\으로 한다. 예를 들어 ``get_json_tree_item(d, 'a', 'b', 'c')``\은
    ``get_json_item(d, 'a.b.c')``\로 쓸 수 있다.

    Parameters
    ----------
    data : Any
        JSON 파일에서 가져온 데이터
    json_path : str
        JSON 객체 내의 값을 참조하기 위한 키 표현식. 각각의 키는 ``.``\로 구분한다.
    default : Any : Optional
        값을 가져오지 못했을 시 대신 가져올 값. 기본값은 none이다. strict=False일 때만 동작한다.
    strict : bool : Optional
        값을 가져오지 못할 시 예외 처리할 지 여부. 기본값은 False이다.

    Returns
    -------
    value : Any
        가져온 값

    Examples
    --------
    >>> d = {'a': 1, 'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> get_json_item(d, 'a')   # d['a']
    1
    >>> get_json_item(d, 'b')   # d['b']
    [2, 3, 4]
    >>> get_json_item(d, 'b.2')   # d['b'][2]
    4
    >>> get_json_item(d, 'c')   # d['c']
    {'d': 'hello', 'e': 'world'}
    >>> get_json_item(d, 'c.d')   # d['c']['d']
    'hello'
    >>> get_json_item(d, 'c.f.0')   # d['c']['f'][0]
    True
    >>> get_json_item(d, 'c.g.h')   # d['c']['g']['h']   # d['c']['g']는 없으므로 default=None을 반환
    None
    """
    return get_json_tree_item(data, *tokenize_json_path(json_path), default=default, strict=strict)


def set_json_item(data, json_path='', value=None):
    r"""이 함수는 ``set_json_item_tree``\의 간단한 버전이다. JSON 내의 객체 값을 손쉽게 수정할 수 있다.

    키의 구분은 ``.``\으로 한다. 예를 들어 ``set_json_item_tree(d, 'a', 'b', 'c', value=10)``\은
    ``set_json_item(d, 'a.b.c', 10)``\로 쓸 수 있다.
    
    리스트에 새 값을 쓰기 위해서는 ``+`` 기호를 사용한다. ``set_json_item_tree(d, 'a', NEW_LIST_ITEM value=10)``\은
    ``set_json_item(d, 'a.+', 10)``\로 쓸 수 있다.

    Parameters
    ----------
    data : Any
        JSON 파일에서 가져온 데이터
    json_path : str
        JSON 객체 내의 값을 참조하기 위한 키 표현식. 각각의 키는 ``.``\로 구분한다.
    value : Any : Optional
        해당 경로에 설정할 값

    Examples
    --------
    >>> d = {'a': 1, 'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> set_json_item(d, 'a', 10)   # d['a'] = 10
    >>> print(d)
    {'a': 10, 'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> set_json_item(d, 'b.+', 5)   # d['b'].append(5)
    >>> print(d)
    {'a': 10, 'b': [2, 3, 4, 5], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> set_json_item(d, 'c.f.0', None)   # d['b']['f'][0] = None
    >>> print(d)
    {'a': 10, 'b': [2, 3, 4, 5], 'c': {'d': 'hello', 'e': 'world', 'f': [True, 0]}}
    >>> set_json_item(d, 'a.+.+.x', value=5)
    >>> print(d)
    {'a': [[{'x': 5}]], 'b': [2, 3, 4, 5], 'c': {'d': 'hello', 'e': 'world', 'f': [True, 0]}}
    """
    set_json_tree_item(data, *tokenize_json_path(json_path), value=value)


def delete_json_item(data, json_path='', strict=False):
    r"""이 함수는 ``delete_json_tree_item``\의 간단한 버전이다. JSON 내의 객체 값을 손쉽게 수정할 수 있다.

    키의 구분은 ``.``\으로 한다. 예를 들어 ``delete_json_tree_item(d, 'a', 'b', 'c')``\은
    ``delete_json_item(d, 'a.b.c')``\로 쓸 수 있다.

    Parameters
    ----------
    data : Any
        JSON 파일에서 가져온 데이터
    json_path : str
        JSON 객체 내의 값을 참조하기 위한 키 표현식. 각각의 키는 ``.``\로 구분한다.
    strict : bool : Optional
        값을 가져오지 못할 시 예외 처리할 지 여부. 기본값은 False이다.

    Examples
    --------
    >>> d = {'a': 1, 'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> delete_json_item(d, 'a')   # del d['a']
    >>> print(d)
    {'b': [2, 3, 4], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> delete_json_item(d, 'b.-1')   # del d['b'][-1]
    >>> print(d)
    {'b': [2, 3], 'c': {'d': 'hello', 'e': 'world', 'f': [True, False]}}
    >>> delete_json_item(d, 'c.f')   # d['b']['f'][0] = None
    >>> print(d)
    {'b': [2, 3], 'c': {'d': 'hello', 'e': 'world'}
    """
    delete_json_tree_item(data, *tokenize_json_path(json_path), strict=strict)


__all__ = ['NEW_LIST_ITEM', 'NewListItemSingleton', 'delete_json_item', 'delete_json_tree_item', 'get_json_item',
           'get_json_tree_item', 'set_json_item', 'set_json_tree_item']
