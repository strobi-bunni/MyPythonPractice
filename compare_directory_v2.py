"""
결과는 다음과 같이 표시됩니다.

{비교 결과}{종류}  {상대 경로}

비교 결과는 다음과 같은 기호로 표시됩니다.
'=' - 같음(-i 옵션을 지정해야만 표시됩니다.)
'+' - SOURCE_DIR에는 없지만 DEST_DIR에 있는 항목
'-' - SOURCE_DIR에는 있지만 DEST_DIR에 없는 항목
'<' - DEST_DIR에 있는 항목이 SOURCE_DIR에 있는 해당 항목보다 최신
'>' - DEST_DIR에 있는 항목이 SOURCE_DIR에 있는 해당 항목보다 오래됨
'!' - SOURCE_DIR와 DEST_DIR에 있는 항목이 서로 다르지만 날짜가 같음
'@' - 비교 결과 미정

항목의 종류는 다음과 같은 기호로 표시됩니다.

'D' - 폴더
'F' - 파일
'M' - 마운트 장치
'L' - 심볼릭 링크
'B' - 블록 장치
'C' - 문자 장치
'I' - FIFO
'S' - 소켓

예를 들어 '+F'는 생성된 파일, '-D'는 삭제된 폴더를 의미합니다.
"""
import argparse
import sys
from collections import Counter
from filecmp import dircmp
from pathlib import Path, PurePath
from typing import Callable, Iterator, List, Literal, NamedTuple, Tuple, Union

T_ItemTypes = Literal['directory', 'file', 'mount', 'symlink', 'blockdev', 'chardev', 'fifo', 'socket']
T_CompareResultTypes = Literal['same', 'created', 'deleted', 'diff', 'newer', 'older', 'undefined']
item_type_abbrev = {'directory': 'D', 'file': 'F', 'mount': 'M', 'symlink': 'L',
                    'blockdev': 'B', 'chardev': 'C', 'fifo': 'I', 'socket': 'S'}
compare_result_abbrev = {'same': '=', 'created': '+', 'deleted': '-', 'diff': '!',
                         'newer': '<', 'older': '>', 'undefined': '@'}
item_type_sort_order = {'directory': 1, 'file': 2, 'mount': 2, 'symlink': 2,
                        'blockdev': 2, 'chardev': 2, 'fifo': 2, 'socket': 2}
item_type_group_id = {'directory': 1, 'file': 0, 'mount': 3, 'symlink': 2,
                      'blockdev': 3, 'chardev': 3, 'fifo': 3, 'socket': 3}

compare_result_color_code = {'same': '\033[39m', 'created': '\033[92m', 'deleted': '\033[91m',
                             'diff': '\033[95m', 'newer': '\033[96m', 'older': '\033[93m',
                             'undefined': '\033[90m'}


class CompareResult(NamedTuple):
    path: PurePath
    item_type: T_ItemTypes
    compare_result: T_CompareResultTypes

    def __str__(self):
        return f'{compare_result_abbrev[self.compare_result]}{item_type_abbrev[self.item_type]}  ' \
               f'{path_to_string(self.path, override_is_dir=(self.item_type == "directory"))}'


