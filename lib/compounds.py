from typing import Optional, Sequence, Union

T_JSON_Primitive = Union[str, bool, None, int, float]
T_JSON_Types = Union[T_JSON_Primitive, 'T_JSON_Container']
T_JSON_List = list[T_JSON_Types]
T_JSON_Object = dict[str, T_JSON_Types]
T_JSON_Container = Union[T_JSON_List, T_JSON_Object]


# 리스트에 항목을 추가한다는 뜻의 전용 싱글톤
class _NewListItemSingleton:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(_NewListItemSingleton, cls).__new__(cls)
        return cls.instance  # noqa


NEW_LIST_ITEM = _NewListItemSingleton()  # keys에 이게 있으면 리스트에 새 항목을 만든다.


def _is_primitive(item: T_JSON_Object) -> bool:
    return isinstance(item, int) \
           or isinstance(item, float) \
           or isinstance(item, str) \
           or isinstance(item, bool) \
           or item is None


def get_item_tree(data: T_JSON_Container, *keys: Union[str, int], default=None, strict=False) -> T_JSON_Types:
    # TODO: 문서 추가
    # 종료 조건: keys가 없으면 그대로를 반환
    if not keys:
        return data

    # keys에서 첫 값은 인덱스를 찾을 때 쓰고, 마지막 값들은 재귀할 때 쓴다.
    keys_head, *keys_tail = keys

    # 딕셔너리(Python) / 객체(JSON)
    if isinstance(data, dict):
        if keys_head in data:
            return get_item_tree(data[keys_head], *keys_tail, default=default, strict=strict)
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

        return get_item_tree(data[keys_head], *keys_tail, default=default, strict=strict)

    # 기본 자료형
    elif strict:
        raise ValueError(f'Excessive key for primitive type: {keys_head}')
    else:
        return default


def _prepare_container_for_dict(data: dict, keys_head: Union[str, int],
                                keys_tail: Sequence[Union[str, int]] = ()) -> None:
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


def set_item_tree_value(data: T_JSON_Container, *keys: Union[str, int], value=None) -> None:
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
        # 꼬리가 있으면서 data에 머리가 없다면: 새 컨테이너를 만든다.
        else:
            if keys_head not in data:
                _prepare_container_for_dict(data, keys_head, keys_tail)
            # 꼬리가 있으면서 data에 머리가 있다면: 머리에 따라서 동작이 달라짐
            else:
                if _is_primitive(data[keys_head]):
                    # 만약에 원시타입이면 새 컨테이너를 만들고 재귀한다.
                    _prepare_container_for_dict(data, keys_head, keys_tail)
                    set_item_tree_value(data[keys_head], *keys_tail, value=value)
                else:
                    # 만약 컨테이너라면 재귀한다.
                    set_item_tree_value(data[keys_head], *keys_tail, value=value)

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
            elif isinstance(keys_head, int) and (-len(data) <= keys_head < len(data)):
                # 꼬리가 있으면서 머리가 유효한 리스트 인덱스다:
                if _is_primitive(data[keys_head]):
                    # 만약에 원시타입이면 새 컨테이너를 만들고 재귀한다
                    _prepare_container_for_list(data, keys_head, keys_tail)
                    set_item_tree_value(data[keys_head], *keys_tail, value=value)
                else:
                    set_item_tree_value(data[keys_head], *keys_tail, value=value)
            else:
                # 유효한 인덱스가 아니면 에러 처리
                raise IndexError(f'Invalid index {keys_head} for list {data}')

    else:
        raise ValueError(f'{data} is primitive type, not a container.')


# TODO: 구현할 것
def delete_item_tree(data: T_JSON_Container, *keys: Union[str, int]) -> None:
    raise NotImplementedError
