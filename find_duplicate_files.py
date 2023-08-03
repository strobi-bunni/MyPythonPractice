#!/usr/bin/env python
"""해시 값을 사용해서 중복되는 파일 찾기

사용법 : find_duplicate_files.py [-h] -d DIR [DIR ...] [-a ALGORITHM] [-o OUT]
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from itertools import chain
from os import PathLike, walk
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, TextIO

HASH_BLOCK_SIZE = 65536


def file_hash(filename: PathLike, algorithm="sha256", **kwargs) -> bytes:
    """파일의 해시 계산

    Parameters
    ----------
    filename : path-like object
        파일의 경로
    algorithm : str : optional
        사용할 알고리즘

    Returns
    -------
    h : bytes
        계산된 파일 해시
    """
    h = hashlib.new(algorithm, **kwargs)
    with open(filename, "rb") as hashfile:
        while buffer := hashfile.read(HASH_BLOCK_SIZE):
            h.update(buffer)
    return h.digest()


def find_child_files(path: PathLike, verbose=False) -> Iterator[Path]:
    for parent_dir_name, _, child_file_names in walk(Path(path)):
        parent_path = Path(parent_dir_name)
        if verbose:
            print(f"Checking {parent_path}", file=sys.stderr)
        yield from (parent_path / child_file_name for child_file_name in child_file_names)


def find_duplicate(*paths: PathLike, algorithm="md5", include_zerofile=False, verbose=False) -> Dict[bytes, List[Path]]:
    """중복된 파일을 찾는다.

    Parameters
    ----------
    paths : path-like object, or iterable of path-like object
        파일이 저장된 폴더 경로
    algorithm : str : optional
        사용할 해시 알고리즘
    include_zerofile : bool
        크기가 0인 파일을 포함할지 여부
    verbose : bool
        자세한 설명을 출력할지 여부

    Returns
    -------
    dupes : dict
        중복된 파일의 리스트
        키는 파일 해시이며 값은 중복된 해시를 갖는 파일 경로의 리스트이다.
    """
    hashes = defaultdict(list)  # 파일 해시를 저장할 딕셔너리

    # 파일 경로 리스트
    paths = [Path(p) for p in paths]
    filepaths = chain.from_iterable(find_child_files(p, verbose=verbose) for p in paths)

    # 해시값 저장
    for filepath in filepaths:
        if not include_zerofile and filepath.stat().st_size == 0:
            continue
        filehash = file_hash(filepath, algorithm)
        hashes[filehash].append(filepath)
    return {k: v for k, v in hashes.items() if len(v) >= 2}


def count_duplicate(out: Mapping[bytes, Iterable[Path]]) -> int:
    """중복된 파일의 갯수를 찾는다."""
    return sum(len(list(v)) - 1 for v in out.values())


def calculate_wasted_spaces(out: Mapping[bytes, Iterable[Path]]) -> int:
    """낭비된 공간을 바이트 단위로 계산한다."""
    wasted = 0
    for v in out.values():
        vlist = list(v)
        wasted += vlist[0].stat().st_size * (len(vlist) - 1)
    return wasted


def format_output(out: Mapping[bytes, Iterable[Path]], file: TextIO = sys.stdout) -> None:
    for k, v in out.items():
        print(f"Duplicate file for hash {k.hex()}", file=file)
        for p in v:
            print(p, file=file)
        print("", file=file)

    print(
        f"Found {count_duplicate(out)} duplicate files ({calculate_wasted_spaces(out):_d} bytes wasted spaces.)",
        file=file,
    )


def format_output_json(out: Mapping[bytes, Iterable[Path]], file: TextIO = sys.stdout) -> None:
    dupes_info: Dict[str, List[str]] = {k.hex(): [str(p) for p in v] for (k, v) in out.items()}
    dupes_stats = {"Count": count_duplicate(out), "TotalSize": calculate_wasted_spaces(out)}
    print(json.dumps({"Result": dupes_info, "Stats": dupes_stats}, ensure_ascii=False, indent=4), file=file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs=argparse.ONE_OR_MORE, metavar="DIR", type=str, help="파일이 저장된 경로")
    parser.add_argument(
        "-a",
        "--algorithm",
        metavar="ALGORITHM",
        type=str,
        help="해시를 계산할 알고리즘",
        default="md5",
        choices=("md5", "sha1", "sha224", "sha256"),
    )
    parser.add_argument("-f", "--format", type=str, choices=("plain", "json"), default="plain", help="출력 형식")
    parser.add_argument("-z", "--zero", action="store_true", dest="include_zerofile", help="크기가 0인 파일을 포함할지 여부")
    parser.add_argument("-v", "--verbose", action="store_true", help="자세한 설명을 출력할지 여부")
    parser.add_argument(
        "-o",
        "--out",
        metavar="OUT",
        type=argparse.FileType("w", encoding="utf-8"),
        default=sys.stdout,
        help="결과를 출력할 파일",
    )
    args = parser.parse_args()
    duplicate_result = find_duplicate(
        *args.dir, algorithm=args.algorithm, include_zerofile=args.include_zerofile, verbose=args.verbose
    )
    if args.format == "json":
        format_output_json(duplicate_result, file=args.out)
    else:
        format_output(duplicate_result, file=args.out)
    args.out.close()
