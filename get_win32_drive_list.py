r"""
다음 코드는 Windows API를 사용해서 시스템 상의 파티션의 리스트를 구한다.
"""
import ctypes
import re
import shutil
from ctypes.wintypes import DWORD, LPCWSTR, LPDWORD, LPWSTR
from enum import IntEnum, IntFlag
from string import ascii_uppercase
from typing import List, NamedTuple


class DriveType(IntEnum):
    """드라이브 타입

    https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getdrivetypea
    """
    DRIVE_UNKNOWN = 0
    DRIVE_NO_ROOT_DIR = 1
    DRIVE_REMOVABLE = 2
    DRIVE_FIXED = 3
    DRIVE_REMOTE = 4
    DRIVE_CDROM = 5
    DRIVE_RAMDISK = 6


class FileSystemFlags(IntFlag):
    """파일 시스템의 플래그

    https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationw
    """
    FILE_CASE_SENSITIVE_SEARCH = 0x1
    FILE_CASE_PRESERVED_NAMES = 0x2
    FILE_UNICODE_ON_DISK = 0x4
    FILE_PERSISTENT_ACLS = 0x8
    FILE_FILE_COMPRESSION = 0x10
    FILE_VOLUME_QUOTAS = 0x20
    FILE_SUPPORTS_SPARSE_FILES = 0x40
    FILE_SUPPORTS_REPARSE_POINTS = 0x80
    FILE_VOLUME_IS_COMPRESSED = 0x8000
    FILE_SUPPORTS_OBJECT_IDS = 0x10000
    FILE_SUPPORTS_ENCRYPTION = 0x20000
    FILE_NAMED_STREAMS = 0x40000
    FILE_READ_ONLY_VOLUME = 0x80000
    FILE_SEQUENTIAL_WRITE_ONCE = 0x100000
    FILE_SUPPORTS_TRANSACTIONS = 0x200000
    FILE_SUPPORTS_HARD_LINKS = 0x400000
    FILE_SUPPORTS_EXTENDED_ATTRIBUTES = 0x800000
    FILE_SUPPORTS_OPEN_BY_FILE_ID = 0x1000000
    FILE_SUPPORTS_USN_JOURNAL = 0x2000000
    FILE_SUPPORTS_BLOCK_REFCOUNTING = 0x8000000
    FILE_DAX_VOLUME = 0x20000000


class DriveInfo(NamedTuple):
    drive_letter: str  # 드라이브 문자, 후행 역슬래시 포함(예: 'C:\\')
    drive_label: str  # 드라이브 라벨(예: 'Windows')
    volume_serial_number: int  # 볼륨 일련 번호(cmd에서 dir를 실행했을 때의 값과 같다)
    filesystem_flags: FileSystemFlags  # 파일 시스템의 플래그
    filesystem_name: str  # 파일 시스템 이름(예: 'NTFS')


regex_drive_letter = re.compile(r'^([A-Z])(?::\\?)?$', re.I)


def normalize_drive_letter(letter: str, trailing_backslash=True) -> str:
    r"""``r'C'``, ``r'C:'``, ``r'C:\'`` 와 같은 드라이브 문자 형식을 통일된 형식으로 바꾼다.

    trailing_backslash = True일 경우 ``r'C:\'``형식으로 바꾸고, False일 경우 ``r'C:'`` 형식으로 바꾼다.
    """
    if matches := regex_drive_letter.match(letter):
        suffix = ':\\' if trailing_backslash else ':'
        return matches[1].upper() + suffix


def get_drive_letters() -> List[str]:
    """현재 컴퓨터에 있는 드라이브 문자 리스트를 구한다.

    이 함수는 WinAPI의 `GetLogicalDrives`_ 함수의 래핑 함수이다.

    .. _`GetLogicalDrives` : https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getlogicaldrives

    Examples
    --------
    >>> get_drive_letters()   # 컴퓨터에 따라 다를 수 있음
    ['C', 'D', 'E']
    """
    drive_list_bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    # drive_list_bitmask는 현재 컴퓨터에 설치된 드라이브 리스트의 비트 마스크
    # {0x1: 'A:\\', 0x2: 'B:\\', 0x4: 'C:\\', 0x8: 'D:\\', ...}
    return [ascii_uppercase[i] for i in range(26) if drive_list_bitmask & (1 << i)]


def get_drive_type(letter: str) -> DriveType:
    r"""드라이브 타입을 구한다.

    Parameters
    ----------
    letter : str
        드라이브 문자. ``r'C'``, ``r'C:'``, ``r'C:\'`` 형식 중 아무거나 써도 된다.

    Returns
    -------
    drive_type : DriveType
        드라이브 타입을 나타내는 열거형

    Notes
    -----
    이 함수는 WinAPI의 `GetDriveTypeW`_ 함수의 래핑 함수이다.

    .. _GetDriveTypeW : https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getdrivetypew
    """
    return DriveType(ctypes.windll.kernel32.GetDriveTypeW(LPCWSTR(normalize_drive_letter(letter))))


