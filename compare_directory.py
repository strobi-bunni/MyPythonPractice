#!/usr/bin/env python
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
'@' - 비교 결과 미정(일반적으로는 볼 수 없음)

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
from typing import Iterable, Iterator, List, NamedTuple, Tuple, Union

# 비교 결과를 나타내기 위한 기호
RESULT_SAME = "="  # 같은 대상
RESULT_CREATED = "+"  # 생성됨
RESULT_DELETED = "-"  # 삭제됨
RESULT_DIFFER = "!"  # 날짜는 같지만 서로 다름(orig != diff)
RESULT_NEWER = "<"  # diff의 파일이 최신임(orig.mtime < diff.mtime)
RESULT_OLDER = ">"  # orig의 파일이 최신임(orig.mtime > diff.mtime)
RESULT_UNDEFINED = "@"  # 알 수 없음

HEADER_PREFIX = "#"

# 경로의 타입을 나타내기 위한 기호
PATHTYPE_DIRECTORY = "D"
PATHTYPE_FILE = "F"
PATHTYPE_MOUNT = "M"
PATHTYPE_SYMLINK = "L"
PATHTYPE_BLOCKDEV = "B"
PATHTYPE_CHARDEV = "C"
PATHTYPE_FIFO = "I"
PATHTYPE_SOCKET = "S"

PATHTYPE_SORT_ORDER = {
    PATHTYPE_DIRECTORY: 1,
    PATHTYPE_FILE: 2,
    PATHTYPE_MOUNT: 2,
    PATHTYPE_SYMLINK: 2,
    PATHTYPE_BLOCKDEV: 2,
    PATHTYPE_CHARDEV: 2,
    PATHTYPE_FIFO: 2,
    PATHTYPE_SOCKET: 2,
}
PATHTYPE_GROUP_ID = {
    PATHTYPE_DIRECTORY: 1,
    PATHTYPE_FILE: 0,
    PATHTYPE_MOUNT: 3,
    PATHTYPE_SYMLINK: 2,
    PATHTYPE_BLOCKDEV: 3,
    PATHTYPE_CHARDEV: 3,
    PATHTYPE_FIFO: 3,
    PATHTYPE_SOCKET: 3,
}
RESULT_FULL_NAMES = {
    RESULT_SAME: "Same",
    RESULT_CREATED: "Created",
    RESULT_DELETED: "Deleted",
    RESULT_NEWER: "Newer",
    RESULT_OLDER: "Older",
    RESULT_DIFFER: "Differ",
    RESULT_UNDEFINED: "Undefined",
}
COLORED_OUTPUT_CODE_MAPPING = {
    RESULT_SAME: "\x1b[39m",
    RESULT_CREATED: "\x1b[92m",
    RESULT_DELETED: "\x1b[91m",
    RESULT_DIFFER: "\x1b[95m",
    RESULT_NEWER: "\x1b[96m",
    RESULT_OLDER: "\x1b[93m",
    RESULT_UNDEFINED: "\x1b[90m",
    HEADER_PREFIX: "\x1b[1m",
}
RESULT_ALPHABETIC_SYMBOLS = {
    "s": RESULT_SAME,
    "c": RESULT_CREATED,
    "d": RESULT_DELETED,
    "i": RESULT_DIFFER,
    "n": RESULT_NEWER,
    "o": RESULT_OLDER,
    "u": RESULT_UNDEFINED,
}


class CompareResult(NamedTuple):
    path: PurePath  # orig, diff에 대한 상대 경로
    item_type: str  # PATHTYPE_*
    compare_result: str  # RESULT_*

    def __str__(self):
        return (
            f"{self.compare_result}{self.item_type}  "
            f"{path_to_string(self.path, override_is_dir=(self.item_type == PATHTYPE_DIRECTORY))}"
        )

    # 기본 정렬 순서
    def __lt__(self, other):
        return path_to_string(self.path) < path_to_string(other.path)


