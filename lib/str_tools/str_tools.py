import hashlib
import re
import unicodedata
from collections.abc import Iterator
from typing import AnyStr, Literal, Union, overload


def find_prefix(prefix: str, s: str, flags=re.M, *, include_prefix=False) -> list[str]:
    """
    텍스트에서 특정 접두어로 시작하는 줄의 내용을 반환한다.

    Parameters
    ----------
    prefix : str
        검색할 접두어
    s : str
        내용을 검색할 텍스트
    flags : int, optional
        정규 표현식 검색에 사용할 플래그. 기본값은 re.MULTILINE이다.
    include_prefix : bool, optional
        검색 결과에 접두어를 포함하는지의 여부. 기본값은 False이다.

    Returns
    -------
    lines : list of str
        특정 접두어로 시작하는 줄의 내용

    Examples
    --------
    >>> text = '''
    ... Java: *.java
    ... Python: *.py
    ... C++: *.cpp
    ... '''
    >>> find_prefix("python: ", text, re.I|re.M)
    ['*.py']
    """
    prefix_pattern = re.escape(prefix)

    if include_prefix:
        regex = re.compile('^{}.*$'.format(prefix_pattern), flags)
    else:
        regex = re.compile('(?<=^{}).*$'.format(prefix_pattern), flags)
    return regex.findall(s)


def findall(string: AnyStr, substr: AnyStr, *, overlap=False) -> Iterator[int]:
    r"""문자열 ``string``\에서 특정 문자열 ``substr``\의 위치를 검색해서 그 위치를 모두 반환한다.
    만약 ``overlap``\이 ``True``\일 경우 ``findall`` 함수는 서로 겹쳐지는 범위를 찾을 수도 있다.

    Parameters
    ----------
    string : str or bytes
        ``substr``\를 검색할 문자열
    substr : str or bytes
        위치를 찾을 문자
    overlap : bool, optional
        겹쳐지는 범위를 찾을 지의 여부. 기본값은 False이다.

    Yields
    ------
    pos : int
        ``string``\에서 ``substr``\가 있는 위치

    Exceptions
    ----------
    TypeError
        ``string``\과 ``substr``\의 타입이 다를 경우
    ValueError
        ``substr``\가 빈 문자일 경우

    Examples
    --------
    >>> list(findall('==hello python hello world hello==', 'hello'))
    [2, 15, 27]
    >>> # ==hello python hello world hello==
    >>> #   ^^^^^        ^^^^^       ^^^^^
    >>> #   2            15          27

    >>> list(findall('trololololol', 'lol'))
    [3, 7]
    >>> # trololololol
    >>> #    ^^^ ^^^
    >>> #    3   7

    >>> list(findall('trololololol', 'lol', overlap=True))
    [3, 5, 7, 9]
    >>> # trololololol
    >>> #    ^^^^^^^^^
    >>> #    3 5 7 9
    """
    if type(string) != type(substr):
        raise TypeError('string and substr have different types.')
    if not substr:
        raise ValueError('substr is empty.')

    current_pos = 0
    while True:
        location = string.find(substr, current_pos)
        if location == -1:
            break
        else:
            yield location
            next_step = 1 if overlap else len(substr)
            current_pos = location + next_step


