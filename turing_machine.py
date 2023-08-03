#!/usr/bin/env python
import time
from collections import deque
from enum import IntEnum
from typing import Deque, Iterator, List, NamedTuple, Optional, Sequence, Tuple


class HeadMoveDirection(IntEnum):
    LEFT = -1
    STAY = 0
    RIGHT = 1


class TuringMachineRule(NamedTuple):
    current_state: str  # 현재 헤드의 상태
    current_symbol: int  # 현재 헤드가 읽는 기호
    next_symbol: int  # 현재 상태와 기호를 읽었을 때 현재 헤드 위치에 쓸 기호
    head_move_direction: HeadMoveDirection  # 현재 상태와 기호에 따라 헤드 이동 방향
    next_state: str  # 변경할 헤드 상태


class TuringMachineResult(NamedTuple):
    tape: Deque[int]
    current_pos: int
    current_state: str
    tape_span: Tuple[int, int]


class TuringMachine:
    def __init__(
        self,
        rules: List[TuringMachineRule],
        start_state: str,
        initial_tape: Optional[Sequence[int]] = None,
        initial_pos: int = 0,
        halt_state: str = "H",
        blank_symbol: int = 0,
    ):
        """튜링 머신을 정의한다.

        :param rules: 튜링 머신의 규칙
        :param start_state: 튜링 머신의 헤드 시작 상태
        :param initial_tape: 시작 시 테이프 상태
        :param initial_pos: 시작 시 헤드의 위치
        :param halt_state: 튜링 머신이 정지할 상태
        :param blank_symbol: 비어 있는 기호로 정의할 값
        """
        self._rules: List[TuringMachineRule] = rules
        self._head_state: str = start_state
        self._blank_symbol: int = blank_symbol
        if initial_tape:
            self._tape: Deque[int] = deque(initial_tape)
        else:
            self._tape: Deque[int] = deque([blank_symbol])
        self._head_pos: int = initial_pos
        self._halt_state = halt_state
        self._tape_span: Tuple[int, int] = (0, len(self._tape))
        self._initial_tape_span: Tuple[int, int] = (0, len(self._tape))

    # getter와 setter 정의
    @property
    def rules(self) -> List[TuringMachineRule]:
        """튜링 머신의 규칙
        읽기 전용
        """
        return self._rules

    @property
    def head_state(self) -> str:
        """헤드의 상태"""
        return self._head_state

    @head_state.setter
    def head_state(self, value: str):
        """헤드의 상태를 변경한다."""
        self._head_state = value

    @property
    def tape(self) -> Deque[int]:
        """현재 테이프의 복사본 반환"""
        return self._tape.copy()

    @property
    def tape_span(self) -> Tuple[int, int]:
        """현재 테이프가 초기 테이프보다 얼만큼 연장되었는지 반환
        읽기 전용

        예를 들어 초기 tape_span이 (0, 3)이었는데 (-3, 4)로 변경되었다면
        왼쪽으로 3칸, 오른쪽으로 1칸 연장되었다는 것을 의미한다.
        """
        return self._tape_span

    @property
    def initial_tape_span(self) -> Tuple[int, int]:
        """초기 테이프 스팬
        읽기 전용
        """
        return self._initial_tape_span

    @property
    def halt_state(self) -> str:
        """튜링 머신의 '정지'를 나타낼 상태
        읽기 전용
        """
        return self._halt_state

    @property
    def head_pos(self) -> int:
        """헤드의 절대 위치(초기 위치에서 왼쪽이면 음수, 오른쪽이면 양수)
        읽기 전용
        """
        return self._head_pos

    @property
    def relative_head_pos(self) -> int:
        """테이프의 왼쪽 끝에서 헤드의 위치
        테이프의 값을 조회하거나 수정할 때는 이 값을 써야 한다.
        읽기 전용
        """
        return self._head_pos - self._tape_span[0]

    @property
    def blank_symbol(self):
        """비어 있는 기호로 정의되는 값
        읽기 전용
        """
        return self._blank_symbol

    def lookup_rule(self, state, symbol) -> Tuple[int, HeadMoveDirection, str]:
        """튜링 머신의 규칙에서 현재 상태와 기호에 해당되는 다음 기호와 헤드 이동 방향, 상태를 반환한다.

        :param state: 현재 상태
        :param symbol: 현재 기호
        :return: (다음 기호, 헤드가 이동할 방향, 다음 상태)
        """
        for rule in self._rules:
            if rule.current_state == state and rule.current_symbol == symbol:
                return rule.next_symbol, rule.head_move_direction, rule.next_state

        raise ValueError(f"Cannot find {state=} and {symbol=} in rule table.")

    def move_head_to_left(self):
        """헤드를 왼쪽으로 한 칸 옮긴다.
        필요 시 테이프를 연장한다.
        """
        self._head_pos -= 1  # 왼쪽으로 한 칸 움직이기
        if self._head_pos < self._tape_span[0]:
            # 헤드가 테이프의 왼쪽 끝을 넘어갔다면
            self._tape.appendleft(self._blank_symbol)  # 테이프를 왼쪽으로 한 칸 연장한다.
            self._tape_span = self._tape_span[0] - 1, self._tape_span[1]  # tape_span 업데이트

    def move_head_to_right(self):
        """헤드를 오른쪽으로 한 칸 옮긴다.
        필요 시 테이프를 연장한다.
        """
        self._head_pos += 1  # 오른쪽으로 한 칸 움직이기
        if self._head_pos >= self._tape_span[1]:
            # 헤드가 테이프 오른쪽 끝을 초과했다면
            self._tape.append(self._blank_symbol)  # 테이프를 오른쪽으로 한 칸 연장한다.
            self._tape_span = self._tape_span[0], self._tape_span[1] + 1  # tape_span 업데이트

    def read_tape(self) -> int:
        """현재 헤드 위치에 있는 테이프 기호를 읽는다."""
        return self._tape[self.relative_head_pos]

    def write_tape(self, sym: int):
        """현재 헤드 위치에 기호를 쓴다."""
        self._tape[self.relative_head_pos] = sym

    def iterate_machine(self) -> Iterator[TuringMachineResult]:
        """튜링 머신이 *정지할 때까지* 작동시킨다."""
        yield TuringMachineResult(self.tape, self.head_pos, self.head_state, self.tape_span)

        while self.head_state != self.halt_state:
            current_state, current_symbol = self.head_state, self.read_tape()
            # 룰을 읽는다.
            next_symbol, head_moving_direction, next_state = self.lookup_rule(current_state, current_symbol)

            # 기호를 쓴다.
            self.write_tape(next_symbol)

            # 헤드를 움직인다.
            if head_moving_direction == HeadMoveDirection.LEFT:
                self.move_head_to_left()
            elif head_moving_direction == HeadMoveDirection.RIGHT:
                self.move_head_to_right()

            # 상태를 변경한다.
            self.head_state = next_state

            yield TuringMachineResult(self.tape, self.head_pos, self.head_state, self.tape_span)


