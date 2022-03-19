r"""
다음 코드는 `ANSI 이스케이프 시퀀스`_\를 사용해서 글자에 효과를 넣는 방법에 대해서 설명한다.

.. _`ANSI 이스케이프 시퀀스` : https://en.wikipedia.org/wiki/ANSI_escape_code

글자에 효과를 주기 위한 ANSI 이스케이프 시퀀스는 다음과 같다. 다음 시퀀스를 입력하면 이후에 입력되는 글자에는 효과가 적용된다.
여기서 *ESC*\는 이스케이프 문자(U+0027, \\x1f 혹은 \\033)이다.

*ESC* ``[`` *Code* ``m``

예를 들어 ``\x1f[1mhello``\를 출력하면 **hello**\가 굵은 글씨로 출력된다.

-----

*Code*\가 38 혹은 48일 경우에는 `256색`_ 혹은 24비트 색상을 지정할 수 있다.

.. _`256색` : https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit

256색:

- 글자 색 지정 : *ESC* ``[38;5;`` *ColorCode* ``;m``
- 배경 색 지정 : *ESC* ``[48;5;`` *ColorCode* ``;m``

24비트 색:

- 글자 색 지정 : *ESC* ``[38;2;`` *Red* ``;`` *Green* ``;`` *Blue* ``;m``
- 배경 색 지정 : *ESC* ``[48;2;`` *Red* ``;`` *Green* ``;`` *Blue* ``;m``
"""
from textwrap import dedent

code_mapping = [
    (0, 'Reset All'), (1, 'Bold'), (2, 'Faint'), (3, 'Italic'), (4, 'Underline'), (5, 'Slow Blink'), (6, 'Rapid Blink'),
    (7, 'Invert'), (8, 'Hide'), (9, 'Crossed Out'), (21, 'Double Underline/Bold Off'), (22, 'Bold/Faint Off'),
    (23, 'Italic Off'), (24, 'Underline Off'), (25, 'Blink Off'), (27, 'Invert Off'), (28, 'Hide Off'),
    (29, 'Crossed Out Off'), (30, 'Foreground Black'), (31, 'Foreground Red'), (32, 'Foreground Green'),
    (33, 'Foreground Yellow'), (34, 'Foreground Blue'), (35, 'Foreground Magenta'), (36, 'Foreground Cyan'),
    (37, 'Foreground White'), (38, 'Set Foreground Color'), (39, 'Reset Foreground Color'), (40, 'Background Black'),
    (41, 'Background Red'), (42, 'Background Green'), (43, 'Background Yellow'), (44, 'Background Blue'),
    (45, 'Background Magenta'), (46, 'Background Cyan'), (47, 'Background White'), (48, 'Set Background Color'),
    (49, 'Reset Background Color'), (53, 'Overline'), (55, 'Overline Off'), (90, 'Foreground Gray'),
    (91, 'Foreground Bright Red'), (92, 'Foreground Bright Green'), (93, 'Foreground Bright Yellow'),
    (94, 'Foreground Bright Blue'), (95, 'Foreground Bright Magenta'), (96, 'Foreground Bright Cyan'),
    (97, 'Foreground Bright White'), (100, 'Background Gray'), (101, 'Background Bright Red'),
    (102, 'Background Bright Green'), (103, 'Background Bright Yellow'), (104, 'Background Bright Blue'),
    (105, 'Background Bright Magenta'), (106, 'Background Bright Cyan'), (107, 'Background Bright White')
]

if __name__ == '__main__':
    print(dedent("""
          How to use ANSI escape code: print('\\033[\033[1m\033[93m<CODE>\033[0mmTEXT')
          Example: '\\033[44mHello\\033[0m\\033[93mWorld\\033[0m' -> \033[44mHello\033[0m\033[93mWorld\033[0m
           
          Code    Description                   Example
          --------------------------------------------------------------------"""))
    for i, s in code_mapping:
        print(f'{i:<8}{s:<30}\033[{i}m{s}\033[0m')
