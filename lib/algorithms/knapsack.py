# Original code from:
# https://www.rosettacode.org/wiki/Knapsack_problem/0-1#Recursive_dynamic_programming_algorithm
# Python3에 호환되도록 바꿨으며, 함수로 만들어서 쉽게 사용할 수 있도록 함
from collections import namedtuple
from collections.abc import Iterable, Iterator
from typing import Optional, TypeVar, Union

from ..iterable_tools.itertools_recipe import powerset

T = TypeVar('T')


class KnapsackItem(namedtuple):
    # 아이템 정보를 담은 튜플
    name: T
    weight: int
    value: int


def get_total_value(items: list[KnapsackItem], max_weight: int) -> int:
    return sum(x.value for x in items) if sum(x.weight for x in items) <= max_weight else 0


def get_total_weight(items: list[KnapsackItem]) -> int:
    return sum(x.weight for x in items)


def _solve(items: list[KnapsackItem], max_weight: int,
           cache_dict: dict[tuple[tuple[KnapsackItem, ...], int], list[KnapsackItem]]) -> list[KnapsackItem]:
    # 종료 조건
    if not items:
        return []
    # 동적 계획법을 사용. 캐시에 없다면 다음을 실행
    if (tuple(items), max_weight) not in cache_dict:
        head, *tail = items
        # 재귀적으로 실행한다.
        include: list[KnapsackItem] = [head, *_solve(tail, max_weight - head.weight, cache_dict)]
        dont_include: list[KnapsackItem] = _solve(tail, max_weight, cache_dict)
        if get_total_value(include, max_weight) > get_total_value(dont_include, max_weight):
            answer = include
        else:
            answer = dont_include
        # 실행 결과를 저장
        cache_dict[(tuple(items), max_weight)] = answer
    return cache_dict[(tuple(items), max_weight)]


def solve_knapsack_0or1(items: Iterable[Union[tuple[T, int, Optional[int]], tuple[T, int]]],
                        max_weight: int) -> tuple[list[KnapsackItem], int, int]:
    """0-1 가방 문제를 푼다.

    Parameters
    ----------
    items : Iterable of KnapsackItem instances, or Iterable of 2-or-3 Tuples
        항목이 저장된 튜플. 튜플의 길이는 2 혹은 3이어야 한다.
        튜플의 길이가 3일 경우 (항목 이름, 항목의 무게, 항목의 가치)로 해석된다.
        튜플의 길이가 2거나 '항목의 가치'가 None인 경우(즉 가치가 생략된 경우)
        항목의 가치는 항목의 무게와 같다고 간주한다.

        2021-07-12 KnapsackItem 객체를 직접 받을 수 있음

    max_weight : int
        무게 제한

    Returns
    -------
    solution : list of KnapsackItem
        0-1 가방 문제의 해. 이름, 무게, 가치가 저장된 항목 객체의 리스트
    total_weight : int
        총 무게
    total_value : int
        총 가치
    """
    _knapsack_items: list[KnapsackItem] = []
    _cache: dict[tuple[tuple[KnapsackItem, ...], int], list[KnapsackItem]] = {}
    # 아이템 변환
    for _item in items:
        if isinstance(_item, KnapsackItem):
            _knapsack_items.append(_item)
        else:
            if len(_item) == 2:
                # 길이가 2일 경우 가치는 무게와 같다고 간주한다.
                name, weight, value = _item[0], _item[1], _item[1]
            else:
                # 길이가 3인 경우, 가치가 None이면 가치는 무게와 같다고 간주하고 그렇지 않다면 입력된 값을 그대로 사용.
                name, weight, value = _item[0], _item[1], _item[1] if _item[2] is None else _item[2]
            _knapsack_items.append(KnapsackItem(name, weight, value))

    # 문제를 해석한다.
    _solution = _solve(_knapsack_items, max_weight=max_weight, cache_dict=_cache)
    # _total_weight = sum(x.weight for x in _solution)
    _total_weight = get_total_weight(_solution)
    _total_value = get_total_value(_solution, max_weight)
    return _solution, _total_weight, _total_value


def solve_knapsack_0or1_brute(items: Iterable[Union[tuple[T, int, Optional[int]], tuple[T, int]]],
                              max_weight: int) -> tuple[list[KnapsackItem], int, int]:
    """0-1 가방 Brute-Force 방식으로 푼다.

    Parameters
    ----------
    items : Iterable of 2-or-3 Tuples
        항목이 저장된 튜플. 튜플의 길이는 2 혹은 3이어야 한다.
        튜플의 길이가 3일 경우 (항목 이름, 항목의 무게, 항목의 가치)로 해석된다.
        튜플의 길이가 2거나 '항목의 가치'가 None인 경우(즉 가치가 생략된 경우)
        항목의 가치는 항목의 무게와 같다고 간주한다.
    max_weight : int
        무게 제한

    Returns
    -------
    solution : list of KnapsackItem
        0-1 가방 문제의 해. 이름, 무게, 가치가 저장된 항목 객체의 리스트
    total_weight : int
        총 무게
    total_value : int
        총 가치
    """
    _knapsack_items: list[KnapsackItem] = []
    _cache: dict[tuple[tuple[KnapsackItem, ...], int], list[KnapsackItem]] = {}
    # 아이템 변환
    for _item in items:
        if len(_item) == 2:
            # 길이가 2일 경우 가치는 무게와 같다고 간주한다.
            name, weight, value = _item[0], _item[1], _item[1]
        else:
            # 길이가 3인 경우, 가치가 None이면 가치는 무게와 같다고 간주하고 그렇지 않다면 입력된 값을 그대로 사용.
            name, weight, value = _item[0], _item[1], _item[1] if _item[2] is None else _item[2]
        _knapsack_items.append(KnapsackItem(name, weight, value))

    solution = list(max((comb for comb in powerset(_knapsack_items)
                         if sum(item.weight for item in comb) <= max_weight),
                        key=lambda cb: sum(item.value for item in cb)))
    total_weight = sum(item.weight for item in solution)
    total_value = sum(item.weight for item in solution)
    return solution, total_weight, total_value


