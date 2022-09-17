"""해시 값을 사용해서 중복되는 파일 찾기

사용법 : find_duplicate_files.py [-h] -d DIR [DIR ...] [-a ALGORITHM] [-o OUT]
"""
import argparse
import hashlib
import sys
from collections import defaultdict
from itertools import chain
from os import PathLike
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, TextIO

HASH_BLOCK_SIZE = 65536


def file_hash(filename: PathLike, algorithm='sha256', **kwargs) -> bytes:
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
        while buffer := hashfile.read(HASH_BLOCK_SIZE):
            h.update(buffer)
    return h.digest()


def find_duplicate(*paths: PathLike, algorithm='md5') -> Dict[bytes, List[Path]]:
    """중복된 파일을 찾는다.

    Parameters
    ----------
    paths : path-like object, or iterable of path-like object
        파일이 저장된 폴더 경로
    algorithm : str : optional
        사용할 해시 알고리즘

    Returns
    -------
    dupes : dict
        중복된 파일의 리스트
        키는 파일 해시이며 값은 중복된 해시를 갖는 파일 경로의 리스트이다.
    """
    hashes = defaultdict(list)  # 파일 해시를 저장할 딕셔너리

    # 파일 경로 리스트
    paths = [Path(p) for p in paths]
    filepaths = chain.from_iterable(filter(lambda x: x.is_file(), p.glob('**/*')) for p in paths)

    # 해시값 저장
    for filepath in filepaths:
        filehash = file_hash(filepath, algorithm)
        hashes[filehash].append(filepath)
    return {k: v for k, v in hashes.items() if len(v) >= 2}


def format_output(out: Mapping[bytes, Iterable[Path]], file: TextIO = sys.stdout) -> None:
    for k, v in out.items():
        print(f'Duplicate file for hash {k.hex()}', file=file)
        print('\n'.join(str(x) for x in v), file=file)
        print('', file=file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs=argparse.ONE_OR_MORE, metavar='DIR', type=str, help='파일이 저장된 경로')
    parser.add_argument('-a', '--algorithm', metavar='ALGORITHM', type=str, help='해시를 계산할 알고리즘',
                        default='md5', choices=('md5', 'sha1', 'sha224', 'sha256'))
    parser.add_argument('-o', '--out', metavar='OUT', type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout, help='결과를 출력할 파일')
    args = parser.parse_args()
    format_output(find_duplicate(*args.dir, algorithm=args.algorithm), args.out)
    args.out.close()
