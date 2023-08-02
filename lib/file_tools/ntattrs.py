"""
ntattrs: 윈도우 NT 파일 속성을 읽고 쓰는 함수들
"""
import ctypes
import sys
from collections.abc import Callable
from ctypes.wintypes import DWORD, HANDLE, LPCWSTR
from datetime import datetime, timedelta, timezone
from os import PathLike
from pathlib import Path
from stat import (
    FILE_ATTRIBUTE_ARCHIVE,
    FILE_ATTRIBUTE_HIDDEN,
    FILE_ATTRIBUTE_NORMAL,
    FILE_ATTRIBUTE_NOT_CONTENT_INDEXED,
    FILE_ATTRIBUTE_OFFLINE,
    FILE_ATTRIBUTE_READONLY,
    FILE_ATTRIBUTE_SYSTEM,
    FILE_ATTRIBUTE_TEMPORARY,
)
from typing import NamedTuple, Optional, Union

if sys.platform != "win32":
    raise RuntimeError(f"`ntattrs` is available only for Windows.")

NT_EPOCH = datetime(1601, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
# Windows에서 datetime.astimezone이 오류를 일으키지 않는 최소 시각
UNIX_SAFE_TIME = datetime(1970, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
BIAS = UNIX_SAFE_TIME - NT_EPOCH + timedelta(days=2)


def astimezone_safer(dt: datetime, tz: Optional[timezone] = None) -> datetime:
    try:
        return dt.astimezone(tz)
    except OSError:
        modified_dt = dt + BIAS
        modified_dt = modified_dt.astimezone(tz)
        return modified_dt - BIAS


class FILETIME(ctypes.Structure):
    """NT 시스템의 파일 시각 구조체 (``1601-01-01T00:00:00Z`` 부터 경과한 100나노초 단위 틱)

    참고: https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-filetime
    """

    _fields_ = [("dwLowDateTime", DWORD), ("dwHighDateTime", DWORD)]


class FileTimeStamp(NamedTuple):
    ctime: Optional[datetime] = None
    mtime: Optional[datetime] = None
    atime: Optional[datetime] = None

    # aliases for Windows filename attributes
    @property
    def CreationTime(self):
        return self.ctime

    @property
    def LastWriteTime(self):
        return self.mtime

    @property
    def LastAccessTime(self):
        return self.atime


def to_nt_timestamp(dt: datetime) -> int:
    r"""``datetime.datetime`` 객체를 NT 시스템 타임스탬프로 변환한다.

    만약 dt.tzinfo = None이라면 로컬 시간대로 간주하고 *시스템 시간대*\를 사용한다.
    """
    delta: timedelta = astimezone_safer(dt, timezone.utc) - NT_EPOCH
    return (delta.days * 86400 + delta.seconds) * 10_000_000 + delta.microseconds * 10


def from_nt_timestamp(ts: int) -> datetime:
    """NT 시스템 타임스탬프를 ``datetime.datetime`` 객체로 변환한다.

    이 때의 시간대는 UTC이다.

    NOTE: 마이크로초 이하 단위는 사라진다.
    """
    microseconds = ts // 10
    days_part = microseconds // 86_400_000_000
    seconds_part = microseconds % 86_400_000_000 // 1_000_000
    microseconds_part = microseconds % 1_000_000
    return NT_EPOCH + timedelta(days=days_part, seconds=seconds_part, microseconds=microseconds_part)


def to_time_struct(dt: Optional[datetime]) -> FILETIME:
    if dt is None:
        return FILETIME(0, 0)
    ts = to_nt_timestamp(dt)
    return FILETIME(ts & 0xFFFF_FFFF, (ts >> 32) & 0xFFFF_FFFF)


def from_time_struct(tst: FILETIME) -> datetime:
    return from_nt_timestamp(tst.dwLowDateTime + (tst.dwHighDateTime << 32))


def set_timestamp(
    path: Union[str, PathLike],
    ctime: Optional[datetime] = None,
    mtime: Optional[datetime] = None,
    atime: Optional[datetime] = None,
    tst: Optional[FileTimeStamp] = None,
):
    r"""파일/폴더의 타임스탬프를 설정한다.

    Parameters
    ----------
    path : Path-like
        파일/폴더의 경로
    ctime : datetime.datetime : Optional
        파일/폴더의 만든 시각(기본값: ``None``)
        만약 바꾸고 싶지 않다면 ``None``\으로 설정한다.
    mtime : datetime.datetime : Optional
        파일/폴더의 수정한 시각(기본값: ``None``)
        만약 바꾸고 싶지 않다면 ``None``\으로 설정한다.
    atime : datetime.datetime : Optional
        파일/폴더의 마지막 액세스 시각(기본값: ``None``)
        만약 바꾸고 싶지 않다면 ``None``\으로 설정한다.\
    tst : FileTimeStamp : Optional
        타임스탬프 객체.
        만약 ``tst``\가 주어지고 ``ctime``, ``mtime``, ``atime`` 중 하나 이상이 주어지면
        ``tst.ctime``, ``tst.mtime`` 또는 ``tst.atime``은 해당 값으로 대체된다.

    Notes
    -----
    이 함수는 Win32 API의 `SetFileTime`_ 함수의 래핑 함수이다.

    .. _`SetFileTime` : https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfiletime
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} cannot found.")
    filepath = str(path.resolve())

    if tst is None:
        tst = FileTimeStamp(ctime=None, mtime=None, atime=None)

    # 쇼트 서킷 논리
    ctime = tst.ctime or ctime
    mtime = tst.mtime or mtime
    atime = tst.atime or atime

    # FILE_WRITE_ATTRIBUTES from https://learn.microsoft.com/en-us/windows/win32/fileio/file-access-rights-constants
    # CreateFileW: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
    handle: HANDLE = ctypes.windll.kernel32.CreateFileW(
        LPCWSTR(filepath),  # lpFileName
        DWORD(0x180),  # dwDesiredAccess = FILE_WRITE_ATTRIBUTES | FILE_READ_ATTRIBUTES
        DWORD(0x0),  # dwShareMode = OPEN_EXISTING
        HANDLE(0),  # lpSecurityAttributes = NULL*
        DWORD(0x3),  # dwCreationDisposition = OPEN_EXISTING
        DWORD(0x0),  # dwFlagsAndAttributes = 0
        HANDLE(0),  # hTemplateFile = NULL*
    )
    ctypes.windll.kernel32.SetFileTime(
        handle,
        ctypes.byref(to_time_struct(ctime)),
        ctypes.byref(to_time_struct(atime)),
        ctypes.byref(to_time_struct(mtime)),
    )
    ctypes.windll.kernel32.CloseHandle(handle)


def get_timestamp(path: Union[str, PathLike]) -> FileTimeStamp:
    r"""파일/폴더의 타임스탬프를 가져온다. ``os.stat_result`` 클래스의 ``st_ctime``, ``st_mtime``, ``st_atime``

    Parameters
    ----------
    path : Path-like
        파일/폴더의 경로

    Returns
    -------
    timestamp: FileTimeStamp
        (ctime, mtime, atime) 네임드 튜플. 각각의 값은 datetime.datetime 객체이다.

    Notes
    -----
    이 함수는 Win32 API의 `GetFileTime`_ 함수의 래핑 함수이다.

    .. _`GetFileTime` : https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfiletime
    """
    path = Path(path)
    filepath = str(path.resolve())

    # FILE_WRITE_ATTRIBUTES from https://learn.microsoft.com/en-us/windows/win32/fileio/file-access-rights-constants
    # CreateFileW: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
    handle: HANDLE = ctypes.windll.kernel32.CreateFileW(
        LPCWSTR(filepath),  # lpFileName
        DWORD(0x180),  # dwDesiredAccess = FILE_WRITE_ATTRIBUTES | FILE_READ_ATTRIBUTES
        DWORD(0x0),  # dwShareMode = OPEN_EXISTING
        HANDLE(0),  # lpSecurityAttributes = NULL*
        DWORD(0x3),  # dwCreationDisposition = OPEN_EXISTING
        DWORD(0x0),  # dwFlagsAndAttributes = 0
        HANDLE(0),  # hTemplateFile = NULL*
    )
    ctime = FILETIME(0, 0)
    mtime = FILETIME(0, 0)
    atime = FILETIME(0, 0)
    ctypes.windll.kernel32.GetFileTime(handle, ctypes.byref(ctime), ctypes.byref(atime), ctypes.byref(mtime))
    ctypes.windll.kernel32.CloseHandle(handle)
    return FileTimeStamp(ctime=from_time_struct(ctime), mtime=from_time_struct(mtime), atime=from_time_struct(atime))


# Alias for compatibility
get_file_timestamp = get_timestamp
set_file_timestamp = set_timestamp

# ================ 파일 속성 함수 ================


SET_FILE_ATTRIBUTE_MASK = (
    FILE_ATTRIBUTE_ARCHIVE
    | FILE_ATTRIBUTE_HIDDEN
    | FILE_ATTRIBUTE_NORMAL
    | FILE_ATTRIBUTE_NOT_CONTENT_INDEXED
    | FILE_ATTRIBUTE_OFFLINE
    | FILE_ATTRIBUTE_READONLY
    | FILE_ATTRIBUTE_SYSTEM
    | FILE_ATTRIBUTE_TEMPORARY
)


def set_attribute(path: Union[str, PathLike], flag: int) -> None:
    """파일/폴더에 해당 속성을 설정한다. 기존의 속성값은 무시되며, flag로 지정된 새 속성으로 덮어씌워진다.

    예를 들어 어떤 파일의 속성이 0x21 (``ARCHIVE | READONLY``)일 시
    새 flag 값을 0x92(``DIRECTORY | NORMAL | HIDDEN``)으로 지정할 경우
    대상 파일의 속성은 0x02 (``HIDDEN``)으로 재지정된다.

    Parameters
    ----------
    path : Path-like
        파일/폴더의 경로
    flag : int
        파일/폴더의 속성 플래그. 하나 이상의 플래그를 Bitwise OR 연산자로 한번에 지정할 수 있다.

        다음 플래그만을 지원하며 이 밖의 플래그는 무시된다.

        - ``FILE_ATTRIBUTE_ARCHIVE``(0x20) : 보관
        - ``FILE_ATTRIBUTE_HIDDEN``(0x2) : 숨김
        - ``FILE_ATTRIBUTE_NORMAL``(0x80) : 일반 (이 속성은 단독으로 지정되었을 때에만 유효하다)
        - ``FILE_ATTRIBUTE_NOT_CONTENT_INDEXED``(0x2000) : 인덱스 안함
        - ``FILE_ATTRIBUTE_OFFLINE``(0x1000) : 오프라인
        - ``FILE_ATTRIBUTE_READONLY``(0x1) : 읽기 전용
        - ``FILE_ATTRIBUTE_SYSTEM``(0x4) : 시스템
        - ``FILE_ATTRIBUTE_TEMPORARY``(0x100) : 임시 파일

    Notes
    -----
    이 함수는 Win32 API의 `SetFileAttributesW`_ 함수의 래핑 함수이다.

    .. _`SetFileAttributesW` : https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileattributesw
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    abspath = path.resolve()
    new_flag = flag
    ctypes.windll.kernel32.SetFileAttributesW(LPCWSTR(str(abspath)), DWORD(new_flag))


def _check_flag_function(flag: int) -> Callable[[Union[str, PathLike]], bool]:
    def _check_flag(path: Union[str, PathLike]) -> bool:
        return bool(Path(path).stat().st_file_attributes & flag)

    return _check_flag


def _set_flag_function(flag: int) -> Callable[[Union[str, PathLike]], None]:
    def _set_flag(path: Union[str, PathLike]) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"{path} not found")

        abspath = path.resolve()
        new_flag = abspath.stat().st_file_attributes | flag
        ctypes.windll.kernel32.SetFileAttributesW(LPCWSTR(str(abspath)), DWORD(new_flag))

    return _set_flag


def _clear_flag_function(flag: int) -> Callable[[Union[str, PathLike]], None]:
    def _clear_flag(path: Union[str, PathLike]) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"{path} not found")

        abspath = path.resolve()
        new_flag = abspath.stat().st_file_attributes & ~flag
        ctypes.windll.kernel32.SetFileAttributesW(LPCWSTR(str(abspath)), DWORD(new_flag))

    return _clear_flag


