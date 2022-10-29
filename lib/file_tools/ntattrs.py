"""
ntattrs: 윈도우 NT 파일 속성을 읽고 쓰는 함수들
"""
import ctypes
import sys
from collections.abc import Callable
from ctypes.wintypes import DWORD, HANDLE, LONG, LPCWSTR, WCHAR, WORD
from datetime import datetime, timedelta, timezone
from os import PathLike
from pathlib import Path
from stat import FILE_ATTRIBUTE_ARCHIVE, FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_NORMAL, \
    FILE_ATTRIBUTE_NOT_CONTENT_INDEXED, FILE_ATTRIBUTE_OFFLINE, FILE_ATTRIBUTE_READONLY, FILE_ATTRIBUTE_SYSTEM, \
    FILE_ATTRIBUTE_TEMPORARY
from typing import NamedTuple, Optional, Union

if sys.platform != 'win32':
    raise RuntimeError(f'`ntattrs` is available only for Windows.')

NT_EPOCH = datetime(1601, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


class FILETIME(ctypes.Structure):
    """NT 시스템의 파일 시각 구조체 (``1601-01-01T00:00:00Z`` 부터 경과한 100나노초 단위 틱)

    참고: https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-filetime
    """
    _fields_ = [
        ('dwLowDateTime', DWORD),
        ('dwHighDateTime', DWORD)
    ]


class SYSTEMTIME(ctypes.Structure):
    """TIME_ZONE_INFORMATION structure (timezoneapi.h)

    https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-systemtime
    """
    _fields_ = [
        ('wYear', WORD),
        ('wMonth', WORD),
        ('wDayOfWeek', WORD),
        ('wDay', WORD),
        ('wHour', WORD),
        ('wMinute', WORD),
        ('wSecond', WORD),
        ('wMilliseconds', WORD),
    ]


class TIME_ZONE_INFORMATION(ctypes.Structure):
    """TIME_ZONE_INFORMATION structure (timezoneapi.h)

    https://learn.microsoft.com/en-us/windows/win32/api/timezoneapi/ns-timezoneapi-time_zone_information
    """
    _fields_ = [
        ('Bias', LONG),
        ('StandardName', WCHAR * 32),
        ('StandardDate', SYSTEMTIME),
        ('StandardBias', LONG),
        ('DaylightName', WCHAR * 32),
        ('DaylightDate', SYSTEMTIME),
        ('DaylightBias', LONG)
    ]


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


def get_timezone() -> timezone:
    """시스템 시간대를 구한다.

    사용 가능 : Windows
    """
    time_zone_information = TIME_ZONE_INFORMATION(
        0, '\x00' * 32, SYSTEMTIME(0, 0, 0, 0, 0, 0, 0, 0), 0, '\x00' * 32, SYSTEMTIME(0, 0, 0, 0, 0, 0, 0, 0), 0
    )
    ctypes.windll.kernel32.GetTimeZoneInformation(ctypes.byref(time_zone_information))
    return timezone(timedelta(minutes=-time_zone_information.Bias))


def to_nt_timestamp(dt: datetime) -> int:
    r"""``datetime.datetime`` 객체를 NT 시스템 타임스탬프로 변환한다.

    만약 dt.tzinfo = None이라면 로컬 시간대로 간주하고 *시스템 시간대*\를 사용한다.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=get_timezone())
    delta: timedelta = (dt - NT_EPOCH)
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
    return FILETIME(ts & 0xffff_ffff, (ts >> 32) & 0xffff_ffff)


def from_time_struct(tst: FILETIME) -> datetime:
    return from_nt_timestamp(tst.dwLowDateTime + (tst.dwHighDateTime << 32))


def set_file_timestamp(path: Union[str, PathLike], ctime: Optional[datetime] = None, mtime: Optional[datetime] = None,
                       atime: Optional[datetime] = None, tst: Optional[FileTimeStamp] = None):
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
        raise FileNotFoundError(f'{path} cannot found.')
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
        HANDLE(0)  # hTemplateFile = NULL*
    )
    ctypes.windll.kernel32.SetFileTime(
        handle,
        ctypes.byref(to_time_struct(ctime)), ctypes.byref(to_time_struct(atime)), ctypes.byref(to_time_struct(mtime)))
    ctypes.windll.kernel32.CloseHandle(handle)


def get_file_timestamp(path: Union[str, PathLike]) -> FileTimeStamp:
    r"""파일/폴더의 타임스탬프를 가져온다. ``os.stat_result`` 클래스의 ``st_ctime``, ``st_mtime``, ``st_atime``

    Parameters
    ----------
    path : Path-like
        파일/폴더의 경로

    Returns
    -------
    ctime : datetime.datetime
        파일/폴더의 만든 시각
    mtime : datetime.datetime
        파일/폴더의 수정한 시각
    atime : datetime.datetime
        파일/폴더의 마지막 액세스 시각

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
        HANDLE(0)  # hTemplateFile = NULL*
    )
    ctime = FILETIME(0, 0)
    mtime = FILETIME(0, 0)
    atime = FILETIME(0, 0)
    ctypes.windll.kernel32.GetFileTime(handle, ctypes.byref(ctime), ctypes.byref(atime), ctypes.byref(mtime))
    ctypes.windll.kernel32.CloseHandle(handle)
    return FileTimeStamp(ctime=from_time_struct(ctime), mtime=from_time_struct(mtime), atime=from_time_struct(atime))


# ================ 파일 속성 함수 ================

def _check_flag_function(flag: int) -> Callable[[Union[str, PathLike]], bool]:
    def _check_flag(path: Union[str, PathLike]) -> bool:
        return bool(Path(path).stat().st_file_attributes & flag)

    return _check_flag


def _set_flag_function(flag: int) -> Callable[[Union[str, PathLike]], None]:
    def _set_flag(path: Union[str, PathLike]) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'{path} not found')

        abspath = path.resolve()
        new_flag = abspath.stat().st_file_attributes | flag
        ctypes.windll.kernel32.SetFileAttributesW(LPCWSTR(str(abspath)), DWORD(new_flag))

    return _set_flag


def _clear_flag_function(flag: int) -> Callable[[Union[str, PathLike]], None]:
    def _clear_flag(path: Union[str, PathLike]) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'{path} not found')

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
