import re
from typing import Optional, Sequence, Union

T_JSON_Primitive = Union[str, bool, None, int, float]
T_JSON_Types = Union[T_JSON_Primitive, 'T_JSON_Container']
T_JSON_List = list[T_JSON_Types]
T_JSON_Object = dict[str, T_JSON_Types]
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


# TODO: 테스트할 것
def get_json_tree_item(data: T_JSON_Container, *keys: Union[str, int], default=None, strict=False) -> T_JSON_Types:
    # TODO: 문서 추가
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
        # TODO: Non-strict일 시 작업 추가
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


# TODO: 테스트할 것
def set_json_tree_item(data: T_JSON_Container, *keys: Union[str, int], value=None) -> None:
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


# TODO: 테스트할 것
def delete_json_tree_item(data: T_JSON_Container, *keys: Union[str, int], strict=False) -> None:
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


__all__ = ['NewListItemSingleton', 'NEW_LIST_ITEM', 'delete_json_tree_item', 'get_json_tree_item', 'set_json_tree_item']


def tokenize_json_path(s: str):
    return_tokens: list[Union[NewListItemSingleton, int, str]] = []
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
    return get_json_tree_item(data, *tokenize_json_path(json_path), default=default, strict=strict)


def set_json_item(data, json_path='', value=None):
    set_json_tree_item(data, *tokenize_json_path(json_path), value=value)


def delete_json_item(data, json_path='', strict=False):
    delete_json_tree_item(data, *tokenize_json_path(json_path), strict=strict)
