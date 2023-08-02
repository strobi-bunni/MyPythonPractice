#!/usr/bin/env python
"""
JSON 파일들을 리포맷팅하는 코드

명령줄 파이프라인과 호환되도록 만들었다.
"""
import argparse
import json
import sys
from pathlib import Path

JOB_DONE_SUCCESSFUL = 0
JOB_DONE_FAILED = 1


def reformat_json_str(jsonstr: str, **kwargs) -> str:
    """JSON 파일을 보기 쉽게 리포맷팅한다.

    Parameters
    ----------
    jsonstr : str
        JSON 데이터
    kwargs
        JSON 파일을 포맷팅할 옵션. json.dump 옵션을 따른다.

    Returns
    -------
    reformatted_jsonstr : str
        변환한 JSON 코드
    """
    data = json.loads(jsonstr)
    return json.dumps(data, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "infile", nargs="?", type=argparse.FileType("r", encoding="utf-8"), default=sys.stdin, help="변환할 JSON 파일"
    )
    indent_options = parser.add_mutually_exclusive_group()
    indent_options.add_argument("-t", "--tab-indent", action="store_true", help="탭으로 인덴트를 구분할지 여부")
    indent_options.add_argument("-i", "--indent", metavar="INDENT", type=int, default=4, help="들여쓰기 크기(기본값: 4)")
    parser.add_argument("-C", "--compact", action="store_true", help="모든 화이트스페이스를 없애기")
    parser.add_argument("-a", "--ascii-only", action="store_true", help="ASCII 모드로만 출력하기")
    parser.add_argument("-k", "--sort-keys", action="store_true", help="키 정렬")
    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument("-I", "--inplace", action="store_true", help="기존 파일을 덮어쓸지 여부")
    output_options.add_argument(
        "-o", "--outfile", type=argparse.FileType("w", encoding="utf-8"), default=sys.stdout, help="출력할 파일"
    )

    args = parser.parse_args()

    # 텍스트 읽기
    json_str = args.infile.read()
    if args.infile is not sys.stdin and not args.infile.closed:
        args.infile.close()

    # json 포맷팅 옵션 딕셔너리 생성
    ensure_ascii = args.ascii_only
    sort_keys = args.sort_keys
    if args.tab_indent:
        indent = "\t"
    else:
        indent = args.indent
    json_format_option = {"ensure_ascii": ensure_ascii, "sort_keys": sort_keys, "indent": indent}
    if args.compact:
        json_format_option["indent"] = None
        json_format_option["separators"] = (",", ":")

    # JSON 포맷팅
    try:
        reformatted_json_str = reformat_json_str(json_str, **json_format_option)
    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing the file: {args.infile.name}\nError details: {e}\n", file=sys.stderr)
        reformatted_json_str = None
        exit(1)

    # 파일 쓰기
    if args.inplace:
        Path(args.infile.name).write_text(reformatted_json_str, encoding="utf-8")
    else:
        args.outfile.write(reformatted_json_str)
        if args.outfile is not sys.stdout:
            args.outfile.close()
