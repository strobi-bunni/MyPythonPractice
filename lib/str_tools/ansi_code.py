from enum import IntEnum
from typing import Optional, Tuple, Union

CODE_TEMPLATE = "\x1b[{0}m"
CODE_FGCOLOR_256_TEMPLATE = "\x1b[38;5;{0}m"
CODE_FGCOLOR_24BIT_TEMPLATE = "\x1b[38;2;{0};{1};{2}m"
CODE_BGCOLOR_256_TEMPLATE = "\x1b[48;5;{0}m"
CODE_BGCOLOR_24BIT_TEMPLATE = "\x1b[48;2;{0};{1};{2}m"

CODE_RESET = 0
CODE_BOLD = 1
CODE_BOLD_OFF_AND_DOUBLE_ITALIC = 21
CODE_FAINT = 2
CODE_ITALIC = 3
CODE_ITALIC_IFF = 23
CODE_UNDERLINE = 4
CODE_UNDERLINE_OFF = 24
CODE_BLINK = 5
CODE_BLINK_OFF = 25
CODE_INVERT = 7
CODE_INVERT_OFF = 27
CODE_HIDE = 8
CODE_HIDE_OFF = 28
CODE_CROSSED_OUT = 9
CODE_CROSSED_OUT_OFF = 29
CODE_RESET_FOREGROUND_COLOR = 39
CODE_RESET_BACKGROUND_COLOR = 49


# Color Preset
class BasicColor(IntEnum):
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    GRAY = 8
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_WHITE = 15


def _fgcolor_code(value: Optional[int] = None, *values: int) -> str:
    if value is None:
        # Reset foreground color
        return CODE_TEMPLATE.format(CODE_RESET_FOREGROUND_COLOR)
    if len(values) == 0:
        if 0 <= value < 8:
            # Dark color
            return CODE_TEMPLATE.format(value + 30)
        elif 8 <= value < 16:
            # Bright color
            return CODE_TEMPLATE.format(value + 82)
        elif 16 <= value < 256:
            # 256-color
            return CODE_FGCOLOR_256_TEMPLATE.format(value)
        else:
            raise ValueError("Color value must be an integer greater than 0 and less than 256.")
    elif len(values) == 2:
        rgb_codes = (value, *values)
        if any((x < 0 or x >= 256) for x in rgb_codes):
            raise ValueError("Color value must be an integer greater than 0 and less than 256.")
        else:
            # 24-bit color
            return CODE_FGCOLOR_24BIT_TEMPLATE.format(*rgb_codes)
    else:
        raise ValueError("Input value must be one(16color or 256color) or three(24-bit color) integers.")


def _bgcolor_code(value: Optional[int] = None, *values: int) -> str:
    if value is None:
        # Reset foreground color
        return CODE_TEMPLATE.format(CODE_RESET_BACKGROUND_COLOR)
    if len(values) == 0:
        if 0 <= value < 8:
            # Dark color
            return CODE_TEMPLATE.format(value + 40)
        elif 8 <= value < 16:
            # Bright color
            return CODE_TEMPLATE.format(value + 92)
        elif 16 <= value < 256:
            # 256-color
            return CODE_BGCOLOR_256_TEMPLATE.format(value)
        else:
            raise ValueError("Color value must be an integer greater than 0 and less than 256.")
    elif len(values) == 2:
        rgb_codes = (value, *values)
        if any((x < 0 or x >= 256) for x in rgb_codes):
            raise ValueError("Color value must be an integer greater than 0 and less than 256.")
        else:
            # 24-bit color
            return CODE_BGCOLOR_24BIT_TEMPLATE.format(*rgb_codes)
    else:
        raise ValueError("Input value must be one(16color or 256color) or three(24-bit color) integers.")


def set_fgcolor(
    text: str = "", color: Union[int, Tuple[int, int, int], None] = None, *, reset=False, reset_color=False
) -> str:
    """글자의 색을 설정한다. 경우에 따라서 동시에 출력할 수 있다.

    Parameters
    ----------
    text : str : Optional
        출력할 텍스트
    color : int or 3-Tuple of ints
        색상. 숫자 1개를 입력하면 표준 16색/256색을 사용하며, 숫자 3개의 튜플을 사용하면 24비트 색상을 사용한다.
    reset : bool : Optional
        텍스트 출력 후 전부 리셋할지 여부. text 인자가 있어야 유효하다.
    reset_color : bool : Optional
        텍스트 출력 후 색상을 리셋할지 여부

    Notes
    -----
    색상 값은 다음을 참고한다.

    https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

    여기서 16색은 256color의 맨 앞 0~15번 색 코드를 사용한다.

    Examples
    --------
    글자 색을 밝은 빨강으로 바꾸기

    >>> print(set_fgcolor(color=9))

    글자 색을 256색 중 42번 색상으로 바꾸기

    >>> print(set_fgcolor(color=42))

    글자 색을 RGB(255, 128, 192)로 바꾸기

    >>> print(set_fgcolor(color=(255, 128, 192)))

    밝은 파란색 'Hello World' 출력

    >>> print(set_fgcolor('Hello World', 12, reset=True))
    """
    color_code = _fgcolor_code(color) if color is None or isinstance(color, int) else _fgcolor_code(*color)
    reset_code = (
        CODE_TEMPLATE.format(CODE_RESET)
        if reset
        else CODE_TEMPLATE.format(CODE_RESET_FOREGROUND_COLOR)
        if reset_color
        else ""
    )
    return color_code + text + reset_code


def set_bgcolor(
    text: str = "", color: Union[int, Tuple[int, int, int], None] = None, *, reset=False, reset_color=False
) -> str:
    """글자 배경의 색을 설정한다. 경우에 따라서 동시에 출력할 수 있다.

    Parameters
    ----------
    text : str : Optional
        출력할 텍스트
    color : int or 3-Tuple of ints
        색상. 숫자 1개를 입력하면 표준 16색/256색을 사용하며, 숫자 3개의 튜플을 사용하면 24비트 색상을 사용한다.
    reset : bool : Optional
        텍스트 출력 후 전부 리셋할지 여부. text 인자가 있어야 유효하다.
    reset_color : bool : Optional
        텍스트 출력 후 색상을 리셋할지 여부

    Notes
    -----
    색상 값은 다음을 참고한다.

    https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

    여기서 16색은 256color의 맨 앞 0~15번 색 코드를 사용한다.

    Examples
    --------
    배경 색을 밝은 빨강으로 바꾸기

    >>> print(set_bgcolor(color=9))

    배경 색을 256색 중 42번 색상으로 바꾸기

    >>> print(set_bgcolor(color=42))

    배경 색을 RGB(255, 128, 192)로 바꾸기

    >>> print(set_bgcolor(color=(255, 128, 192)))

    밝은 파랑 배경의 'Hello World' 출력

    >>> print(set_bgcolor('Hello World', reset=True))
    """
    color_code = _bgcolor_code(color) if color is None or isinstance(color, int) else _bgcolor_code(*color)
    reset_code = (
        CODE_TEMPLATE.format(CODE_RESET)
        if reset
        else CODE_TEMPLATE.format(CODE_RESET_BACKGROUND_COLOR)
        if reset_color
        else ""
    )
    return color_code + text + reset_code