def compare_dir(
    orig: Path, diff: Path, working_dir: PurePath = PurePath("."), collapse_dir: bool = False
) -> Iterator[CompareResult]:
    """두 폴더 orig와 diff의 내용을 비교해서 그 결과를 result 글로벌 변수에 저장한다.

    Parameters
    ----------
    orig : pathlib.Path
        원본 경로
    diff : pathlib.Path
        대상 경로
    working_dir : pathlib.PurePath
        반환된 결과를 저장할 때 기본이 되는 상대 경로(기본값은 '.')
    collapse_dir : bool
        생성되거나 삭제된 폴더의 내부 항목을 간략하게 표시할 지 여부. 기본값은 False

    Yields
    ------
    cmp : CompareResult
        각각의 항목에 대해서 비교한 결과
    """
    dcmp = dircmp(orig, diff)
    # 이름과 내용이 같은 파일들을 처리한다.
    for name in dcmp.same_files:
        orig_item = orig / name
        yield CompareResult(working_dir / name, get_type(orig_item), RESULT_SAME)

    # 이름은 같지만 내용이 다른 파일들을 처리한다.
    for name in dcmp.diff_files:
        orig_item = orig / name
        diff_item = diff / name

        # 파일의 수정 시각을 비교해서 newer 혹은 older를 판단한다.
        compare_result_type = (
            RESULT_NEWER
            if orig_item.stat().st_mtime < diff_item.stat().st_mtime
            else RESULT_OLDER
            if orig_item.stat().st_mtime > diff_item.stat().st_mtime
            else RESULT_DIFFER
        )
        yield CompareResult(working_dir / name, get_type(orig_item), compare_result_type)

    # 동일한 폴더를 찾는다.(폴더의 이름이 동일한지의 여부, 안의 내용은 상관없다.)
    for name in dcmp.common_dirs:
        yield CompareResult(working_dir / name, PATHTYPE_DIRECTORY, RESULT_SAME)
        # 안의 내용물을 재귀적으로 계산한다.
        yield from compare_dir(orig / name, diff / name, working_dir / name, collapse_dir=collapse_dir)

    # src에만 있는 항목들을 찾아서 deleted로 저장한다.
    for name in dcmp.left_only:
        # orig에만 있는 항목들과 (만약 collapse_dir가 지정되어 있다면) 하위 항목들을 전부 deleted로 간주한다.
        yield from mark_item_recursive(name, orig, RESULT_DELETED, working_dir, collapse_dir=collapse_dir)

    # dst에만 있는 항목들을 찾아서 created로 저장한다.
    for name in dcmp.right_only:
        # diff에만 있는 항목들과 (만약 collapse_dir가 지정되어 있다면) 하위 항목들을 전부 created로 간주한다.
        # 만약에 폴더라면 안의 내용들을 전부 deleted로 간주한다.
        yield from mark_item_recursive(name, diff, RESULT_CREATED, working_dir, collapse_dir=collapse_dir)

    # 형식이 다르거나 비교할 수 없는 항목들을 찾는다.
    for name in dcmp.common_funny:
        orig_type = get_type(orig / name)
        diff_type = get_type(diff / name)
        # 만약에 타입이 다르다면 orig의 항목들을 deleted로, diff의 항목들을 created로 간주한다.
        if orig_type != diff_type:
            yield from mark_item_recursive(name, orig, RESULT_DELETED, working_dir, collapse_dir=collapse_dir)
            yield from mark_item_recursive(name, diff, RESULT_CREATED, working_dir, collapse_dir=collapse_dir)

        # 만약 타입이 같다면 비교할 수 없다고 간주한다.
        else:
            yield CompareResult(working_dir / name, orig_type, RESULT_UNDEFINED)


