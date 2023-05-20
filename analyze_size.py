"""
대상 폴더 내의 파일들의 크기를 분석하는 스크립트
"""
import argparse
from collections.abc import Iterable, Iterator
from pathlib import Path, PurePath
from typing import Literal, NamedTuple

MISC_FILES = '<MISC_FILES:{0}>'
MISC_FOLDERS = '<MISC_FOLDERS:{0}>'
KIBIBYTE = 1_024  # 2**10 bytes
MEBIBYTE = 1_048_576  # 2**20 bytes
GIBIBYTE = 1_073_741_824  # 2**30 bytes
TEBIBYTE = 1_099_511_627_776  # 2**40 bytes
PEBIBYTE = 1_125_899_906_842_624  # 2**50 bytes


class FolderInfo(NamedTuple):
    path: Path
    subfolders: list['FolderInfo']
    subfiles: list[Path]

    @property
    def size(self) -> int:
        return sum(p.stat().st_size for p in self.subfiles) + sum(subf.size for subf in self.subfolders)


def get_size(p: Path | FolderInfo) -> int:
    if isinstance(p, Path):
        return p.stat().st_size
    else:
        return p.size


class SizeReportRow(NamedTuple):
    path: Path
    size: int
    ratio: float
    ratio_current_level: float
    row_type: Literal['root', 'folder', 'file', 'various_folders', 'various_files']


def treeify(path: Path) -> FolderInfo:
    """대상 폴더의 내용을 트리로 만든다.
    """
    folders = [p for p in path.iterdir() if p.is_dir() and not p.is_symlink()]  # 심볼릭 링크는 제외한다.
    files = [p for p in path.iterdir() if p.is_file() and not p.is_symlink()]
    return FolderInfo(path, [treeify(folder) for folder in folders], files)


def _create_report_row(
        fi: FolderInfo, total_size: int, current_level_size: int, ratio_threshold: float = 0.05, folder_first=False
) -> Iterator[SizeReportRow]:
    # 기타 폴더의 총 크기와 갯수
    various_folder_size = 0
    various_folder_num = 0
    # 기타 파일의 총 크기와 갯수
    various_file_size = 0
    various_file_num = 0

    if folder_first:
        # folder_first=True일 경우 폴더 먼저 산출한 다음 파일을 산출한다.
        subfolders = sorted(fi.subfolders, key=get_size, reverse=True)
        subfiles = sorted(fi.subfiles, key=get_size, reverse=True)
        for item in subfolders:
            size = item.size
            if size / current_level_size >= ratio_threshold:
                # 만약 폴더 크기가 임계비율 이상이면 대상 폴더를 산출하고 하위 폴더의 내용들도 산출한다.
                yield SizeReportRow(item.path, size, size / total_size, size / current_level_size, 'folder')
                yield from _create_report_row(item, total_size, size, ratio_threshold, folder_first)
            else:
                # 그렇지 않다면 '기타 폴더'로 집계한다.
                various_folder_size += size
                various_folder_num += 1

        if various_folder_num:
            # 기타 폴더로 집계된 항목이 있다면 산출한다.
            yield SizeReportRow(
                fi.path / MISC_FOLDERS.format(various_folder_num), various_folder_size,
                various_folder_size / total_size, various_folder_size / current_level_size, 'various_folders'
            )

        for item in subfiles:
            size = item.stat().st_size
            if size / current_level_size >= ratio_threshold:
                # 만약 파일 크기가 임계비율 이상이면 대상 파일을 산출한다.
                yield SizeReportRow(item, size, size / total_size, size / current_level_size, 'file')
            else:
                # 그렇지 않다면 '기타 파일'로 집계한다.
                various_file_size += size
                various_file_num += 1

        if various_file_num:
            # 기타 파일로 집계된 항목이 있다면 산출한다.
            yield SizeReportRow(
                fi.path / MISC_FILES.format(various_file_num), various_file_size, various_file_size / total_size,
                various_file_size / current_level_size, 'various_files'
            )
    else:
        # folder_first=False일 경우 폴더와 파일을 합쳐서 내림차순으로 정렬한 다음 순회한다.
        items = sorted(fi.subfolders + fi.subfiles, key=get_size, reverse=True)  # noqa # 이 합치기는 의도된 것이다
        for item in items:
            size = get_size(item)
            if isinstance(item, Path):
                # 파일: 타입이 Path
                if size / current_level_size >= ratio_threshold:
                    yield SizeReportRow(item, size, size / total_size, size / current_level_size, 'file')
                else:
                    various_file_size += size
                    various_file_num += 1
            else:
                # 폴더: 타입이 FolderInfo
                if size / current_level_size >= ratio_threshold:
                    yield SizeReportRow(item.path, size, size / total_size, size / current_level_size, 'folder')
                    yield from _create_report_row(item, total_size, size, ratio_threshold, folder_first)
                else:
                    various_folder_size += size
                    various_folder_num += 1

        # 모든 항목을 산출한 다음에는 기타 항목들을 산출한다.
        if various_folder_num:
            yield SizeReportRow(
                fi.path / MISC_FOLDERS.format(various_folder_num), various_folder_size,
                various_folder_size / total_size, various_folder_size / current_level_size, 'various_folders'
            )
        if various_file_num:
            yield SizeReportRow(
                fi.path / MISC_FILES.format(various_file_num), various_file_size, various_file_size / total_size,
                various_file_size / current_level_size, 'various_files'
            )


