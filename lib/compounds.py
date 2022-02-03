from typing import Sequence, Union

T_JSON_Primitive = Union[str, bool, None, int, float]
T_JSON_Types = Union[T_JSON_Primitive, 'T_JSON_Container']
T_JSON_List = list[T_JSON_Types]
T_JSON_Object = dict[str, T_JSON_Types]
T_JSON_Container = Union[T_JSON_List, T_JSON_Object]


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


def _prepare_container(data: T_JSON_Container, keys_head: Union[str, int],
                       keys_tail: Sequence[Union[str, int]]) -> None:
    if isinstance(keys_tail[0], int):
        data[keys_head] = []
    else:
        data[keys_head] = {}


# TODO: 완전히 구현할 것
# TODO: data가 리스트나 딕셔너리일 때의 동작을 _set_item_in_container로 일원화할것
def set_item_tree_value(data: T_JSON_Container, *keys: Union[str, int], value) -> None:
    raise NotImplementedError

    # 종료 조건: key가 없으면 아무것도 하지 않는다.
    if not keys:
        return

    # keys에서 첫 값은 인덱스를 찾을 때 쓰고, 마지막 값들은 재귀할 때 쓴다.
    keys_head, *keys_tail = keys

    # 만약 keys_head가 유일한 키라면 그냥 값을 넣고 종료한다.
    if not keys_tail:
        if isinstance(data, dict):
            data[keys_head] = value

    # 딕셔너리(Python) / 객체(JSON)
    if isinstance(data, dict):
        if keys_head in data:
            if keys_tail:
                _prepare_container(data, keys_head, keys_tail)
            else:
                set_item_tree_value(data[keys_head], *keys_tail, value=value)

        elif keys_tail:
            # 만약에 다음 키가 있다면 적합한 컨테이너를 만든다.
            _prepare_container(data, keys_head, keys_tail)
            set_item_tree_value(data[keys_head], *keys_tail, value=value)

        else:
            # 마지막 키라면 값을 넣는다.
            data[keys_head] = value

    elif isinstance(data, list):
        # 만약에 빈 리스트라면 그냥 값을 추가한다.
        if not data:
            data.append(value)

        if not isinstance(keys_head, int):
            raise KeyError(f'Invalid key type for list: {keys_head} is not a int')
        # 리스트의 인덱스가 값을 벗어나는지 여부
        if not (-len(data) <= keys_head < len(data)):  # 음수 인덱스 고려
            raise IndexError(f'Index out of range: {keys_head}')

        # 만약에 해당 인덱스가 있다면

    else:
        raise ValueError(f'{data} is primitive type, not a container.')


# TODO: 구현할 것
def delete_item_tree(data: T_JSON_Container, *keys: Union[str, int]) -> None:
    raise NotImplementedError


test_data = {'aaa': {'bbb': {'ccc': 1, 'ddd': 0.5, 'eee': True, 'fff': False},
                     'ggg': [10, 20, 'test', 'hello', 'world']},
             'hhh': [0.1, 0.2, [0.3, 0.4, 0.5], {'iii': 'python'}]}
print(set_item_tree_value(test_data, 'aaa', value={}))
print(test_data)
print(set_item_tree_value(test_data, 'aaa', 'xxx', value=30))
