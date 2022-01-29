"""
브레인퍽(Brainfuck) 언어의 인터프리터

브레인퍽은 난해한 프로그래밍 언어의 일종으로, 8개의 명령어만으로 튜링 완전하다.
"""
from typing import List, Optional

OPCODE_INCR_POINTER = '>'
OPCODE_DECR_POINTER = '<'
OPCODE_INCR_VALUE = '+'
OPCODE_DECR_VALUE = '-'
OPCODE_WRITE = '.'
OPCODE_READ = ','
OPCODE_JUMP_FORWARD = '['
OPCODE_JUMP_BACKWARD = ']'
OPCODES = [OPCODE_INCR_POINTER, OPCODE_DECR_POINTER, OPCODE_INCR_VALUE, OPCODE_DECR_VALUE,
           OPCODE_WRITE, OPCODE_READ, OPCODE_JUMP_FORWARD, OPCODE_JUMP_BACKWARD]


def match_bracket(s: str, loc: int) -> int:
    """열리는(혹은 닫히는) 대괄호에 대응하는 닫히는(혹은 열리는) 대괄호의 위치를 찾는다.

    예시 : s = '[a[b]c[d]e[f[g[h]i[j[k]l]m]n[o]p]q[r]s]'일 때
    loc=10(e와 f 사이) 위치의 열리는 괄호 '['에 대응하는 닫히는 괄호는 위치 32(p와 q 사이)에 있으며
    loc=26(m과 n 사이) 위치의 닫히는 괄호 ']'에 대응하는 열리는 괄호는 위치 12(f와 g 사이)에 있다.

    >>> s = '[a[b]c[d]e[f[g[h]i[j[k]l]m]n[o]p]q[r]s]'
    >>> match_bracket(s, 10)
    32
    >>> match_bracket(s, 26)
    12
    """
    bracket = s[loc]  # 해당 위치에 있는 괄호를 찾는다.
    stack = 0  # 괄호의 중첩 단계. 만약 0인 상태에서 반대 괄호를 찾으면 루프 중단.
    found = False  # 찾았는지 여부
    found_index = None
    if bracket == OPCODE_JUMP_FORWARD:
        index = loc + 1
        while index < len(s):
            c = s[index]
            if c == OPCODE_JUMP_FORWARD:
                stack += 1
            elif c == OPCODE_JUMP_BACKWARD:
                if stack:
                    stack -= 1
                else:
                    found = True
                    found_index = index
                    break
            index += 1
    elif bracket == OPCODE_JUMP_BACKWARD:
        index = loc - 1
        while index >= 0:
            c = s[index]
            if c == OPCODE_JUMP_BACKWARD:
                stack += 1
            elif c == OPCODE_JUMP_FORWARD:
                if stack:
                    stack -= 1
                else:
                    found = True
                    found_index = index
                    break
            index -= 1
    else:
        raise ValueError(f'{bracket} is not a bracket')

    if found:
        return found_index
    else:
        raise ValueError('Cannot find match bracket.')


def preprocess(s: str) -> str:
    """브레인퍽 코드에서 불필요한 부분을 제거한다.
    """
    return ''.join(c for c in s if c in OPCODES)


