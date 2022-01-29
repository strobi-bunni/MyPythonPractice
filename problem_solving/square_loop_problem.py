r"""
문제
----

[그림 1]

::

    /--23--26--10--15---1---8--28--21---4--32--17--19--30---6---3--13--\
    |                                                                  |
    \---2--14--22--27---9--16--20--29---7--18--31---5--11--25--24--12--/

다음 그림은 1부터 32까지의 자연수를 중복 없이 원형으로 쓴 것으로, 인접한 두 수의 합은 제곱수가 된다.

::

    4 + 32 == 36 == 6 ** 2
    32 + 17 == 49 == 7 ** 2
    17 + 19 == 36 == 6 ** 2
    19 + 30 == 49 == 7 ** 2
    ...
    21 + 4 == 25 == 5 ** 2

32 이상의 자연수 n이 주어졌을 때 1부터 n까지의 수를 원형으로 배치해서
인접한 수의 합이 제곱수가 되는 경우의 수는 다음과 같다.
(OEIS: `A071984`_)

.. _`A071984`: https://oeis.org/A071984

::

    n       32  33  34  35  36  37  38  ...
    cases   1   1   11  57  31  20  25  ...

32 이상의 자연수 n이 주어졌을 때 중복되지 않은(즉, 회전시키거나 뒤집었을 때 같은 순서가 되지 않는)
모든 경우를 구하여라.
"""
from functools import cmp_to_key
from itertools import count, filterfalse
from typing import Iterator, List


def is_square(n: int) -> bool:
    """자연수 n이 제곱수인지 여부
    """
    returns = False
    for x in count():
        if (x_sq := x ** 2) > n:
            break
        elif x_sq == n:
            returns = True
            break

    return returns


def unique_everseen(iterable, key=None):
    """List unique elements, preserving order. Remember all elements ever seen.

    코드 출처 : https://docs.python.org/3/library/itertools.html?highlight=itertools

    참고 : 컨테이너를 set에서 list로 바꿈"""
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = []
    seen_add = seen.append
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def _get_circle(preselected: List[int], pool: List[int]) -> Iterator[List[int]]:
    # preselected : 이어가고 있는 원 조각
    # pool : 남은 숫자들

    # preselected이 없으면(아직 시작을 안 하면) pool에서 맨 처음 것을 꺼내서 시작한다.
    # 원형이니까 어느 쪽에서 시작해도 결과는 같다.
    if not preselected:
        pool_head, *pool_tail = pool
        yield from _get_circle([pool_head], pool_tail)

    # 종료 조건 : pool이 비어 있다면(원을 완성했다면) 원의 양 끝점을 이었을 때 제곱수가 되었는지 확인하고
    # 만약 제곱수가 되었다면 산출한다.
    elif not pool:
        if is_square(preselected[0] + preselected[-1]):
            yield preselected

    # 재귀 조건 : pool에서 하나를 뽑아서(그 값을 pool_value로 한다) preselected의 마지막 항목과 더했을때 제곱수가 되면
    # preselected의 항목에 pool_value을 추가한 리스트를 새 preselected로,
    # pool에서 pool_value을 제외한 리스트를 새 pool로 간주하고 재귀한다.
    else:
        for pool_index, pool_value in enumerate(pool):
            if is_square(preselected[-1] + pool_value):
                pool_copy = pool.copy()
                pool_copy.pop(pool_index)
                yield from _get_circle(preselected + [pool_value], pool_copy)


def get_circle(n: int) -> Iterator[List[int]]:
    yield from _get_circle([], list(range(1, n + 1)))


def circular_shift_list(lst: List[int], n: int) -> List[int]:
    """리스트를 오프셋 n만큼 순환 시프트한다.

    n이 양수이면 왼쪽으로 시프트하고 음수면 오른쪽으로 시프트한다.

    >>>  circular_shift_list([1, 2, 3, 4], 1)
    [2, 3, 4, 1]
    >>>  circular_shift_list([1, 2, 3, 4], -1)
    [4, 1, 2, 3]
    """
    return lst[n:] + lst[:n]


def _is_same_circle(l1: List[int], l2: List[int]) -> bool:
    """l1과 l2가 똑같은 원인지 확인
    옆으로 움직였을 때 같으면 is_same_circle(l1, l2)==True이다.
    뒤집었을 때 결과는 고려하지 않는다.
    """
    returns = False
    for offset in range(len(l1)):
        if circular_shift_list(l1, offset) == l2:
            returns = True
    return returns


def is_same_circle_cmp(l1: List[int], l2: List[int]) -> int:
    """l1과 l2가 똑같은 원인지 확인
    옆으로 움직이거나(shift) 뒤집어도(filp) 같으면 is_same_circle(l1, l2)==0이고 다르면 -1을 반환한다.

    결과값이 int인 이유는 cmp_to_key를 쓰기 위해서이다.
    """
    if _is_same_circle(l1, l2) or _is_same_circle(l1[::-1], l2):
        return 0
    else:
        return -1


# 다음은 n=34일때, 회전시키거나 뒤집는 경우를 제외한 중복되지 않은 모든 경우의 수를 구한다.
for item in unique_everseen(get_circle(34), cmp_to_key(is_same_circle_cmp)):
    print(item)
