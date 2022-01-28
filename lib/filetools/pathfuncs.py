import os
from collections.abc import Callable, Iterator
from itertools import chain, filterfalse
from pathlib import Path
from typing import Any, Optional, Union

from ..iterable_tools.custom_itertools import common_starts

T_Pathifyable = Union[str, os.PathLike]
T_PathIter = Iterator[Path]


def get_dir_size(path: T_Pathifyable) -> int:
    """폴더 ``path``의 크기를 계산한다.

    Parameters
    ----------
    path : str, optional
        크기를 계산할 폴더. 기본값은 현재 작업 폴더이다.

    Returns
    -------
    total_size : size
        폴더 ``path``의 모든 파일들의 크기의 합
    """
    path = Path(path)
    if not path.is_dir():
        raise ValueError(f'{path} is not a directory.')

    return sum(p.stat().st_size for p in path.glob('**/*'))


def path_walker(path: T_Pathifyable, *, dir_first: bool = True,
                sort_keys: Callable[[Path], Any] = None, reverse: bool = False) -> T_PathIter:
    """path 아래의 모든 폴더와 파일을 산출하는 이터레이터

    Parameters
    ----------
    path : Path-like object
        산출할 파일의 경로
    dir_first : bool, optional
        폴더를 먼저 산출할지의 여부, 기본값은 True
    sort_keys : function, optional
        정렬할 기준
    reverse : bool, optional
        역순으로 정렬할지의 여부

    Yields
    ------
    p : Path
        경로 리스트
    """
    # 파일 필터가 없으면 항상 참인 것으로 간주
    path: Path = Path(path)

    # dir_first 여부에 따라서 정렬을 한다.
    if dir_first:
        # 자식(not 자손) 폴더와 파일 경로 리스트
        folders_list: T_PathIter = (p for p in path.iterdir() if p.is_dir())
        files_list: T_PathIter = (p for p in path.iterdir() if p.is_file())

        if sort_keys is None:
            # 정렬 안함
            paths_list: T_PathIter = chain(folders_list, files_list)
        else:
            # 정렬함
            paths_list: T_PathIter = chain(sorted(folders_list, key=sort_keys, reverse=reverse),
                                           sorted(files_list, key=sort_keys, reverse=reverse))
    else:
        # 파일/폴더 여부에 관계없이 배열
        items_list: T_PathIter = (p for p in path.iterdir() if p.is_file() or p.is_dir())
        if sort_keys is None:
            # 정렬 안함
            paths_list: T_PathIter = items_list
        else:
            # 정렬함
            paths_list: T_PathIter = sorted(items_list, key=sort_keys, reverse=reverse)

    # 재귀적으로 실행
    items = chain.from_iterable(([p] if p.is_file()
                                 else (
        path_walker(p, dir_first=dir_first, sort_keys=sort_keys, reverse=reverse))) for p in paths_list)
    return chain([path], items)


def relative_level(target: T_Pathifyable, ref: T_Pathifyable, resolve: bool = True) -> Optional[int]:
    """target 폴더가 ref 폴더에 비해 얼마나 하위 경로인지 계산한다.

    Parameters
    ----------
    target : Path-like object
        대상 경로
    ref : Path-like object
        기준 경로
    resolve : bool, optional
        모든 심볼릭 링크 관계를 풀고 상대 경로를 절대 경로로 변환할지의 여부. 기본값은 True

    Returns
    -------
    level : int : Optional
        양수일 경우 target이 ref의 하위 디렉토리이며 그 상대적인 단계를 반환한다.
        음수일 경우 target이 ref의 상위 디렉토리이며 그 상대적인 단계를 반환한다.
        0일 경우 target과 ref이 같은 디렉토리 안에 있다.
        None일 경우 둘 중 어느 하나도 다른 쪽의 포함 관계가 아닐 때

    Examples
    --------
    >>> relative_level('./test/test.py', '.')   # `target` path is "child" of `ref` path.
    2
    >>> relative_level('.', './..')   # `target` path is "parent" of `ref` path.
    -1
    >>> relative_level('./test1.py', './test2.py')   # `target` path is "sibling" of `ref` path.
    0
    """
    target_path = Path(target)
    ref_path = Path(ref)
    # resolve가 있다면 절대 경로로 변경한다.
    if resolve:
        target_path = target_path.resolve()
        ref_path = ref_path.resolve()

    # 1. target이 ref의 하위 폴더인지 검사
    if ref_path in target_path.parents:
        return len(target_path.relative_to(ref_path).parts)
    # 2. ref이 target의 하위 폴더인지 검사
    elif target_path in ref_path.parents:
        return -len(ref_path.relative_to(target_path).parts)
    # 3. target과 ref이 같은 상위 폴더를 가지는지 검사
    elif target_path.parent == ref_path.parent:
        return 0
    # 4. 어디에도 해당되지 않다면 None 발생
    else:
        return None


def common_parent(*paths: T_Pathifyable, resolve: bool = False) -> Path:
    """여러 개의 path에서 공통된 상위 경로를 찾는다.

    Parameters
    ----------
    paths : Path-like object
        경로
    resolve : bool : Optional
        각각의 path에서 공통된 경로를 찾을 지 여부

    Returns
    -------
    parent : Path
        공통된 상위 경로

    Exceptions
    ----------
    ValueError
        경로들이 공통된 드라이브에 있지 않을 경우(Windows)

    Examples
    --------
    Posix 환경에서
    >>> from pathlib import PosixPath
    >>> common_parent(PosixPath('/usr/lib'), PosixPath('/usr/local/lib'))
    PosixPath('/usr')

    Windows 환경에서
    >>> from pathlib import WindowsPath
    >>> common_parent(WindowsPath("C:/Users/Public"), WindowsPath("C:/Users/user"))
    WindowsPath('C:\\Users')

    한편 Windows에서 경로들이 같은 드라이브 상에 있지 않을 경우 오류를 반환한다.
    >>> from pathlib import WindowsPath
    >>> common_parent(WindowsPath("C:"), WindowsPath("D:"))
    Traceback (most recent call last):
      ...
    ValueError: Paths don't have the same drive
    """
    paths: list[Path] = [Path(path) for path in paths]
    if resolve:
        paths = [p.resolve() for p in paths]
    paths_parts: list[tuple[str, ...]] = [p.parts for p in paths]
    common_parts: list[str] = list(common_starts(*paths_parts))

    if not common_parts:
        raise ValueError("Paths don't have the same drive")
    return Path(os.sep.join(common_parts))


def is_empty_folder(path: T_Pathifyable) -> bool:
    """대상 폴더가 빈 폴더인지 여부를 반환한다.

    *빈 폴더* 는 대상 폴더 안에 파일이 없으면서, 대상 폴더 안에 하위 폴더가 있을 경우
    모든 하위 폴더가 *빈 폴더* 인 경우를 뜻한다.

    Parameters
    ----------
    path : Path-like
        대상 폴더

    Returns
    -------
    is_empty : bool
        대상 폴더가 빈 폴더일 경우 True를 반환한다.

    Exceptions
    ----------
    NotADirectoryError
        path가 폴더가 아닐 경우
    """
    path = Path(path)
    items = list(path.iterdir())
    folders, not_folders = filter(Path.is_dir, items), filterfalse(Path.is_dir, items)

    return not list(not_folders) and all(is_empty_folder(p) for p in folders)