class BrainfuckInterpreter:
    """브레인퍽 인터프리터

    Properties
    ----------
    code : str
        브레인퍽 코드
    cursor_pos : int : Readonly
        코드를 읽는 커서의 현재 위치
    pointer : int : Readonly
        현재 메모리 포인터
    mem : List of int : Readonly
        메모리

    Methods
    -------
    feed(self, code: str) -> None
        인터프리터에 코드 입력 후 실행
    iterate_machine(self) -> None
        입력된 코드 실행
    """

    # ==========Initializer==========
    def __init__(self, memsize: int = 32768, code: Optional[str] = None,
                 use_null_terminated_str: bool = True):
        """브레인퍽 인터프리터를 초기화한다.

        Parameters
        ----------
        memsize : int
            메모리 크기(기본값은 32KB)
        code : str : Optional
            브레인퍽 코드
        use_null_terminated_str : bool
            입력받는 문자의 끝에 NULL 문자를 추가할 지 여부. 기본값은 True
        """
        self._code: Optional[str] = preprocess(code)  # 명령어(.,[]<>+-)
        self._cursor_pos: int = 0  # 명령어를 읽는 커서
        self._pointer: int = 0  # 메모리 포인터
        self._mem: List[int] = [0] * memsize  # 메모리
        self._read_buffer: str = ''  # 읽기 버퍼
        self._use_null_terminated_str: bool = use_null_terminated_str  # 문자열 끝에 NULL 문자를 추가할 지 여부

    # ==========Properties==========
    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str):
        self._code = value

    @property
    def cursor_pos(self) -> int:
        return self._cursor_pos

    @property
    def pointer(self) -> int:
        return self._pointer

    @property
    def mem(self) -> List[int]:
        return self._mem

    # ==========Public Methods==========
    def feed(self, code: str):
        """코드를 입력 후 실행한다.

        Parameters
        ----------
        code : str
            코드 내용
        """
        self._code = preprocess(code)
        self.run()

    def run(self):
        """현재 코드를 실행한다.
        """
        while self._cursor_pos < len(self._code):
            opcode = self._code[self._cursor_pos]
            if opcode == OPCODE_INCR_VALUE:
                self._increase_value()
            elif opcode == OPCODE_DECR_VALUE:
                self._decrease_value()
            elif opcode == OPCODE_INCR_POINTER:
                self._increase_pointer()
            elif opcode == OPCODE_DECR_POINTER:
                self._decrease_pointer()
            elif opcode == OPCODE_WRITE:
                self._write()
            elif opcode == OPCODE_READ:
                self._read()
            elif opcode == OPCODE_JUMP_FORWARD:
                self._jump_forward_if_zero()
            elif opcode == OPCODE_JUMP_BACKWARD:
                self._jump_backward_if_nonzero()
            self._cursor_pos += 1

    # ==========Protected Methods==========
    def _increase_pointer(self):
        # 포인터 증가
        self._pointer += 1

    def _decrease_pointer(self):
        # 포인터 감소
        self._pointer -= 1

    def _increase_value(self):
        # 포인터가 가리키는 값 증가
        self._mem[self._pointer] += 1

    def _decrease_value(self):
        # 포인터가 가리키는 값 감소
        self._mem[self._pointer] -= 1

    def _write(self):
        # 포인터의 값을 문자로 출력
        print(chr(self._mem[self._pointer]), end='')

    def _read(self):
        # 문자를 입력해서 그 아스키 코드를 포인터에 저장
        # 만약 여러개의 문자를 입력받으면 버퍼에 저장되서 다음 OPCODE_READ이 실행될 때 자동으로 실행된다.
        if not self._read_buffer:
            input_str = input('\n>>> ')
            if self._use_null_terminated_str:
                input_str += '\x00'
            self._read_buffer = input_str
        self._mem[self._pointer] = ord(self._read_buffer[0])
        self._read_buffer = self._read_buffer[1:]

    def _jump_forward_if_zero(self):
        # 포인터의 값이 0이면 짝이 맞는 ']'로 이동
        if not self._mem[self._pointer]:
            oldpos = self._cursor_pos
            self._cursor_pos = match_bracket(self._code, oldpos)

    def _jump_backward_if_nonzero(self):
        # 포인터의 값이 0이 아니면 짝이 맞는 '['로 이동
        if self._mem[self._pointer]:
            oldpos = self._cursor_pos
            self._cursor_pos = match_bracket(self._code, oldpos)


if __name__ == '__main__':
    with open('./res/brainfuck_rot13.txt', 'r', encoding='utf-8') as f:
        bf_code = f.read()
    bf = BrainfuckInterpreter(code=bf_code, use_null_terminated_str=True)
    bf.run()
    