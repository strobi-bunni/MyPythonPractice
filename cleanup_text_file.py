#!/usr/bin/env python
"""
탭을 공백으로 변경하고 후행 공백을 지우는 스크립트

Notepad++를 실행하고 일일히 변경하는 것이 귀찮아서 스크립트를 만들었다.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Literal


def cleanup_line(s: str, tabsize: int = 4, remove_whitespaces_mode: Literal['ascii', 'all', 'none'] = 'ascii') -> str:
    """줄을 정돈한다.
    탭을 공백으로 바꾸고(0 이하일 시 바꾸지 않음) 줄의 후행 공백을 지운다

    :param s: 줄의 문자
    :param tabsize: 탭 크기
    :param remove_whitespaces_mode: 지울 후행 공백('none': 지우지 않음, 'ascii': ASCII 공백, 'all': 모든 유니코드 공백)
    :return:
    """
    if tabsize and tabsize >= 0:
        s = s.expandtabs(tabsize)

    if remove_whitespaces_mode == 'ascii':
        s = re.sub(r'[ \t\n\r\f\v]+$', '', s)
    elif remove_whitespaces_mode == 'all':
        s = re.sub(r'\s+$', '', s)

    return s


def cleanup_text(s: str, tabsize=4, remove_whitespaces_mode: Literal['ascii', 'all', 'none'] = 'ascii') -> str:
    """문자열을 정돈한다.

    문자열의 모든 줄에 대해서 cleanup_line 함수를 실행한다.

    :param s: 줄의 문자
    :param tabsize: 탭 크기
    :param remove_whitespaces_mode: 지울 후행 공백('none': 지우지 않음, 'ascii': ASCII 공백, 'all': 모든 유니코드 공백)
    :return:
    """
    return '\n'.join(cleanup_line(line, tabsize, remove_whitespaces_mode) for line in s.split('\n'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r', encoding='utf-8'),
                        help="입력 파일 경로 (생략 시: stdin)", default=sys.stdin)
    parser.add_argument('-t', '--tab-size', type=int, default=4,
                        help='탭 크기(탭을 공백으로 변경하지 않으려면 0을 입력) (default: 4)')
    parser.add_argument('-s', '--remove-spaces', dest='remove_whitespaces_mode', type=str, default='ascii',
                        choices=('ascii', 'all', 'none'), help='지울 후행 공백 종류 (default: ascii)')
    group_output = parser.add_mutually_exclusive_group()
    group_output.add_argument('-o', '--outfile', type=argparse.FileType('w', encoding='utf-8'),
                              help='출력 파일 경로 (생략 시: stdout)', default=sys.stdout)
    group_output.add_argument('-I', '--inplace', action='store_true', help="새 파일을 만드는 대신 기존 파일을 덮어쓴다")
    parser.add_argument('--dry-run', action='store_true',
                        help="가상으로 돌려 보기(실제로 스크립트를 작동시키지 않는다)")
    parser.add_argument('-v', '--verbose', action='store_true', help="자세한 설명 출력")

    args = parser.parse_args()

    # 텍스트 읽기
    text: str = args.infile.read()
    if args.infile is not sys.stdin and not args.infile.closed:
        args.infile.close()

    # 텍스트 변환
    cleaned_text: str = cleanup_text(text, args.tab_size, args.remove_whitespaces_mode)
    needs_to_cleanup = text != cleaned_text
    # verbose 옵션
    if args.verbose:
        if not needs_to_cleanup:
            print(f"{args.infile.name} doesn't need to cleanup", file=sys.stderr)
        elif args.dry_run:
            print(f"{args.infile.name} needs to cleanup", file=sys.stderr)
        else:
            print(f"Cleaning up {args.infile.name}", file=sys.stderr)

    # dry-run=false일 시에만 변환한다.
    if not args.dry_run:
        if args.inplace and needs_to_cleanup:
            Path(args.infile.name).write_text(cleaned_text, encoding='utf-8')
        else:
            args.outfile.write(cleaned_text)
            if args.outfile is not sys.stdout:
                args.outfile.close()