def get_optimal_knapsacks(items: Iterable[KnapsackItem], target_weight: int,
                          buffer_weight: int) -> Iterator[tuple[list[KnapsackItem], int, int]]:
    """0-1 가방 문제 알고리즘을 사용해서 여러 개의 항목들을 target_weight에 맞춰서 여러 개의 가방에 꽉꽉 채워담는
    최적의 방식을 구한다.

    항목들 중 무게 합이 buffer_weight인 항목들을 우선 추려서 가방에 최대한 꽉꽉 채워담으며, 이 과정에서 가방에 채우지
    못한 항목들은 다음 가방에 우선적으로 채워진다.

    Parameters
    ----------
    items : Iterable of KnapsackItem instances
        가방 항목들
    target_weight : int
        한 가방에 최대한 채울 수 있는 무게
    buffer_weight : int
        가방에 최대한 채우기 위해서 item의 항목들 중 target_weight보다 더 많이 항목들을 뽑는데, 그 무게의 상한선.
        target_weight의 1.25~1.33배 정도로 하는 것이 좋다.

    Yields
    ------
    knapsack_items : list of KnapsackItems
        가방 항목들
    total_knapsack_weight : int
        knapsack_items의 무게 합
    total_knapsack_value : int
        knapsack_items의 가치 합
    """
    # 파일을 수정한 시각 기준으로 오름차순으로 정렬
    items_iterator: Iterator[KnapsackItem] = iter(items)

    # 계산할 때마다 목표 용량과 버퍼 용량이 바뀌므로 값을 복사해 둔다.
    _target_size = target_weight
    _buffer_size = buffer_weight

    pack: list[KnapsackItem] = []  # noqa # 가방 문제로 선정된 항목들
    temp_pack: list[KnapsackItem] = []  # 임시로 _target_size만큼 뽑힌 항목들
    prev_pack: list[KnapsackItem] = []  # 이전 수행에서 Yield되지 못한 항목들
    pack_weight: int = 0  # noqa
    temp_pack_weight: int = 0
    prev_pack_weight: int = 0  # noqa
    # 종료 시그널, 2중 while문을 탈출하기 위해 설정함.
    stop_iteration_signal: bool = False

    while True:
        # 파일을 하나씩 가져옴
        while temp_pack_weight <= _buffer_size:
            try:
                item: KnapsackItem = next(items_iterator)
            except StopIteration:
                # 더 이상 가져올 파일이 없다고 할 경우 이터레이션 종료 시그널 활성화
                stop_iteration_signal = True
                break

            # 가져온 파일을 임시묶음에 저장한다.
            temp_pack.append(item)
            temp_pack_weight += item.weight

        # temp_pack.sort(key=lambda p: p.stat().st_size, reverse=False)
        # '0-1 가방 문제' 알고리즘을 사용해서 최적의 용량만큼 묶는다.
        temp_pack_for_knapsack: list[KnapsackItem] = temp_pack.copy()
        pack_for_knapsack, temp_pack_weight, _ = solve_knapsack_0or1(temp_pack_for_knapsack, _target_size)
        pack = pack_for_knapsack.copy()

        yield prev_pack + pack, get_total_weight(prev_pack + pack), get_total_value(prev_pack + pack, target_weight)

        # 다음 계산을 위해 뽑히지 않은 임시묶음과 임시묶음용량을 이전묶음과 이전묶음용량으로 이동한다.
        # 이전묶음과 이전묶음용량은 최우선적으로 다음에 산출된다.
        prev_pack = [p for p in temp_pack if p not in pack]
        prev_pack_weight = get_total_weight(prev_pack)
        temp_pack.clear()
        temp_pack_weight = 0

        # 목표용량과 버퍼용량 재계산
        _target_size = target_weight - prev_pack_weight
        _buffer_size = buffer_weight - prev_pack_weight

        # 종료시그널 시 루프 빠져나가기
        if stop_iteration_signal:
            break

    # 루프를 빠져나간 다음 남아있는 항목들을 산출하고 종료
    if prev_pack:
        yield prev_pack, get_total_weight(prev_pack), get_total_value(prev_pack, target_weight)