def create_report_row(fi: FolderInfo, ratio_threshold: float = 0.05, folder_first=False) -> Iterator[SizeReportRow]:
    yield SizeReportRow(fi.path, fi.size, 1.0, 1.0, 'root')
    yield from _create_report_row(fi, fi.size, fi.size, ratio_threshold, folder_first)


def simply_path(p: PurePath, override_folder: bool = False) -> str:
    parts = p.parts
    if (len_parts := len(parts)) == 0:
        return '.'
    else:
        return '| ' * (len_parts - 1) + p.name + '/' * override_folder


def format_size(i: int) -> str:
    if i >= PEBIBYTE:
        unit_num, unit = PEBIBYTE, 'PiB'
    elif i >= TEBIBYTE:
        unit_num, unit = TEBIBYTE, 'TiB'
    elif i >= GIBIBYTE:
        unit_num, unit = GIBIBYTE, 'GiB'
    elif i >= MEBIBYTE:
        unit_num, unit = MEBIBYTE, 'MiB'
    elif i >= KIBIBYTE:
        unit_num, unit = KIBIBYTE, 'KiB'
    else:
        unit_num, unit = 1, 'B'

    pre_decimal_point_nums = len(str(i // unit_num))
    post_decimal_point_nums = 4 - pre_decimal_point_nums
    if unit_num == 1:
        return f'{i} {unit}'
    else:
        return f'{i / unit_num:{pre_decimal_point_nums}.{post_decimal_point_nums}f} {unit}'


def print_row(rows: Iterable[SizeReportRow], home_path: Path, simply=False) -> None:
    for row in rows:
        match row.row_type:
            case 'file' | 'various_files':
                path_repr = simply_path(row.path.relative_to(home_path)) if simply \
                    else row.path.relative_to(home_path).as_posix()
            case 'folder' | 'various_folders':
                path_repr = simply_path(row.path.relative_to(home_path), True) if simply \
                    else row.path.relative_to(home_path).as_posix() + '/'
            case _:  # 'root'
                path_repr = 'sandbox'
        print(f'{path_repr}\t{format_size(row.size)}\t{row.ratio:.2%}\t{row.ratio_current_level:.2%}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='PATH', type=str, help='대상 경로')
    parser.add_argument('-d', '--directory-first', action='store_true', dest='dir_first',
                        help='폴더를 먼저 표시할 지 여부')
    parser.add_argument('-r', '--ratio', dest='ratio_threshold', type=int, default=1,
                        help='대상 % 이하의 값(0...100, 0일 경우 모든 항목을 보여준다.)')
    parser.add_argument('-t', '--tree', action='store_true', dest='tree', help='트리를 간략하게 보여줄 지 여부')

    args = parser.parse_args()
    args_path = Path(args.path)
    args_ratio = (0 if args.ratio_threshold < 0 else 100 if args.ratio_threshold > 100 else args.ratio_threshold) / 100

    print_row(create_report_row(treeify(args_path), args_ratio, args.dir_first), args_path, args.tree)
