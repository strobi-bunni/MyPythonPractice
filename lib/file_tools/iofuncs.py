from os import PathLike
from pathlib import Path
from typing import Optional, Union, overload

T_Pathifyable = Union[str, PathLike]


@overload
def rename(path: T_Pathifyable, new_file_nameonly: str) -> Path: ...


@overload
def rename(path: T_Pathifyable, new_file_nameonly: str, new_file_ext: str) -> Path: ...


def rename(path: T_Pathifyable, new_file_nameonly: str, new_file_ext: Optional[str] = None) -> Path:
    """파일 이름을 바꾸는 더 쉬운 함수.

    파일이 저장된 폴더를 보존한 채 파일 이름만 바꾼다.
    파일 이름을 변경한 이후에는 이름이 변경된 파일의 절대경로를 반환한다.

    Parameters
    ----------
    path : Path-like
        이름을 바꿀 파일의 절대 경로
    new_file_nameonly : str
        경로, 확장자를 제외한 바꿀 파일 이름
    new_file_ext : str, optional
        바꿀 파일 확장자, **온점 포함**. 만약 생략한다면 확장자를 바꾸지 않음

    Returns
    -------
    new_path : Path
        바꾼 파일 이름

    Notes
    -----
    이 함수는 파일의 이름을 바꾸는 부작용(Side Effect)이 있다. 따라서 순수한 함수가 아니다.

    Examples
    --------
    >>> rename('~/document/test.txt', 'hello')
    '~/document/hello.txt'
    >>> rename('~/document/hello.txt', 'world', '.py')
    '~/document/world.py'
    """
    path = Path(path)
    new_ext = new_file_ext if new_file_ext else path.suffix
    new_path = path.with_name(new_file_nameonly + new_ext)
    path.rename(new_path)
    return new_path


def dummy_copytree(path: T_Pathifyable, dest_path: T_Pathifyable) -> None:
    """
    폴더 경로 path의 모든 파일과 폴더를 dest_path로 복사한다.
    다만 파일은 0바이트의 더미 파일로 복사한다.

    이 함수는 파일 시스템 작업 테스트용 데이터를 생성할 때 유용하다.
    """
    path = Path(path)
    dest_path = Path(dest_path)

    # path 오류 처리
    if not path.exists():
        raise FileNotFoundError(f'{path} cannot found.')
    if not path.is_dir():
        raise NotADirectoryError(f'{path} is not a directory.')

    dest_path.mkdir(parents=True, exist_ok=True)

    for subpath in path.glob('**/*'):
        relative_subpath = subpath.relative_to(path)
        if subpath.is_dir():
            (dest_path / relative_subpath).mkdir(parents=True, exist_ok=True)
        else:
            (dest_path / relative_subpath).touch(exist_ok=True)


__all__ = ['dummy_copytree', 'rename']