def mark_item_recursive(
    name: str, target_dir: Path, result: str, working_dir: PurePath, collapse_dir: bool = False
) -> Iterator[CompareResult]:
    """폴더 target_dir 안의 항목 name의 비교 결과를 result로 표시한다.
    이 때 하위 항목들의 path에 대한 하위 항목들의 상대 경로는 working_dir 폴더 안의 경로로 산출된다.

    만약 target_dir/name이 폴더일 경우:
    - collapse_dir이 True일 경우 target_dir/name 안의 항목도 재귀적으로 result로 표시한다.
    - collapse_dir이 False일 경우 target_dir/name 항목만을 산출한다.
    """
    if (target_dir / name).is_dir() and not collapse_dir:
        yield from mark_recursive(target_dir / name, result, working_dir / name)
    else:
        yield CompareResult(working_dir / name, get_type(target_dir / name), result)


def mark_recursive(path: Path, result: str, working_dir=PurePath(".")) -> Iterator[CompareResult]:
    """폴더 path와 path안의 모든 하위 항목들의 비교 결과를 result로 표시한다.
    이 때 하위 항목들의 path에 대한 하위 항목들의 상대 경로는 working_dir 폴더 안의 경로로 산출된다.
    """
    yield CompareResult(working_dir, get_type(path), result)
    for item in path.iterdir():
        if item.is_dir():
            yield from mark_recursive(item, result, working_dir / item.name)
        else:
            yield CompareResult(working_dir / item.name, get_type(item), result)


def get_type(p: Path) -> str:
    """경로 p의 유형을 구한다.

    Parameters
    ----------
    p : pathlib.Path
        대상 경로

    Returns
    -------
    type_ : str
        경로의 유형
    """
    return_type = (
        PATHTYPE_FILE
        if p.is_file()
        else PATHTYPE_DIRECTORY
        if p.is_dir()
        else PATHTYPE_SYMLINK
        if p.is_symlink()
        else PATHTYPE_BLOCKDEV
        if p.is_block_device()
        else PATHTYPE_CHARDEV
        if p.is_char_device()
        else PATHTYPE_FIFO
        if p.is_fifo()
        else PATHTYPE_SOCKET
        if p.is_socket()
        else PATHTYPE_MOUNT  # p.is_mount() raises NotImplementedError on Windows
    )
    return return_type


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
        return_list.append(
            CompareResult(path=parent_path, item_type=PATHTYPE_DIRECTORY, compare_result=RESULT_UNDEFINED)
        )
    return_list.append(x)
    return return_list


def sort_key_for_directory_first(x: CompareResult) -> List[Tuple[int, str]]:
    r"""폴더가 위에 오도록 정렬하기 위한 키 함수이다.

    이 함수는 리스트를 반환하며, 정렬을 시행할 경우 각각의 리스트들은 사전 순서대로 정렬한다.

    리스트의 각각의 값은 폴더가 우선시되도록 정렬하기 위한 튜플이며, 그 튜플의 값은 다음과 같다.

    - 첫 번째 값은 폴더이면 1, 폴더가 아니면 2의 값을 가진다. 따라서 사전 순으로 정렬할 때 폴더가 위에 온다.
    - 두 번째 값은 대상의 이름이다. 따라서 같은 폴더거나, 같은 파일이면 이름대로 위에 온다.
    """
    return [(PATHTYPE_SORT_ORDER[_result.item_type], _result.path.name) for _result in expand_parents_of_result(x)]


def path_to_string(path: Union[Path, PurePath], override_is_dir=False) -> str:
    """경로를 문자열로 변경한다.

    Path.as_posix()과는 다른 점은 폴더일 때는 뒤에 슬래시가 붙는다는 점이다.

    override_is_dir는 is_dir()를 쓸 수 없을 때 폴더임을 나타내기 위한 값이다.
    """
    p = path.as_posix()
    is_dir = (isinstance(path, Path) and path.is_dir()) or (isinstance(path, PurePath) and override_is_dir)
    if is_dir:
        p += "/"
    return p


def colored_output(x: str) -> str:
    for prefix, color_code in COLORED_OUTPUT_CODE_MAPPING.items():
        if x.startswith(prefix):
            return color_code + x + "\x1b[0m"
    return x


