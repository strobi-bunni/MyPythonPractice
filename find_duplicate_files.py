"""해시 값을 사용해서 중복되는 파일 찾기

사용법 : find_duplicate_files.py [-h] -d DIR [DIR ...] [-a ALGORITHM] [-o OUT]


"""
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Iterable, Union, TextIO
from itertools import chain
import argparse
import hashlib
import sys


T_PathLike = Union[str, Path]
HASH_BLOCK_SIZE = 65536


def file_hash(filename: T_PathLike, algorithm='sha256', **kwargs) -> bytes:
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
    with open(filename, 'rb') as hashfile:
        while True:
            buffer = hashfile.read(HASH_BLOCK_SIZE)
            if not buffer:
                break
            h.update(buffer)
    return h.digest()


def find_duplicate(path: Union[T_PathLike, Iterable[T_PathLike]],
                   algorithm='md5') -> Dict[bytes, List[Path]]:
    """중복된 파일을 찾는다.

    Parameters
    ----------
    path : path-like object, or iterable of path-like object
        파일이 저장된 폴더 경로
    algorithm : str : optional
        사용할 해시 알고리즘

    Returns
    -------
    dupes : dict
        중복된 파일의 리스트
        키는 파일 해시이며 값은 중복된 해시를 갖는 파일 경로의 리스트이다.
    """
    hashs = defaultdict(list)   # 파일 해시를 저장할 딕셔너리

    # 파일 경로 리스트
    if isinstance(path, Path) or isinstance(path, str):
        path = [Path(path)]
    else:
        path = [Path(p) for p in path]
    filepaths = chain.from_iterable(filter(lambda x: x.is_file(), p.glob('**/*')) for p in path)

    # 해시값 저장
    for filepath in filepaths:
        filehash = file_hash(filepath, algorithm)
        hashs[filehash].append(filepath)
    return {k: v for k, v in hashs.items() if len(v) >= 2}


def format_output(out: Dict[bytes, List[Path]], file: TextIO=sys.stdout) -> None:
    for k, v in out.items():
        print(f'Duplicate file for hash {k.hex()}', file=file)
        print('\n'.join(str(x) for x in v), file=file)
        print('', file=file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', nargs=argparse.ONE_OR_MORE,
                        metavar='DIR', required=True, type=str,
                        help='파일이 저장된 경로')
    parser.add_argument('-a', '--algorithm', metavar='ALGORITHM',
                        type=str, help='해시를 계산할 알고리즘',
                        default='md5')
    parser.add_argument('-o', '--out', metavar='OUT',
                        type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout,
                        help='결과를 출력할 파일')
    args=parser.parse_args()
    format_output(find_duplicate(args.dir, algorithm=args.algorithm), args.out)
    args.out.close()