def pretty_print_result(results: List[TuringMachineResult], blank_symbol=0) -> None:
    """이 함수는 튜링 머신의 실행 결과를 출력할 때 쓴다."""
    final_span = results[-1].tape_span
    for i, result in enumerate(results):
        # 테이프의 길이를 똑같이 맞춘다.
        extended_tape = (
            [blank_symbol] * (result.tape_span[0] - final_span[0])
            + list(result.tape)
            + [blank_symbol] * (final_span[1] - result.tape_span[1])
        )
        relative_head_pos = result.current_pos - final_span[0]
        print(f"{i:>3d} {result.current_state}   {apply_bracket_to_pos(extended_tape, relative_head_pos)}")


def apply_bracket_to_pos(items: List[int], pos: int) -> str:
    items_span: List[str] = [str(x) for x in items] + [" "]
    bracket_list: List[str] = [" "] * pos + ["[", "]"] + [" "] * (len(items) - pos - 1)
    return "".join("".join(pair) for pair in zip(bracket_list, items_span))


if __name__ == "__main__":
    # 3-State 2-Symbol busy beaver
    bb4_rules = [
        TuringMachineRule("A", 0, 1, HeadMoveDirection.RIGHT, "B"),
        TuringMachineRule("A", 1, 1, HeadMoveDirection.LEFT, "B"),
        TuringMachineRule("B", 0, 1, HeadMoveDirection.LEFT, "A"),
        TuringMachineRule("B", 1, 0, HeadMoveDirection.LEFT, "C"),
        TuringMachineRule("C", 0, 1, HeadMoveDirection.RIGHT, "H"),
        TuringMachineRule("C", 1, 1, HeadMoveDirection.LEFT, "D"),
        TuringMachineRule("D", 0, 1, HeadMoveDirection.RIGHT, "D"),
        TuringMachineRule("D", 1, 0, HeadMoveDirection.RIGHT, "A"),
    ]

    # 5-State 2-Symbol busy beaver(현재까지 알려진 가장 유력한 바쁜 비버 후보)
    bb5_rules = [
        TuringMachineRule("A", 0, 1, HeadMoveDirection.RIGHT, "B"),
        TuringMachineRule("A", 1, 1, HeadMoveDirection.LEFT, "C"),
        TuringMachineRule("B", 0, 1, HeadMoveDirection.RIGHT, "C"),
        TuringMachineRule("B", 1, 1, HeadMoveDirection.RIGHT, "B"),
        TuringMachineRule("C", 0, 1, HeadMoveDirection.RIGHT, "D"),
        TuringMachineRule("C", 1, 0, HeadMoveDirection.LEFT, "E"),
        TuringMachineRule("D", 0, 1, HeadMoveDirection.LEFT, "A"),
        TuringMachineRule("D", 1, 1, HeadMoveDirection.LEFT, "D"),
        TuringMachineRule("E", 0, 1, HeadMoveDirection.RIGHT, "H"),
        TuringMachineRule("E", 1, 0, HeadMoveDirection.LEFT, "A"),
    ]
    tm = TuringMachine(bb4_rules, start_state="A")
    time_start = time.time()
    steps = 0
    busy_beaver = 0
    for tm_step, tm_result in enumerate(tm.iterate_machine()):
        steps = tm_step
        if (count_1s := sum(tm_result.tape)) > busy_beaver:
            busy_beaver = count_1s

    time_end = time.time()
    print(f"Elapsed Time: {time_end - time_start} seconds")
    print(f"Maximum 1s: {busy_beaver}")
    print(f"TM Halted after {steps} steps")
