"""
다음 코드는 유니코드의 수학 글꼴 글자들을 출력한다.
"""
# 반각 문자
from typing import Dict, List, Tuple

halfwidth_upper = range(0x41, 0x5B)  # A-Z (U+0041 - U+005A)
halfwidth_lower = range(0x61, 0x7B)  # a-z (U+0061 - U+007A)

typefaces: Dict[str, Dict[int, int]] = {}
# 글꼴 이름과 'A'에 해당되는 문자의 시작 위치
# 유니코드 테이블에서 각각의 글꼴들은 ABC...XYZabc...xyz 순서로 되어 있다.
typeface_names_and_start_points: List[Tuple[str, int]] = [
    ('Bold', 0x1D400), ('Italic', 0x1D434), ('Bold Italic', 0x1D468), ('Script', 0x1D49C), ('Bold Script', 0x1D4D0),
    ('Fraktur', 0x1D504), ('Double Struck', 0x1D538), ('Bold Fraktur', 0x1D56C), ('Sans-Serif', 0x1D5A0),
    ('Sans-Serif Bold', 0x1D5D4), ('Sans-Serif Italic', 0x1D608), ('Sans-Serif Bold Italic', 0x1D63C),
    ('Monospace', 0x1D670)
]
for typeface_name, start_point in typeface_names_and_start_points:
    # {ord(<alphabet charcodes>): ord(<typefaced alphabet charcodes>)} mapping
    uppercase_map: Dict[int, int] = dict(zip(halfwidth_upper, range(start_point, start_point + 26)))  # uppercase
    lowercase_map: Dict[int, int] = dict(zip(halfwidth_lower, range(start_point + 26, start_point + 52)))  # lowercase
    typefaces[typeface_name] = {**uppercase_map, **lowercase_map}  # union dicts

# 예외 사항들
typefaces['Italic'].update({ord('h'): 0x210E})
typefaces['Script'].update({
    ord('B'): 0x212C, ord('E'): 0x2130, ord('F'): 0x2131, ord('H'): 0x210B, ord('I'): 0x2110, ord('L'): 0x2112,
    ord('M'): 0x2133, ord('R'): 0x211B, ord('e'): 0x212F, ord('g'): 0x210A, ord('o'): 0x2134
})
typefaces['Fraktur'].update({ord('C'): 0x212D, ord('H'): 0x210C, ord('I'): 0x2111, ord('R'): 0x211C, ord('Z'): 0x2128})
typefaces['Double Struck'].update({
    ord('C'): 0x2102, ord('H'): 0x210D, ord('N'): 0x2115, ord('P'): 0x2119, ord('Q'): 0x211A, ord('R'): 0x211D,
    ord('Z'): 0x2124
})

for typeface_name, typeface_mapping in typefaces.items():
    sample_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    print(f'{typeface_name}\n{sample_letters.translate(typeface_mapping)}\n')
