#!/usr/bin/env python
r"""
n-퀸 문제(n-queens problem)

n×n 체스판에 n개의 퀸을 배치할 때, 서로가 서로를 위협하지 못하게 하는 배치 방법

각각의 체스판 크기에 대한 경우의 수는 다음과 같다:

::

    size            1  2  3  4  5   6  7   8   9    10   ...
    cases           1  0  0  2  10  4  40  92  352  724  ...
    distinct_cases  1  0  0  1  2   1  6   12  46   92   ...

- 경우의 수: OEIS:`A000170`_
- 뒤집거나 돌려서 같은 항목을 하나로 봤을 때 경우의 수: OEIS:`A002562`_

.. _`A000170` : https://oeis.org/A000170
.. _`A002562` : https://oeis.org/A002562
"""
import math
from collections.abc import Iterator, Sequence
from functools import cmp_to_key
from itertools import filterfalse, zip_longest
from typing import TypeVar

T = TypeVar('T')


def find_diagonal_line_bottom_right(loc: int, size: int) -> int:
    row, col = divmod(loc, size)
    return row - col


def find_diagonal_line_bottom_left(loc: int, size: int) -> int:
    row, col = divmod(loc, size)
    return row + col


def find_threat_area(loc: int, size: int) -> list[int]:
    """위치 loc에 퀸을 배치할 경우 퀸의 위협을 받는 영역을 표시한다.
    """
    return [int((loc % size == p % size) | (loc // size == p // size)
                | (find_diagonal_line_bottom_right(loc, size) == find_diagonal_line_bottom_right(p, size))
                | (find_diagonal_line_bottom_left(loc, size) == find_diagonal_line_bottom_left(p, size)))
            for p in range(size * size)]


def count_queens(board: list[int]) -> int:
    """체스판 위의 퀸의 갯수를 센다.
    """
    return sum(filter(bool, board))


def _solve_n_queens(board: list[int], threats: list[int], size: int) -> Iterator[list[int]]:
    queens = count_queens(board)
    if queens == size:
        # 종료 조건: n*n 크기 체스판에 n개의 퀸을 올려놓았을 경우
        yield board
    else:
        # 위협받지 않는 다음 자리를 찾는다.
        next_possible_queen_locations = [p for p in range(queens * size, (queens + 1) * size) if not threats[p]]
        for next_possible_queen_location in next_possible_queen_locations:
            new_board = board.copy()

            # 다음 자리에 퀸을 올려놓고 위험 지역을 업데이트한다.
            new_board[next_possible_queen_location] = 1
            new_threats = [th | new_th for (th, new_th)
                           in zip(threats, find_threat_area(next_possible_queen_location, size))]
            yield from _solve_n_queens(new_board, new_threats, size)


def solve_n_queens(size: int) -> Iterator[list[int]]:
    board = [0 for _ in range(size * size)]
    threats = [0 for _ in range(size * size)]
    yield from _solve_n_queens(board, threats, size)


def grouper(iterable, n, *, incomplete='fill', fillvalue=None):
    """Collect data into non-overlapping fixed-length chunks or blocks

    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    if incomplete == 'fill':
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == 'strict':
        return zip(*args, strict=True)
    if incomplete == 'ignore':
        return zip(*args)
    else:
        raise ValueError('Expected fill, strict, or ignore')


def print_board(board: list[int], size: int) -> None:
    row_str = []
    for row in grouper(board, size):
        row_str.append(''.join(('\uff31' if c else '\uff0e') for c in row))
    print('\n'.join(row_str))
    print()


def reorder(seq: Sequence[T], order: Sequence[int]) -> list[T]:
    if len(seq) != len(order):
        raise IndexError
    return [seq[i] for i in order]


def is_same_square_array(seq: Sequence[T], seq2: Sequence[T]) -> int:
    size = math.isqrt(len(seq))
    if (
            seq == seq2 or
            (seq == reorder(seq2, [i * size + j for i in range(size - 1, -1, -1) for j in range(size)])) or
            (seq == reorder(seq2, [i * size + j for i in range(size) for j in range(size - 1, -1, -1)])) or
            (seq == reorder(seq2, [i * size + j for i in range(size - 1, -1, -1) for j in range(size - 1, -1, -1)])) or
            (seq == reorder(seq2, [j * size + i for i in range(size) for j in range(size)])) or
            (seq == reorder(seq2, [j * size + i for i in range(size - 1, -1, -1) for j in range(size)])) or
            (seq == reorder(seq2, [j * size + i for i in range(size) for j in range(size - 1, -1, -1)])) or
            (seq == reorder(seq2, [j * size + i for i in range(size - 1, -1, -1) for j in range(size - 1, -1, -1)]))
    ):
        return 0
    else:
        return -1


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


if __name__ == '__main__':
    board_size = 8
    num_of_solutions = 0
    nqueens = solve_n_queens(board_size)  # 모든 경우의 수(뒤집거나 회전시키는 것을 다른 것으로 볼 때: A000170)
    unique_nqueens = unique_everseen(nqueens, cmp_to_key(is_same_square_array))  # 중복없는 경우의 수(A002562)
    for solution in unique_nqueens:
        num_of_solutions += 1
        print_board(solution, board_size)
    print(f'{num_of_solutions} unique solutions')