def convert_newline(s: AnyStr, mode: Literal['cr', 'lf', 'crlf'] = 'lf') -> AnyStr:
    r"""
    새 줄 문자를 통일된 형식으로 바꾼다.

    Parameters
    ----------
    s : str or bytes
        변환할 문자열
    mode : {'cr', 'lf', 'crlf'}
        변환할 새 줄 문자. 기본값은 'lf'이다.

        ========== ============ ================
        mode       newline char operating system
        ========== ============ ================
        ``'cr'``   ``'\r'``     Classic MacOS
        ``'lf'``   ``'\n'``     GNU/Linux, macOS
        ``'crlf'`` ``'\r\n'``   MS-DOS, Windows
        ========== ============ ================

    Returns
    -------
    new_s : str or bytes
        줄바꿈 문자가 변환된 새 문자

    Exceptions
    ----------
    ValueError
        ``mode``가 ``'cr'``, ``'lf'``, ``'crlf'`` 중 어느 값에도 해당되지 않을 때

    Examples
    --------
    >>> convert_newline('abcde\rfghij\r\nklmno\npqrst')
    'abcde\nfghij\nklmno\npqrst'
    >>> convert_newline(b'abcde\rfghij\r\nklmno\npqrst')
    b'abcde\nfghij\nklmno\npqrst'
    """
    if mode not in ['cr', 'lf', 'crlf']:
        raise ValueError('`Mode` must be \'cr\', \'lf\' or \'crlf\'')

    is_str = isinstance(s, str)
    b = s.encode() if is_str else s

    new_b = b.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    if mode == 'cr':
        new_b = new_b.replace(b'\n', b'\r')
    elif mode == 'crlf':
        new_b = new_b.replace(b'\n', b'\r\n')

    return new_b.decode() if is_str else new_b


@overload
def get_str_hash(s: bytes, **kwargs) -> bytes: ...


@overload
def get_str_hash(s: bytes, algorithm: str, **kwargs) -> bytes: ...


@overload
def get_str_hash(s: str, **kwargs) -> bytes: ...


@overload
def get_str_hash(s: str, algorithm: str, **kwargs) -> bytes: ...


@overload
def get_str_hash(s: str, algorithm: str, encoding: str, **kwargs) -> bytes: ...


@overload
def get_str_hash(s: str, algorithm: str, encoding: str, errors: str, **kwargs) -> bytes: ...


def get_str_hash(s: Union[str, bytes], algorithm: str = 'sha256', encoding='utf-8', errors='strict', **kwargs) -> bytes:
    r"""문자열의 해시 값을 구한다.

    Parameters
    ----------
    s : str or bytes
        계산할 문자열, 혹은 바이트
    algorithm : str, Optional
        해시를 계산할 때 사용할 알고리즘. 생략한다면 SHA256을 사용한다.
    encoding : str : Optional
        사용할 인코딩, 기본값은 'utf-8'이다. s가 str일 때만 유효하다.
    errors : str : Optional
        인코딩 오류 시 처리할 방법, 기본값은 'strict'이다. s가 str일 때만 유효하다.
    kwargs
        추가 옵션. ``hashlib.new``에서 해시를 계산할 때 사용할 수 있는 옵션들이다.

    Returns
    -------
    h : bytes
        문자열의 해시 값

    Examples
    --------
    >>> get_str_hash('python')  # default: SHA256
    b'\x11\xa4\xa6\x0bQ\x8b\xf2I\x89\xd4\x81F\x80v\xe5\xd5\x98(\x84bj\xed\x9f\xae\xb3[\x85v\xfc\xd2#\xe1'
    >>> get_str_hash('python', 'md5')  # MD5
    b'#\xee\xebCG\xbd\xd2k\xfck~\xe9\xa3\xb7U\xdd'
    >>> get_str_hash('python', 'blake2b', digest_size=32)  # BLAKE2b, using kwargs
    b'^[H}\xcc\xd7\xb1pH\xd0\xa2s\x96\xdf\xa2\x06\xa4\x1c\xf5\xc8w!\xb8;?\xda9^\xe2\x95\x90^'
    """
    hash_obj = hashlib.new(algorithm, **kwargs)
    if isinstance(s, str):
        b = s.encode(encoding=encoding, errors=errors)
    else:
        b = s
    hash_obj.update(b)
    return hash_obj.digest()


def get_unicode_repr(s: str) -> str:
    """문자(열)의 유니코드 표기법을 반환한다.

    ::

        unicode_repr      ::= "" | unicode_char_repr (" " unicode_char_repr)*
        unicode_char_repr ::= "U+" hexadecimal_digit{4, 6}
        hexadecimal_digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" |
                              "8" | "9" | "A" | "B" | "C" | "D" | "E" | "F"

    Parameters
    ----------
    s : str
        문자열

    Returns
    -------
    code : str
        문자열의 표기법

    Examples
    --------
    >>> get_unicode_repr('A')
    'U+0041'
    >>> get_unicode_repr('ABC')
    'U+0041 U+0042 U+0043'
    """
    return ' '.join(f'U+{ord(c):04X}' for c in s)