def compare_dir(src: Path, dst: Path, working_dir: PurePath = PurePath('.')) -> Iterator[CompareResult]:
    """두 폴더 src와 dst의 내용을 비교해서 그 결과를 result 글로벌 변수에 저장한다.

    Parameters
    ----------
    src : pathlib.Path
        원본 경로
    dst : pathlib.Path
        대상 경로
    working_dir : pathlib.PurePath
        반환된 결과를 저장할 때 기본이 되는 상대 경로(기본값은 '.')

    Yields
    ------
    cmp : CompareResult
        각각의 항목에 대해서 비교한 결과
    """
    dcmp = dircmp(src, dst)
    # 이름과 내용이 같은 파일들을 처리한다.
    for name in dcmp.same_files:
        src_item = src / name
        yield CompareResult(working_dir / name, get_type(src_item), 'same')

    # 이름은 같지만 내용이 다른 파일들을 처리한다.
    for name in dcmp.diff_files:
        src_item = src / name
        dst_item = dst / name

        # 파일의 수정 시각을 비교해서 newer 혹은 older를 판단한다.
        compare_result_type = 'newer' if dst_item.stat().st_mtime > src_item.stat().st_mtime \
            else 'older' if dst_item.stat().st_mtime < src_item.stat().st_mtime \
            else 'diff'
        yield CompareResult(working_dir / name, get_type(src_item), compare_result_type)  # noqa

    # 동일한 폴더를 찾는다.(폴더의 이름이 동일한지의 여부, 안의 내용은 상관없다.)
    for name in dcmp.common_dirs:
        yield CompareResult(working_dir / name, 'directory', 'same')
        # 안의 내용물을 재귀적으로 계산한다.
        yield from compare_dir(src / name, dst / name, working_dir / name)

    # src에만 있는 항목들을 찾아서 deleted로 저장한다.
    for name in dcmp.left_only:
        yield CompareResult(working_dir / name, get_type(src / name), 'deleted')

        # 만약에 폴더라면 안의 내용들을 전부 deleted로 간주한다.
        if (src / name).is_dir():
            yield from mark_as_deleted_recursive((src / name), working_dir / name)

    # dst에만 있는 항목들을 찾아서 created로 저장한다.
    for name in dcmp.right_only:
        yield CompareResult(working_dir / name, get_type(dst / name), 'created')
        # 만약에 폴더라면 안의 내용들을 전부 created로 간주한다.
        if (dst / name).is_dir():
            yield from mark_as_created_recursive((dst / name), working_dir / name)

    # 형식이 다르거나 비교할 수 없는 항목들을 찾는다.
    for name in dcmp.common_funny:
        src_type = get_type(src / name)
        dst_type = get_type(dst / name)
        # 만약에 타입이 다르다면 src의 항목들을 deleted로, dst의 항목들을 created로 간주한다.
        if src_type != dst_type:
            yield CompareResult(working_dir / name, src_type, 'deleted')
            yield CompareResult(working_dir / name, dst_type, 'created')
            if src_type == 'directory':
                yield from mark_as_deleted_recursive((src / name), working_dir / name)
            if dst_type == 'directory':
                yield from mark_as_created_recursive((dst / name), working_dir / name)
        # 만약 타입이 같다면 비교할 수 없다고 간주한다.
        else:
            yield CompareResult(working_dir / name, src_type, 'undefined')


def mark_as_deleted_recursive(path: Path, working_dir=PurePath('.')) -> Iterator[CompareResult]:
    for item in path.glob('**/*'):
        yield CompareResult(working_dir / (item.relative_to(path)), get_type(item), 'deleted')


def mark_as_created_recursive(path: Path, working_dir=PurePath('.')) -> Iterator[CompareResult]:
    for item in path.glob('**/*'):
        yield CompareResult(working_dir / (item.relative_to(path)), get_type(item), 'created')


def get_type(p: Path) -> T_ItemTypes:
    """경로 p의 유형을 구한다.

    Parameters
    ----------
    p : pathlib.Path
        대상 경로

    Returns
    -------
    type_ : {'directory', 'file', 'mount', 'symlink', 'blockdev', 'chardev', 'fifo', 'socket'}
        경로의 유형
    """
    if p.is_file():
        return 'file'  # noqa
    elif p.is_dir():
        return 'directory'  # noqa
    elif p.is_mount():
        return 'mount'  # noqa
    elif p.is_symlink():
        return 'symlink'  # noqa
    elif p.is_block_device():
        return 'blockdev'  # noqa
    elif p.is_char_device():
        return 'chardev'  # noqa
    elif p.is_fifo():
        return 'fifo'  # noqa
    else:
        return 'socket'  # noqa


def get_result_abbrev(x: CompareResult) -> str:
    """

    :param x:
    :return:
    """
    return compare_result_abbrev[x.compare_result] + item_type_abbrev[x.item_type]


def expand_parents_of_result(x: CompareResult) -> List[CompareResult]:
    r"""비교 결과 x의 부모 디렉토리를 전개한다.
    예를 들어 x가 ``+F  /path/to/file.txt``\라면 다음과 같은 식으로 전개한다.

    ::

        @D  /
        @D  /path/
        @D  /path/to/
        +f  /path/to/file.txt
    """
    return_list: List[CompareResult] = []
    for parent_path in reversed(x.path.parents):
        return_list.append(CompareResult(path=parent_path, item_type='directory', compare_result='undefined'))
    return_list.append(x)
    return return_list


def sort_key_for_directory_first(x: CompareResult) -> List[Tuple[int, str]]:
    r"""폴더가 위에 오도록 정렬하기 위한 키 함수이다.
    
    이 함수는 리스트를 반환하며, 정렬을 시행할 경우 각각의 리스트들은 사전 순서대로 정렬한다.
    
    리스트의 각각의 값은 폴더가 우선시되도록 정렬하기 위한 튜플이며, 그 튜플의 값은 다음과 같다.

    - 첫 번째 값은 폴더이면 1, 폴더가 아니면 2의 값을 가진다. 따라서 사전 순으로 정렬할 때 폴더가 위에 온다.
    - 두 번째 값은 대상의 이름이다. 따라서 같은 폴더거나, 같은 파일이면 이름대로 위에 온다.
    """
    return [(item_type_sort_order[_result.item_type], _result.path.name) for _result in expand_parents_of_result(x)]


