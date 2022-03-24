import hashlib
from os import PathLike
from typing import Union, overload

T_Pathifyable = Union[str, PathLike]
HASH_BLOCK_SIZE = 65536
FILESIZE_UNITS_DECIMAL = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
FILESIZE_UNITS_BINARY = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]


@overload
def get_file_hash(path: T_Pathifyable) -> bytes:
    ...


@overload
def get_file_hash(path: T_Pathifyable, algorithm: str, **kwargs) -> bytes:
    ...


def get_file_hash(path: T_Pathifyable, algorithm: str = "sha256", **kwargs) -> bytes:
    """파일의 해시를 계산한다.

    Parameters
    ----------
    path : Path-like
        계산할 파일의 경로
    algorithm : str, optional
        해시를 계산할 때 사용할 알고리즘. 생략한다면 SHA256을 사용한다.
    kwargs
        추가 옵션. ``hashlib.new``에서 해시를 계산할 때 사용할 수 있는 옵션들이다.

    Returns
    -------
    h : bytes
        계산된 파일의 해시
    """
    hash_obj = hashlib.new(algorithm, **kwargs)
    with open(path, "rb") as f:
        while True:
            buffer = f.read(HASH_BLOCK_SIZE)
            if not buffer:
                break
            hash_obj.update(buffer)
    return hash_obj.digest()


def repr_file_size(size: int, *, binary: bool = True, decimal: int = 1) -> str:
    """바이트 단위의 size에 단위를 붙여서 읽기 쉽게 한다.

    Parameters
    ----------
    size : int
        파일의 크기(bytes)
    binary : bool
        만약 True일 경우 1024 단위 접두사를 붙임. 만약 False일 경우 1000 단위 접두사를 붙임
    decimal : int
        소수점 아래로 몇 자리까지 표시할 지 여부

    Returns
    -------
    s : str
        파일 크기를 표현.

    EXAMPLE
    >>> repr_file_size(12345678)   # 12345678byte에 1024 단위 접두사를 붙인다.
    '11.8 MiB'
    >>> repr_file_size(12345678, binary=False)   # 12345678byte에 1000 단위 접두사를 붙인다.
    '12,3 MB'
    """
    if not (isinstance(size, int)):
        raise TypeError("size는 정수여야 합니다.")

    if binary:
        units = FILESIZE_UNITS_BINARY
        base = 1024
    else:
        units = FILESIZE_UNITS_DECIMAL
        base = 1000

    exp = 0  # base ** exp
    while size >= base:
        size /= base
        exp += 1

    if exp == 0:
        return "{size} {unit_symbol}".format(size=size, unit_symbol=units[exp])
    else:
        return "{size:.{decimal}f} {unit_symbol}".format(decimal=decimal, size=size, unit_symbol=units[exp])