def yield_summary_row(res: Iterable[CompareResult]) -> Iterator[str]:
    cnt = Counter((r.compare_result, PATHTYPE_GROUP_ID[r.item_type]) for r in res)
    for compare_result in [
        RESULT_SAME,
        RESULT_CREATED,
        RESULT_DELETED,
        RESULT_NEWER,
        RESULT_OLDER,
        RESULT_DIFFER,
        RESULT_UNDEFINED,
    ]:
        yield (
            f"{compare_result} {RESULT_FULL_NAMES[compare_result]:<10} "
            f"{cnt[(compare_result, 0)]:>6d}{PATHTYPE_FILE} / {cnt[(compare_result, 1)]:>5d}{PATHTYPE_DIRECTORY} / "
            f"{cnt[(compare_result, 2)]:>3d}{PATHTYPE_SYMLINK} / {cnt[(compare_result, 3)]:>3d}Others"
        )


def parse_filter_syntax(filter_syntax: str) -> str:
    """필터 문자열을 해석하기 위한 중간 함수"""
    filter_syntax = filter_syntax.lower()
    if filter_syntax == "all":
        return (
            RESULT_SAME
            + RESULT_CREATED
            + RESULT_DELETED
            + RESULT_OLDER
            + RESULT_NEWER
            + RESULT_DIFFER
            + RESULT_UNDEFINED
        )

    return "".join(RESULT_ALPHABETIC_SYMBOLS.get(c, c) for c in filter_syntax)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("orig", metavar="ORIG_DIR", type=str, help="비교의 대상이 될 원본 폴더")
    parser.add_argument("diff", metavar="DIFF_DIR", type=str, help="변경 내용이 있는 대상 폴더")
    parser.add_argument("-r", "--reverse", action="store_true", dest="reverse", help="원본 폴더와 대상 폴더를 뒤바꿉니다.")
    parser.add_argument("-c", "--color", action="store_true", dest="color", help="색상으로 표시합니다.")
    parser.add_argument("-d", "--directory-first", action="store_true", dest="dir_first", help="폴더를 먼저 표시할 지 여부")
    parser.add_argument("-s", "--summary", action="store_true", dest="summary", help="요약을 출력합니다.")
    parser.add_argument(
        "-f",
        "--filter",
        dest="filter_syntax",
        type=str,
        default="+-!<>@",
        help="대상 결과만을 보여줍니다.\n= + - ! < > @(혹은 S C D I N O U)\n중 하나 이상을 조합합니다.",
    )
    parser.add_argument(
        "-C", "--collapse-directory", action="store_true", dest="collapse_dir", help="생성되거나 삭제된 폴더를 간략하게 표시합니다."
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        type=argparse.FileType("w", encoding="utf-8"),
        default=sys.stdout,
        help="출력할 파일",
    )

    args = parser.parse_args()

    # 원본 폴더와 대상 폴더 설정
    orig_dir, diff_dir = Path(args.orig), Path(args.diff)
    if args.reverse:
        orig_dir, diff_dir = diff_dir, orig_dir

    # 헤더 출력
    header_src = f"#ORIG: {path_to_string(orig_dir)}"
    if args.color:
        header_src = colored_output(header_src)
    header_tgt = f"#DIFF: {path_to_string(diff_dir)}"
    if args.color:
        header_tgt = colored_output(header_tgt)
    print(f"{header_src}\n{header_tgt}\n", file=args.output_file)

    sort_key = sort_key_for_directory_first if args.dir_first else None
    result = sorted(compare_dir(orig_dir, diff_dir, collapse_dir=args.collapse_dir), key=sort_key)

    # 결과 출력
    for i in result:
        if i.compare_result in parse_filter_syntax(args.filter_syntax):
            result_text = colored_output(str(i)) if args.color else str(i)
            print(result_text, file=args.output_file)

    # 요약본 출력
    if args.summary:
        print(file=args.output_file)
        for summary_text in yield_summary_row(result):
            print(colored_output(summary_text) if args.color else summary_text, file=args.output_file)

    if args.output_file is not sys.stdout:
        args.output_file.close()
