"""
다음은 유니코드로 되어 있는 파일 이름을 정규화한다.
정규화 방식은 NFC 혹은 NFD를 지원한다.

예시 : '테스트파일.txt'(NFC) <--> '테스트파일.txt'(NFD)

이 스크립트는 macOS/iOS/iPadOS에서 가져온 파일의 이름에서 한글의 자모가 분리된 현상을 해결할 때 사용할 수 있다.

::

    normalize_unicode_filename.py [-h] [-r] [-m {NFC,NFD}] path [path ...]

-h : 도움말을 표시한다.
-r : path가 폴더일 경우, 하위 폴더 및 파일의 이름까지 정규화한다.
-m : 유니코드 정규화 방식. 기본값은 NFC이다.
path : 이름을 변경할 파일(들)
"""
import argparse
import unicodedata
from pathlib import Path
from typing import Iterator, List, Literal, Union

T_PathLike = Union[str, Path]
T_NormalizeMode = Literal['NFC', 'NFD']


def normalized_name(filename: str, mode: T_NormalizeMode = 'NFC') -> str:
    """NFC로 정규화한 파일 이름
    """
    return unicodedata.normalize(mode, filename)


def rename_to_normalized(path: T_PathLike, mode: T_NormalizeMode = 'NFC') -> Path:
    """정규화된 파일 이름으로 이름 바꾸기
    """
    path = Path(path)
    return path.rename(path.with_name(normalized_name(path.name, mode=mode)))


def traverse_subpaths_dfs_post(path: T_PathLike) -> Iterator[Path]:
    """경로 path 안의 하위 경로를 DFS(Depth-first) 방식으로 후위 순회한다.
    """
    path = Path(path)
    for child in path.iterdir():
        if child.is_dir():
            yield from traverse_subpaths_dfs_post(child)
        else:
            yield child
    yield path


def rename_item(path: T_PathLike, mode: T_NormalizeMode = 'NFC', recursive: bool = False) -> None:
    path = Path(path)
    items: List[Path] = [path]
    if path.is_dir() and recursive:
        items.extend(traverse_subpaths_dfs_post(path))
    [rename_to_normalized(p, mode=mode) for p in items]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='유니코드 파일 이름을 정규화합니다.')
    parser.add_argument('path', type=Path, nargs='+', help='변경할 파일의 경로(들)')
    parser.add_argument('-r', '--recursive', action='store_true', help='폴더 안의 파일이름도 변경할지 여부')
    parser.add_argument('-m', '--mode', choices=['NFC', 'NFD'], default='NFC',
                        help='유니코드 정규화 형식(NFC/NFD). 기본값은 NFC')
    args = parser.parse_args()

    for path in args.path:
        abs_path = path.absolute()
        if abs_path.exists():
            rename_item(abs_path, mode=args.mode, recursive=args.recursive)
