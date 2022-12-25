#!/usr/bin/env python
"""
다음은 유니코드로 되어 있는 파일 이름을 정규화한다.
정규화 방식은 NFC 혹은 NFD를 지원한다.

예시 : '테스트파일.txt'(NFC) <--> '테스트파일.txt'(NFD)

이 스크립트는 macOS/iOS/iPadOS에서 가져온 파일의 이름에서 한글의 자모가 분리된 현상을 해결할 때 사용할 수 있다.

::

    normalize_unicode_filename.py [-h] [-r] [-m {NFC,NFD,NFKC,NFKD}] [-v] path [path ...]

-h : 도움말을 표시한다.
-r : path가 폴더일 경우, 하위 폴더 및 파일의 이름까지 정규화한다.
-m : 유니코드 정규화 방식. 기본값은 NFC이다.
path : 이름을 변경할 파일(들)
"""
import argparse
import sys
import unicodedata
from os import PathLike
from pathlib import Path
from typing import Iterator, List, Literal

T_NormalizeMode = Literal['NFC', 'NFD', 'NFKC', 'NFKD']


def traverse_subpaths_dfs_post(path: PathLike) -> Iterator[Path]:
    """경로 path 안의 하위 경로를 DFS(Depth-first) 방식으로 후위 순회한다. 자신도 포함한다.
    """
    path = Path(path)
    for child in path.iterdir():
        if child.is_dir():
            yield from traverse_subpaths_dfs_post(child)
        else:
            yield child
    yield path


def rename_item(path: PathLike, mode: T_NormalizeMode = 'NFC', recursive: bool = False, verbose=False) -> None:
    path = Path(path)
    if path.is_dir() and recursive:
        items: List[Path] = list(traverse_subpaths_dfs_post(path))
    else:
        items: List[Path] = [path]

    for p in items:
        new_name = p.with_name(unicodedata.normalize(mode, p.name))
        if new_name != p:
            p.rename(new_name)
            if verbose:
                print(f'Renamed {p} --> {new_name}', file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='유니코드 파일 이름을 정규화합니다.')
    parser.add_argument('path', type=Path, nargs='+', help='변경할 파일의 경로(들)')
    parser.add_argument('-r', '--recursive', action='store_true', help='폴더 안의 파일이름도 변경할지 여부')
    parser.add_argument('-m', '--mode', choices=('NFC', 'NFD', 'NFKC', 'NFKD'), default='NFC', type=str,
                        help='유니코드 정규화 형식(NFC/NFD/NFKC/NFKD). 기본값은 NFC')
    parser.add_argument('-v', '--verbose', action='store_true', help='자세한 설명을 출력')
    args = parser.parse_args()

    for path_to_rename in args.path:
        abs_path_to_rename = path_to_rename.absolute()
        if abs_path_to_rename.exists():
            rename_item(abs_path_to_rename, mode=args.mode, recursive=args.recursive, verbose=args.verbose)
