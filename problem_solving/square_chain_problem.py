#!/usr/bin/env python
r"""
문제
----

[그림 1]

::

    8--1--15--10--6--3--13--12--4--5--11--14--2--7--9

다음은 1부터 15까지의 자연수를 중복 없이 일렬로 쓴 것으로, 인접한 두 수의 합은 제곱수가 된다.

::

    8  + 1  == 9  == 3 ** 2
    1  + 15 == 16 == 4 ** 2
    15 + 10 == 25 == 5 ** 2
    ...
    7  + 9  == 16 == 4 ** 2

15 이상의 자연수 n이 주어졌을 때 1부터 n까지의 수를 일렬로 배치해서 인접한 수의 합이 제곱수가 되는 경우의 수는 다음과 같다.
(OEIS: `A071983`_)

.. _`A071983`: https://oeis.org/A071983

::

    n       15  16  17  18  19  20  21  22  23  24  25  26  27  ...
    cases   1   1   1   0   0   0   0   0   3   0   10  12  35  ...

15 이상의 자연수 n이 주어졌을 때 중복되지 않은(즉, 뒤집었을 때 같은 순서가 되지 않는) 모든 경우를 구하여라.
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


def _get_sequence(preselected: List[int], pool: List[int]) -> Iterator[List[int]]:
    # preselected : 이어가고 있는 시퀀스 조각
    # pool : 남은 숫자들

    # preselected이 없으면(아직 시작을 안 하면) pool에서 차례대로 항목을 꺼내 시작한다.
    if not preselected:
        for pool_head in pool:
            pool_tail = [p for p in pool if p != pool_head]
            yield from _get_sequence([pool_head], pool_tail)

    # 종료 조건 : pool이 비어 있다면(시퀀스를 완성했다면) 산출한다.
    elif not pool:
        yield preselected

    # 재귀 조건 : pool에서 하나를 뽑아서(그 값을 pool_value로 한다) preselected의 마지막 항목과 더했을때 제곱수가 되면
    # preselected의 항목에 pool_value을 추가한 리스트를 새 preselected로,
    # pool에서 pool_value을 제외한 리스트를 새 pool로 간주하고 재귀한다.
    else:
        for pool_index, pool_value in enumerate(pool):
            if is_square(preselected[-1] + pool_value):
                pool_copy = pool.copy()
                pool_copy.pop(pool_index)
                yield from _get_sequence(preselected + [pool_value], pool_copy)


def get_sequence(n: int) -> Iterator[List[int]]:
    yield from _get_sequence([], list(range(1, n + 1)))


def is_same_sequence_cmp(l1: List[int], l2: List[int]) -> int:
    """l1과 l2가 똑같은 시퀀스인지 확인
    뒤집어도(filp) 같으면 is_same_sequence_cmp(l1, l2)==0이고 다르면 -1을 반환한다.

    결과값이 int인 이유는 cmp_to_key를 쓰기 위해서이다.
    """
    if l1 == l2 or l1 == l2[::-1]:
        return 0
    else:
        return -1


# 다음은 n=23일때, 뒤집는 경우를 제외한 중복되지 않은 모든 경우의 수를 구한다.
for item in unique_everseen(get_sequence(23), cmp_to_key(is_same_sequence_cmp)):
    print(item)
