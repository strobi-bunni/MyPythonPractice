r"""
글자수 세기
===========
이 스크립트는 텍스트 파일 내의 글자수를 센다.

::

    $ python char_count.py -i filename.txt
    filename.txt | 4031S 124L 101N 428W 3659C 1916V
    $ echo filename.txt | python char_count.py
    filename.txt | 4031S 124L 101N 428W 3659C 1916V

``-v`` 옵션을 지정하지 않았을 시 출력 포맷은 다음과 같다:

- S : 텍스트 파일의 길이(bytes)
- L : 줄 갯수
- N : 유효한 줄 갯수(화이트스페이스만 있는 줄 제외)
- W : 단어 갯수
- C : 문자 갯수(개행 문자 포함)
- V : 유효한 문자 갯수(화이트스페이스, 문장 부호 등 제외)

NOTE: Windows 환경에서 stdin으로 내용을 보낼 때는 `UTF-8 모드`_\로 실행한다.

::

    C:\folder> type filename.txt | python.exe -X utf8 char_count.py
    filename.txt | 4031S 124L 101N 428W 3659C 1916V

.. _`UTF-8 모드`: https://docs.python.org/3/library/os.html#utf8-mode
"""
import argparse
import re
import sys
from typing import Literal


def convert_newline(s: str, mode: Literal["cr", "lf", "crlf"] = "lf") -> str:
    r"""
    새 줄 문자를 통일된 형식으로 바꾼다.

    Parameters
    ----------
    s : str
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
    new_s : str
        줄바꿈 문자가 변환된 새 문자

    Exceptions
    ----------
    ValueError
        ``mode``가 ``'cr'``, ``'lf'``, ``'crlf'`` 중 어느 값에도 해당되지 않을 때

    Examples
    --------
    >>> convert_newline('abcde\rfghij\r\nklmno\npqrst')
    'abcde\nfghij\nklmno\npqrst'
    """
    if mode not in ["cr", "lf", "crlf"]:
        raise ValueError("`Mode` must be 'cr', 'lf' or 'crlf'")

    new_s = s.replace("\r\n", "\n").replace("\r", "\n")
    if mode == "cr":
        new_s = new_s.replace("\n", "\r")
    elif mode == "crlf":
        new_s = new_s.replace("\n", "\r\n")

    return new_s


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='입력할 파일', type=argparse.FileType('rb'), default=sys.stdin)
    parser.add_argument('-e', '--encoding', help='인코딩', type=str, default='utf-8')
    parser.add_argument('-n', '--newline', help='개행 문자', type=str,
                        choices=['cr', 'lf', 'crlf', 'auto'], default='auto')
    parser.add_argument('-v', '--verbose', help='자세한 설명을 출력할지 여부', action='store_true')
    args = parser.parse_args()

    if (input_file := args.input) is sys.stdin:
        filename = '<stdin>'
        text: str = input_file.read()
        size_of_file = len(text.encode(args.encoding))
    else:
        filename = input_file.name
        data: bytes = input_file.read()
        size_of_file = len(data)
        text = data.decode(args.encoding)

    number_of_chars = len(text)

    # 개행 문자를 통일함
    if args.newline == 'auto':
        text_newline_converted: str = convert_newline(text)
        newline = '\n'
    else:
        text_newline_converted: str = text
        newline = '\n' if args.newline == 'lf' \
            else '\r\n' if args.newline == 'crlf' \
            else '\r'

    # split text into lines
    lines: list[str] = text_newline_converted.split(newline)
    number_of_lines = 0
    number_of_valid_lines = 0
    number_of_words = 0
    number_of_valid_chars = 0

    # 줄 하나하나에 정규표현식 적용
    for line in lines:
        number_of_lines += 1
        if line and not line.isspace():
            number_of_valid_lines += 1
            words: list[str] = re.findall(r'\b\w+\b', line)
            number_of_words += len(words)
            number_of_valid_chars += sum(len(w) for w in words)

    if args.verbose:
        print(f'{filename}\n'
              f'{size_of_file} bytes\n'
              f'{number_of_lines} lines\n'
              f'{number_of_valid_lines} valid(meaningful) lines\n'
              f'{number_of_words} words\n'
              f'{number_of_chars} characters\n'
              f'{number_of_valid_chars} valid(meaningful) characters')
    else:
        print(f'{filename} | {size_of_file}S {number_of_lines}L {number_of_valid_lines}N '
              f'{number_of_words}W {number_of_chars}C {number_of_valid_chars}V')