def path_to_string(path: Union[Path, PurePath], override_is_dir=False) -> str:
    """경로를 문자열로 변경한다.

    Path.as_posix()과는 다른 점은 폴더일 때는 뒤에 슬래시가 붙는다는 점이다.

    override_is_dir는 is_dir()를 쓸 수 없을 때 폴더임을 나타내기 위한 값이다.
    """
    p = path.as_posix()
    is_dir = (isinstance(path, Path) and path.is_dir()) or (isinstance(path, PurePath) and override_is_dir)
    if is_dir:
        p += '/'
    return p


def print_result(x: CompareResult, colored=False, file=sys.stdout):
    color_code_prefix = compare_result_color_code[x.compare_result] if colored else ''
    color_code_suffix = '\033[0m' if colored else ''
    name = path_to_string(x.path, override_is_dir=(x.item_type == 'directory'))
    print(f'{color_code_prefix}{get_result_abbrev(x):<4}{name}{color_code_suffix}', file=file)


def print_summary(res: List[CompareResult], colored=False, file=sys.stdout):
    cnt = Counter((r.compare_result, item_type_group_id[r.item_type]) for r in res)
    for compare_result in ['same', 'created', 'deleted', 'newer', 'older', 'diff', 'undefined']:
        color_code_prefix = compare_result_color_code[compare_result] if colored else ''
        color_code_suffix = '\033[0m' if colored else ''
        print(f'{color_code_prefix}[{compare_result_abbrev[compare_result]}]{compare_result:<10}'
              f'{cnt[(compare_result, 0)]:>6d} Files | {cnt[(compare_result, 1)]:>5d} Folders | '
              f'{cnt[(compare_result, 2)]:>3d} Symlinks | {cnt[(compare_result, 3)]:>3d} Others{color_code_suffix}',
              file=file)


def print_header(source_path: Path, dest_path: Path, colored=False, file=sys.stdout):
    title_color_code_prefix = '\033[1m' if colored else ''
    title_color_code_suffix = '\033[0m' if colored else ''
    print(f'{title_color_code_prefix}Source: {path_to_string(source_path)}{title_color_code_suffix}', file=file)
    print(f'{title_color_code_prefix}Dest:   {path_to_string(dest_path)}{title_color_code_suffix}', file=file)


def get_filter_pred(filter_syntax: str) -> Callable[[CompareResult], bool]:
    compare_result_types_to_output = []
    for (k, v) in compare_result_abbrev.items():
        if v in filter_syntax:
            compare_result_types_to_output.append(k)
    return lambda x: x.compare_result in compare_result_types_to_output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', metavar='SOURCE_DIR', type=str, help='원본 폴더')
    parser.add_argument('dest', metavar='DEST_DIR', type=str, help='대상 폴더')
    parser.add_argument('-c', '--color', action='store_true', dest='color', help='색상으로 표시합니다.')
    parser.add_argument('-i', '--include-same-files', action='store_true', dest='include_same_files',
                        help='같은 파일들을 출력합니다.')
    parser.add_argument('-s', '--summary', action='store_true', dest='summary', help='요약을 출력합니다.')
    parser.add_argument('-f', '--filter', dest='filter_syntax', type=str, default='=+-!<>@',
                        help='대상 결과만을 보여줍니다.\n= + - ! < > @ 중 하나 이상을 조합합니다.')
    parser.add_argument('-o', '--output', dest='output_file', type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout, help='출력할 파일')

    args = parser.parse_args()

    src_dir, dst_dir = Path(args.source), Path(args.dest)
    print_header(src_dir, dst_dir, colored=args.color, file=args.output_file)
    print(file=args.output_file)

    result = sorted(compare_dir(src_dir, dst_dir), key=sort_key_for_directory_first)

    filter_pred = get_filter_pred(args.filter_syntax)
    for i in result:
        if i.compare_result != 'same' or args.include_same_files:
            # Short circuit logic: i.compare_result!=same이거나 i.compare_result==same and args.include_same_files일때
            if filter_pred(i):
                print_result(i, colored=args.color, file=args.output_file)

    if args.summary:
        print(file=args.output_file)
        print_summary(result, colored=args.color, file=args.output_file)