def get_drive_info(letter: str) -> DriveInfo:
    r"""윈도우 드라이브 정보를 구한다.

    Parameters
    ----------
    letter : str
        드라이브 문자. ``r'C'``, ``r'C:'``, ``r'C:\'`` 형식 중 아무거나 써도 된다.

    Returns
    -------
    info : DriveInfo
        드라이브 정보

    Notes
    -----
    이 함수는 WinAPI의 `GetVolumeInformationW`_ 함수의 래핑 함수이다.

    .. _`GetVolumeInformationW` : https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationw
    """
    lp_root_path_name = LPCWSTR(normalize_drive_letter(letter))
    lp_volume_name_buffer = LPWSTR('\x00' * 255)
    n_volume_name_size = DWORD(256)
    lp_volume_serial_number = LPDWORD(DWORD(0))
    lp_maximum_component_length = LPDWORD(DWORD(0))
    lp_file_system_flags = LPDWORD(DWORD(0))
    lp_file_system_name_buffer = LPWSTR('\x00' * 255)
    n_file_system_name_size = DWORD(256)

    ctypes.windll.kernel32.GetVolumeInformationW(
        lp_root_path_name, lp_volume_name_buffer, n_volume_name_size, lp_volume_serial_number,
        lp_maximum_component_length, lp_file_system_flags, lp_file_system_name_buffer, n_file_system_name_size
    )
    return DriveInfo(lp_root_path_name.value, lp_volume_name_buffer.value, lp_volume_serial_number.contents.value,
                     FileSystemFlags(lp_file_system_flags.contents.value), lp_file_system_name_buffer.value)


def simplified_filesystem_flag(flag: FileSystemFlags) -> str:
    """플래그를 약어로 표시한다.

    참고 : 공식적인 약어는 아니다
    """
    flag_abbrs = ['C', 'PN', 'U', 'ACL', 'CO', 'Q', 'SP', 'RP', 'ISCO', 'OID', 'ENC', 'NS', 'RO', 'WO', 'TR', 'HL',
                  'XA', 'OPENID', 'USN', 'BR', 'DAX']  # 플래그 약어
    strs = []
    for abbr, value in zip(flag_abbrs, sorted((x.value for x in FileSystemFlags.__members__.values()))):
        if flag & value:
            strs.append(abbr)
        else:
            strs.append(''.join(' ' for _ in abbr))  # 같은 크기의 공백으로 대체
    return f"Flags: {' '.join(strs)}".strip()


def format_percent_to_bar(ratio: float, width: int = 79, fillchar: str = '@', emptychar: str = '.') -> str:
    r"""0 이상 1 이하의 비율 ratio을 막대로 표시한다.

    Parameters
    ----------
    ratio : number-like
        표시할 비율. 0 이상 1 이하로 제한된다.
    width : int
        바의 길이. 기본값은 터미널 최대 폭보다 1 작아서 줄바꿈을 일으키지 않는 최대 크기인 79로 설정했다.
    fillchar : str
        채울 문자.
    emptychar : str
        비어 있는 공간을 표시하기 위한 문자

    Returns
    -------
    bar : str
        막대로 표시한 비율

    Examples
    --------
    >>> for r in [0.0, 0.5, 0.3, 0.8, 0.6, 1.0]:
    ...     print(format_percent_to_bar(r, 10, fillchar='#', emptychar='-'))
    ----------
    #####-----
    ###-------
    ########--
    ######----
    ##########
    """
    # ratio를 0 이상 1 이하로 제한한다.
    ratio = 1.0 if ratio > 1 else 0.0 if ratio < 0 else ratio

    length_of_bar = round(ratio * width)
    bar = fillchar * length_of_bar
    return f'{bar:{emptychar}<{width}}'


def print_drive_info(letter: str, width: int = 77) -> None:
    """드라이브 정보를 보기 쉽게 출력한다.
    """
    drive_type = get_drive_type(letter)
    drive_info = get_drive_info(letter)
    print(f'{drive_info.drive_label} ({normalize_drive_letter(letter, trailing_backslash=False)})\n'
          f'{drive_type.name}, {drive_info.filesystem_name}\n'
          f'{simplified_filesystem_flag(drive_info.filesystem_flags)}')
    try:
        disk_usage = shutil.disk_usage(letter + ':')
    except OSError:
        print('Drive not available')
    else:
        use_ratio = disk_usage.used / disk_usage.total
        print(f'{disk_usage.used / 1073741824:.1f} GiB used / '
              f'{disk_usage.free / 1073741824:.1f} GiB free / '
              f'{disk_usage.total / 1073741824:.1f} GiB total '
              f'({use_ratio:.1%})')
        print(f'[{format_percent_to_bar(use_ratio, width=width)}]')


if __name__ == '__main__':
    # 터미널 크기를 구한다.
    terminal_width = shutil.get_terminal_size().columns

    for drive_letter in get_drive_letters():
        # 바의 전체 길이('[', ']' 제외)는 줄바꿈을 일으키지 않는 최대 길이인 터미널폭-3으로 한다.
        print_drive_info(drive_letter, terminal_width - 3)
        print()