def get_str_width(s: str, east_asian=False) -> int:
    """문자열 s의 전각/반각을 고려해서, 모노스페이스 글꼴로 출력할 시 폭을 출력한다.

    참고 링크 : https://www.unicode.org/reports/tr11/

    Parameters
    ----------
    s : str
        대상 문자열
    east_asian : bool
        동아시아 인코딩을 기준으로 할 것인지. ``east_asian=True`` 이면  ``east_asian_width`` 속성값이 ``'A'`` 인 값은
        전각으로 인코딩되며 ``east_asian=False`` 이면 반각으로 인코딩된다.

    Returns
    -------
    width : int
        문자열의 폭

    Examples
    --------
    >>> get_str_width('abcdef')   # ASCII alphabets: [Na]rrow
    6
    >>> get_str_width('가나다라')   # Hangul characters: [W]ide
    8
    >>> get_str_width('１２３')   # Fullwidth digits: [F]ullwidth (narrow if NFKC normalized)
    6
    >>> get_str_width('ｱｲｳｴｵ')   # Halfwidth Katakanas: [H]alfwidth (wide if NFKC normalized)
    5
    >>> get_str_width('ΑΒΓΔ')   # Greek letters: [A]mbiguous
    4
    >>> get_str_width('ΑΒΓΔ', east_asian=True)   # use East Asian compatible width
    8
    """
    width = 0
    for c in s:
        east_asian_width_code = unicodedata.east_asian_width(c)
        char_width = 1 if east_asian_width_code in ['H', 'Na', 'N'] \
            else 2 if east_asian_width_code in ['W', 'F'] \
            else 2 if east_asian \
            else 1
        width += char_width
    return width


def apart_prefix(s: AnyStr, prefix: AnyStr) -> tuple[AnyStr, AnyStr]:
    r"""문자열의 시작 부분에서 prefix 부분만을 떼어낸다.
    만약 문자열이 prefix로 시작하지 않는다면 ``('', s)``\를 반환한다.

    Parameters
    ----------
    s : str or bytes
        문자열
    prefix : str or bytes
        문자열의 시작 부분

    Returns
    -------
    prefix : str or bytes
        문자열의 첫 부분
    last : str or bytes
        문자열의 prefix를 제외한 뒤 부분

    Examples
    --------
    >>> apart_prefix('Hello World', 'Hello')
    ('Hello', ' World')
    >>> apart_prefix('Hello World', 'Python')
    ('', 'Hello World')
    """
    if prefix and s.startswith(prefix):
        return prefix, s[len(prefix):]
    else:
        if isinstance(s, str):
            return '', s
        else:
            return b'', s


def apart_suffix(s: AnyStr, suffix: AnyStr) -> tuple[AnyStr, AnyStr]:
    r"""문자열의 끝 부분에서 suffix 부분만을 떼어낸다.
    만약 문자열이 suffix로 시작하지 않는다면 ``(s, '')``\를 반환한다.

    Parameters
    ----------
    s : str or bytes
        문자열
    suffix : str or bytes
        문자열의 끝 부분

    Returns
    -------
    first : str or bytes
        문자열의 suffix를 제외한 앞 부분
    suffix : str or bytes
        문자열의 끝 부분

    Examples
    --------
    >>> apart_suffix('Hello World', 'World')
    ('Hello ', 'World')
    >>> apart_suffix('Hello World', 'Python')
    ('Hello World', '')
    """
    # len(suffix) == 0이면 if suffix and... 부분을 안 붙였을 때 s[:-0] == ''가 되므로 테스트 케이스가 실패한다.
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)], suffix
    else:
        if isinstance(s, str):
            return s, ''
        else:
            return s, b''


__all__ = ['apart_prefix', 'apart_suffix', 'convert_newline', 'find_prefix', 'findall', 'get_str_hash', 'get_str_width',
           'get_unicode_repr']
