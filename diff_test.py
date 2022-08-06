import argparse
import difflib
from itertools import repeat
from typing import Iterator, List, Literal, NamedTuple, Optional, Union

marker_abbr = {'equal': '  ', 'insert': '+ ', 'delete': '- ', 'replace': '@ '}
marker_color_code = {'equal': '\033[39m', 'insert': '\033[92m', 'delete': '\033[91m', 'replace': '\033[93m'}


def int_str_length(i: int) -> int:
    """정수 1를 문자열로 나타냈을 때의 글자 수

    >>> int_str_length(30)   # len('30')
    2
    >>> int_str_length(-100)   # len('-100')
    4
    """
    return len(str(i))


def int_right_align(i: int, length: int) -> str:
    """정수를 오른쪽 정렬한다.
    """
    return '{i:>{length}}'.format(i=i, length=length)


class DifferGroupHeader(NamedTuple):
    source_starts: int  # 원본 줄 번호의 시작점(1부터 시작)
    source_length: int  # 원본 줄 번호
    dest_starts: int  # 대상 줄 번호의 시작점(1부터 시작)
    dest_length: int  # 대상 줄 길이

    def __str__(self):
        source_str = f'{self.source_starts},{self.source_length}' if self.source_length > 1 else f'{self.source_starts}'
        dest_str = f'{self.dest_starts},{self.dest_length}' if self.dest_length > 1 else f'{self.dest_starts}'
        return f'@@ -{source_str} +{dest_str} @@'


class DifferLine(NamedTuple):
    source_line_no: Optional[int] = None  # 원본의 줄 번호(1부터 시작)
    dest_line_no: Optional[int] = None  # 대상의 줄 번호(1부터 시작)
    marker: Literal['equal', 'replace', 'insert', 'delete'] = 'equal'
    string: str = ''


def get_diff_group_header(group) -> DifferGroupHeader:
    """unified_diff로 출력된 각 그룹의 위치를 DifferGroupHeader로 나타낸다.

    :param group:
    :return:
    """
    source_starts = group[0][1] + 1
    source_length = group[-1][2] - group[0][1]
    dest_starts = group[0][3] + 1
    dest_length = group[-1][4] - group[0][3]
    return DifferGroupHeader(source_starts, source_length, dest_starts, dest_length)


def unified_diff(source_lines: List[str], dest_lines: List[str], n=3) -> Iterator[Union[DifferLine, DifferGroupHeader]]:
    diffs = difflib.SequenceMatcher(None, source_lines, dest_lines)
    for group in diffs.get_grouped_opcodes(n=n):
        yield get_diff_group_header(group)
        # print(group)
        for marker, i0, i1, j0, j1 in group:
            line_iterator_source = list(range(i0, i1))
            line_iterator_dest = list(range(j0, j1))

            if marker == 'equal':
                for line_src, line_dst, string in zip(line_iterator_source, line_iterator_dest, source_lines[i0:i1]):
                    yield DifferLine(line_src + 1, line_dst + 1, 'equal', string)
            if marker in {'replace', 'delete'}:
                for line_src, line_dst, string in zip(line_iterator_source, repeat(-1), source_lines[i0:i1]):
                    yield DifferLine(line_src + 1, line_dst + 1, 'delete', string)
            if marker in {'replace', 'insert'}:
                for line_src, line_dst, string in zip(repeat(-1), line_iterator_dest, dest_lines[j0:j1]):
                    yield DifferLine(line_src + 1, line_dst + 1, 'insert', string)


def format_differ_group_header(gh: DifferGroupHeader, source_length: int, dest_length: int, colored=True,
                               show_line_no=True):
    if show_line_no:
        margin = ' ' * (int_str_length(source_length) + int_str_length(dest_length) + 3)
    else:
        margin = ''
    if colored:
        return f'\n{margin}\033[93m{gh}\033[0m'
    else:
        return f'\n{margin}{gh}'


def format_differ_line(d: DifferLine, source_length: int, dest_length: int, colored=True, show_line_no=True):
    source_line_no_str = int_right_align(d.source_line_no, int_str_length(source_length)) \
        if d.source_line_no else ' ' * int_str_length(source_length)
    dest_line_no_str = int_right_align(d.dest_line_no, int_str_length(dest_length)) \
        if d.dest_line_no else ' ' * int_str_length(dest_length)
    marker = marker_abbr[d.marker]
    color_code_starts = marker_color_code[d.marker] if colored else ''
    color_code_ends = '\033[0m' if colored else ''

    if show_line_no:
        return f'{color_code_starts} {source_line_no_str} {dest_line_no_str} {marker}{d.string}{color_code_ends}'
    else:
        return f'{color_code_starts}{marker}{d.string}{color_code_ends}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fromfile', type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument('tofile', type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument('-c', '--color', dest='colored', action='store_true', help='색상으로 표시할 지 여부')
    parser.add_argument('-n', '--numlines', dest='n', type=int, default=3, help='컨텍스트 줄 수')
    parser.add_argument('-l', '--lineno', dest='show_line_no', action='store_true', help='줄 수를 표시할지 여부')
    args = parser.parse_args()

    source_text = args.fromfile.read().splitlines()
    dest_text = args.tofile.read().splitlines()
    lines_source = len(source_text)
    lines_dest = len(dest_text)

    for item in unified_diff(source_text, dest_text, n=args.n):
        if isinstance(item, DifferGroupHeader):
            print(format_differ_group_header(item, lines_source, lines_dest, show_line_no=args.show_line_no,
                                             colored=args.colored))
        else:
            print(format_differ_line(item, lines_source, lines_dest, show_line_no=args.show_line_no,
                                     colored=args.colored))
