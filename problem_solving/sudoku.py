#!/usr/bin/env python
"""
백트래킹을 이용한 간단한 스도쿠 풀이기
"""
from collections.abc import Iterator
from itertools import compress, zip_longest


def find_first_empty_index(board: list[int]) -> int:
    """첫 비어 있는 칸을 찾는다. 비어 있는 칸이 없다면 -1를 반환한다.
    """
    for (i, v) in enumerate(board):
        if v == 0:
            return i
    return -1


def find_matching_tile(i: int) -> list[int]:
    """해당 칸에 매칭되는 블록들을 1로 표시한다.

    - 같은 가로줄에 있거나
    - 같은 세로줄에 있거나
    - 혹은 같은 3x3 블록에 있거나
    """
    return [int((p % 9 == i % 9) | (p // 9 == i // 9) | ((p % 9 // 3 == i % 9 // 3) & (p // 27 == i // 27)))
            for p in range(81)]


def solve_sudoku(board: list[int]) -> Iterator[list[int]]:
    """스도쿠 풀이. 단순한 백트래킹 방식이다.
    """
    if (first_empty_index := find_first_empty_index(board)) == -1:
        # 종료 조건: 이미 채워진 보드
        yield board
    else:
        # 백트래킹 방법을 사용한다. 첫 비워진 칸에 올 수 있는 숫자를 찾아내서 재귀 함수로 풀어낸다.
        forbidden_numbers = set(compress(board, find_matching_tile(first_empty_index)))
        allowed_numbers = set(range(1, 10)) - forbidden_numbers
        for allowed_number in allowed_numbers:
            new_board = board.copy()
            new_board[first_empty_index] = allowed_number
            yield from solve_sudoku(new_board)


def get_candidate_map(board: list[int]) -> list[set[int]]:
    """각 칸에 올 수 있는 후보 숫자를 선정한다.
    """
    return [set(range(1, 10))
            - set(compress(board, find_matching_tile(i))) if v == 0 else set()
            for (i, v) in enumerate(board)]


def get_candidate_map2(board: list[int]) -> list[set[int]]:
    """각 칸에 올 수 있는 후보 숫자를 선정한다.

    get_candidate_map과 별 차이는 없는 듯 하다.
    """
    candidates = [set(range(1, 10)) for _ in range(81)]
    for (index_board, value_board) in enumerate(board):
        if value_board:
            # 만약 해당 칸에 숫자가 있다면 같은 가로줄, 세로줄, 블록의 해당 후보 숫자들을 지운다.
            matching_tiles = find_matching_tile(index_board)
            for (index_matching, value_matching) in enumerate(matching_tiles):
                if value_matching and index_matching != index_board:
                    candidates[index_matching] -= {board[index_board]}
            # 해당 칸에 숫자가 있다면 해당 칸은 더 이상 숫자가 들어갈 수 없기 때문에 비운다.
            candidates[index_board].clear()
        else:
            # 만약 해당 칸에 숫자가 없다면 같은 가로줄, 세로줄, 블록을 스캔해서 후보 숫자들을 지운다.
            candidates[index_board] -= set(compress(board, find_matching_tile(index_board)))
    return candidates


def narrow(board: list[int]) -> list[int]:
    """백트래킹 방법을 사용하기 전, 채울 수 있는 칸은 모두 채운다.
    """
    board_copy = board.copy()

    while True:
        old_board = board_copy.copy()
        candidates = get_candidate_map2(board_copy)
        for (i, v) in enumerate(candidates):
            # 만약에 하나만 올 수 있다면 그것을 채워 넣는다(Sole candidate)
            if len(v) == 1:
                board_copy[i] = v.pop()
        # 더 이상 채워 넣을 수 없다면 루프를 빠져나간다.
        if old_board == board_copy:
            break
    return board_copy


def solve_sudoku2(board: list[int]) -> Iterator[list[int]]:
    """스도쿠 풀이 2. 사전에 채울 수 있는 항목은 모두 채우고 시작한다.
    """
    narrowed_board = narrow(board)
    yield from solve_sudoku(narrowed_board)


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


# 몇 가지 문제들:
# 빈 칸은 0으로 표시한다.
# 000300200000008000078060340042510000106000409000086150035090760000700000009005000(쉬움)
# 040000000001034620603000070000483507000050060000009040005000001800547396000021000(보통)
# 000801000000000043500000000000070800000000100020030000600000075003400000000200600(어려움, 5-10분 정도 걸림)

sudoku_board = '''
530 070 000
600 195 000
098 000 060

800 060 003
400 803 001
700 020 006

060 000 280
000 419 005
000 080 079
'''
sudoku = [int(x) for x in sudoku_board if x.isdigit()]
# solve_sudoku : 단순 백트래킹 / solve_sudoku2 : 백트래킹 전 채울 수 있는 칸은 모두 채우고 시작
for solution in solve_sudoku2(sudoku):
    for row in grouper(solution, 9):
        print(row)
    print()  # 빈 줄
