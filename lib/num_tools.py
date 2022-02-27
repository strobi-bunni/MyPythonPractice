import math
from typing import List


def get_digit(num: int, loc: int, *, base: int = 10, copysign=True) -> int:
    """
    숫자에서 ``base ** loc`` 번째 자릿수를 반환한다.

    Parameters
    ----------
    num : int
        계산할 숫자.
    loc : int(non-negative)
        뒤에서부터 위치, 예를 들어 base=10일 때 loc=3이면 1000의 자릿수를 구한다.
    base : int(positive) : optional
        뒤에서부터 위치를 계산할 때 기준이 되는 진법. 기본값은 10이다.
    copysign : bool : optional
        num의 부호를 복사할 지의 여부. 기본값은 True이다.

    Returns
    -------
    d : int
        ``num``의 ``base ** loc``번째 자릿수

    Example
    -------
    >>> get_digit(12345, 0)   # 10**0, 즉 1의 자릿수를 반환
    5
    >>> get_digit(12345, 3)   # 10**3, 즉 1000의 자릿수를 반환
    2
    >>> hex(get_digit(0xabcdef, 1, base=256))
    '0xcd'
    """
    if loc < 0:
        raise ValueError('`loc` must be non-negative value.')
    if base <= 0:
        raise ValueError('`base` must be positive value.')
    sign = -1 if ((num < 0) and copysign) else 1
    return sign * ((abs(num) % base ** (loc + 1)) // base ** loc)


def base_encode(num: int, base: int, use_big_endian=True, copysign=True) -> List[int]:
    r"""숫자 ``num``\을 ``base`` 진법을 사용해서 리스트 형태로 반환한다.

    Parameters
    ----------
    num : int
        변환할 숫자
    base : int(positive)
        변환할 자릿수
    use_big_endian : bool, optional
        빅 엔디언을 사용할 지의 여부. 기본값은 True이다.
    copysign : bool : optional
        ``num``\의 부호를 복사할 지의 여부. 기본값은 True이다.

    Returns
    -------
    digits : list of int
        변환된 자릿수

    Exceptions
    ----------
    ValueError
        base <= 0일 경우

    Examples
    --------
    다음은 ``base_encode`` 함수의 기본적인 사용이다.
    >>> base_encode(12345, 10)
    [1, 2, 3, 4, 5]
    >>> [hex(i) for i in base_encode(0xabcdef, 256)]
    ['0xab', '0xcd', '0xef']

    다음은 Little Endian 변환 예시이다.
    >>> base_encode(12345, 10, use_big_endian=False)
    [5, 4, 3, 2, 1]
    >>> sum(v * 10 ** i for (i, v) in enumerate([5, 4, 3, 2, 1]))
    12345

    다음은 음수 처리의 예시이다.
    >>> base_encode(-12345, 10)
    [-1, -2, -3, -4, -5]
    >>> base_encode(-12345, 10, copysign=False)
    [1, 2, 3, 4, 5]
    """
    if base <= 0:
        raise ValueError('`base` must be positive value.')

    if num == 0:
        return [0]

    _num = abs(num)
    digits = []
    sign = -1 if ((num < 0) and copysign) else 1

    while _num:
        _num, digit = divmod(_num, base)
        digits.append(sign * digit)
    if use_big_endian:
        digits.reverse()
    return digits


def floor_to_multiple(x, mult=1, offset=0):
    """주어진 배수로 숫자를 내림한다.

    Parameters
    ----------
    x : Any numeric value
        아무 수
    mult : Any numeric value
        숫자를 내림할 배수. 기본값은 1
    offset : Any numeric value
        배수의 기준이 될 오프셋. 기본값은 0

    Returns
    -------
    y : Any numeric value
        주어진 배수로 내림한 수

    Examples
    --------
    다음은 주어진 숫자를 가장 가까운 짝수/홀수로 내림하는 예시이다.

    >>> floor_to_multiple(3.1415, 2)   # 가장 가까운 짝수
    2
    >>> floor_to_multiple(3.1415, 2, offset=1)   # 가장 가까운 홀수
    3

    다른 유형의 자료형에도 지정할 수 있다.

    >>> from datetime import datetime, timedelta
    >>> d = datetime(2020, 9, 20)
    >>> origin = datetime(2020, 1, 1)
    >>> dt = timedelta(days=10)
    >>> floor_to_multiple(d, dt, offset=origin)
    datetime.datetime(2020, 9, 17, 0, 0)
    """
    return math.floor((x - offset) / mult) * mult + offset


def ceil_to_multiple(x, mult=1, offset=0):
    """주어진 배수로 숫자를 올림한다.

    Parameters
    ----------
    x : Any numeric value
        아무 수
    mult : Any numeric value
        숫자를 올림할 배수. 기본값은 1
    offset : Any numeric value
        배수의 기준이 될 오프셋. 기본값은 0

    Returns
    -------
    y : Any numeric value
        주어진 배수로 올림한 수

    Examples
    --------
    다음은 주어진 숫자를 가장 가까운 짝수/홀수로 올림하는 예시이다.

    >>> ceil_to_multiple(3.1415, 2)   # 가장 가까운 짝수
    4
    >>> ceil_to_multiple(3.1415, 2, offset=1)   # 가장 가까운 홀수
    5

    다른 유형의 자료형에도 지정할 수 있다.

    >>> from datetime import datetime, timedelta
    >>> d = datetime(2020, 9, 20)
    >>> origin = datetime(2020, 1, 1)
    >>> dt = timedelta(days=10)
    >>> floor_to_multiple(d, dt, offset=origin)
    datetime.datetime(2020, 9, 27, 0, 0)
    """
    return math.ceil((x - offset) / mult) * mult + offset


def catalan(n: int) -> int:
    """
    n번째 카탈란 수
    """
    return math.factorial(2 * n) // (math.factorial(n) * math.factorial(n + 1))