# check FILE_ATTRIBUTE_* flags functions
is_archive = _check_flag_function(FILE_ATTRIBUTE_ARCHIVE)
is_hidden = _check_flag_function(FILE_ATTRIBUTE_HIDDEN)
is_normal = _check_flag_function(FILE_ATTRIBUTE_NORMAL)
is_not_content_indexed = _check_flag_function(FILE_ATTRIBUTE_NOT_CONTENT_INDEXED)
is_offline = _check_flag_function(FILE_ATTRIBUTE_OFFLINE)
is_readonly = _check_flag_function(FILE_ATTRIBUTE_READONLY)
is_system = _check_flag_function(FILE_ATTRIBUTE_SYSTEM)
is_temporary = _check_flag_function(FILE_ATTRIBUTE_TEMPORARY)

# set FILE_ATTRIBUTE_* flags functions
set_archive = _set_flag_function(FILE_ATTRIBUTE_ARCHIVE)
set_hidden = _set_flag_function(FILE_ATTRIBUTE_HIDDEN)
set_normal = _set_flag_function(FILE_ATTRIBUTE_NORMAL)
set_not_content_indexed = _set_flag_function(FILE_ATTRIBUTE_NOT_CONTENT_INDEXED)
set_offline = _set_flag_function(FILE_ATTRIBUTE_OFFLINE)
set_readonly = _set_flag_function(FILE_ATTRIBUTE_READONLY)
set_system = _set_flag_function(FILE_ATTRIBUTE_SYSTEM)
set_temporary = _set_flag_function(FILE_ATTRIBUTE_TEMPORARY)

# clear FILE_ATTRIBUTE_* flags functions
clear_archive = _clear_flag_function(FILE_ATTRIBUTE_ARCHIVE)
clear_hidden = _clear_flag_function(FILE_ATTRIBUTE_HIDDEN)
clear_normal = _clear_flag_function(FILE_ATTRIBUTE_NORMAL)
clear_not_content_indexed = _clear_flag_function(FILE_ATTRIBUTE_NOT_CONTENT_INDEXED)
clear_offline = _clear_flag_function(FILE_ATTRIBUTE_OFFLINE)
clear_readonly = _clear_flag_function(FILE_ATTRIBUTE_READONLY)
clear_system = _clear_flag_function(FILE_ATTRIBUTE_SYSTEM)
clear_temporary = _clear_flag_function(FILE_ATTRIBUTE_TEMPORARY)
