#!/usr/bin/env python
"""
JSON 파일들을 "그 자리에서" 리포맷팅하는 코드

하위 호환성 없어짐: 이제부터 폴더 안의 파일을 포맷팅하기 위해서는 glob 패턴을 사용해서 path/**/*.json 방식으로 입력해야 한다.
"""
import argparse
import glob
import json
import sys
from itertools import chain
from os import PathLike
from pathlib import Path
from typing import Iterator

JOB_DONE_SUCCESSFUL = 0
JOB_DONE_FAILED = 1


def find_files_with_glob(pattern: str) -> Iterator[Path]:
    return (p for s in glob.iglob(pattern, recursive=True) if (p := Path(s)).is_file())


def reformat_json(filename: PathLike, **kwargs) -> int:
    """JSON 파일을 보기 쉽게 리포맷팅한다.

    Parameters
    ----------
    filename : path-like object
        파일의 경로
    kwargs
        JSON 파일을 포맷팅할 옵션. json.dump 옵션을 따른다.

    Returns
    -------
    exit_code : int
        작업이 성공할 시 0, 실패할 시 1
    """
    jsonfile_read = open(filename, "r", encoding="utf-8")
    try:
        data = json.load(jsonfile_read)
    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing the file: {jsonfile_read.name}\nError details: {e}\n")
        jsonfile_read.close()
        return JOB_DONE_FAILED
    else:
        jsonfile_read.close()

        with open(filename, "w", encoding="utf-8") as jsonfile_write:
            json.dump(data, jsonfile_write, **kwargs)
        return JOB_DONE_SUCCESSFUL


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", metavar="PATH", nargs="+", type=str, help="JSON 파일(들) (와일드카드 지원)")
    indent_options = parser.add_mutually_exclusive_group()
    indent_options.add_argument("-t", "-tab", "--tab-indent", action="store_true", help="탭으로 인덴트를 구분할지 여부")
    indent_options.add_argument(
        "-i", "-in", "--indent", metavar="INDENT_VALUE", type=int, default=4, help="들여쓰기 크기(기본값: 4)"
    )
    parser.add_argument("-a", "-ascii", "--ascii-only", action="store_true", help="ASCII 모드로만 출력하기")
    parser.add_argument("-s", "-sort", "--sort-keys", action="store_true", help="키 정렬")
    parser.add_argument("-c", "-com", "--compact", action="store_true", help="모든 화이트스페이스를 없애기")
    parser.add_argument("-v", "--verbose", action="store_true", help="각각의 파일의 작업 결과를 출력")

    args = parser.parse_args()

    ensure_ascii = args.ascii_only
    indent = "\t" if args.tab_indent else args.indent
    sort_keys = args.sort_keys
    json_format_option = {"ensure_ascii": ensure_ascii, "sort_keys": sort_keys, "indent": indent}
    if args.compact:
        json_format_option["indent"] = None
        json_format_option["separators"] = (",", ":")

    json_files: Iterator[Path] = chain.from_iterable(find_files_with_glob(p) for p in args.path)

    # --verbose 옵션에서 사용할 카운트
    num_of_json_files = 0
    num_of_formatted_json_files = 0
    for json_file in json_files:
        num_of_json_files += 1

        if reformat_json(json_file, **json_format_option) == JOB_DONE_SUCCESSFUL:
            if args.verbose:
                print(f"{json_file!s} is formatted successfully", file=sys.stderr)
            num_of_formatted_json_files += 1

    if args.verbose:
        print(
            f"Successful: {num_of_formatted_json_files} / "
            f"Failed: {num_of_json_files - num_of_formatted_json_files} / "
            f"Total: {num_of_json_files}",
            file=sys.stderr,
        )
