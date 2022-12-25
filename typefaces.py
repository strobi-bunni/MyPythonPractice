#!/usr/bin/env python
"""
다음 코드는 유니코드의 수학 글꼴 글자들을 출력한다.

유니코드의 수학 글꼴 글자들은 2개의 영역에 저장되어 있다.

- U+2100 - U+214F `Letterlike Symbols`_ : 자주 사용되는 수학 글꼴 글자들을 저장했다.
- U+1D400 - U+1D7FF `Mathematical Alphanumeric Symbols`_ : 모든 수학 글꼴 글자들이 저장되어 있다.

.. _`Letterlike Symbols` : https://www.unicode.org/charts/PDF/U2100.pdf
.. _`Mathematical Alphanumeric Symbols` : https://www.unicode.org/charts/PDF/U1D400.pdf
"""
# 반각 문자
from typing import Dict, List, Literal, Tuple

T_Typefaces = Literal[
    'bold', 'italic', 'bold_italic', 'script', 'bold_script', 'fraktur', 'double_struck', 'bold_fraktur', 'sans-serif',
    'sans-serif_bold', 'sans-serif_italic', 'sans-serif_bold_italic', 'monospace'
]
halfwidth_upper = range(0x41, 0x5B)  # A-Z (U+0041 - U+005A)
halfwidth_lower = range(0x61, 0x7B)  # a-z (U+0061 - U+007A)

typefaces: Dict[T_Typefaces, Dict[int, int]] = {}
# 글꼴 이름과 'A'에 해당되는 문자의 시작 위치
# 유니코드 테이블에서 각각의 글꼴들은 ABC...XYZabc...xyz 순서로 되어 있다.
typeface_names_and_start_points: List[Tuple[T_Typefaces, int]] = [
    ('bold', 0x1D400), ('italic', 0x1D434), ('bold_italic', 0x1D468), ('script', 0x1D49C), ('bold_script', 0x1D4D0),
    ('fraktur', 0x1D504), ('double_struck', 0x1D538), ('bold_fraktur', 0x1D56C), ('sans-serif', 0x1D5A0),
    ('sans-serif_bold', 0x1D5D4), ('sans-serif_italic', 0x1D608), ('sans-serif_bold_italic', 0x1D63C),
    ('monospace', 0x1D670)
]
for typeface_name, start_point in typeface_names_and_start_points:
    # {ord(<alphabet charcodes>): ord(<typefaced alphabet charcodes>)} mapping
    uppercase_map: Dict[int, int] = dict(zip(halfwidth_upper, range(start_point, start_point + 26)))  # uppercase
    lowercase_map: Dict[int, int] = dict(zip(halfwidth_lower, range(start_point + 26, start_point + 52)))  # lowercase
    typefaces[typeface_name] = {**uppercase_map, **lowercase_map}  # union dicts

# 예외 사항들
typefaces['italic'].update({ord('h'): 0x210E})
typefaces['script'].update({
    ord('B'): 0x212C, ord('E'): 0x2130, ord('F'): 0x2131, ord('H'): 0x210B, ord('I'): 0x2110, ord('L'): 0x2112,
    ord('M'): 0x2133, ord('R'): 0x211B, ord('e'): 0x212F, ord('g'): 0x210A, ord('o'): 0x2134
})
typefaces['fraktur'].update({ord('C'): 0x212D, ord('H'): 0x210C, ord('I'): 0x2111, ord('R'): 0x211C, ord('Z'): 0x2128})
typefaces['double_struck'].update({
    ord('C'): 0x2102, ord('H'): 0x210D, ord('N'): 0x2115, ord('P'): 0x2119, ord('Q'): 0x211A, ord('R'): 0x211D,
    ord('Z'): 0x2124
})


def convert_typeface(s: str, tf_name: T_Typefaces) -> str:
    return s.translate(typefaces[tf_name])


def show_demo() -> None:
    for _typeface_name, _typeface_mapping in typefaces.items():
        sample_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        print(f'{_typeface_name}\n{convert_typeface(sample_letters, _typeface_name)}\n')


show_demo()
