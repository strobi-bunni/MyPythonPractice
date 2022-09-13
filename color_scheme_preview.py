from typing import Tuple

print('Color Scheme Preview')
print('--------------------')


def color_code_convert(ccode: int) -> Tuple[int, int]:
    if ccode < 8:
        _fg_code = ccode + 30
        _bg_code = ccode + 40
    else:
        _fg_code = ccode + 82
        _bg_code = ccode + 92
    return _fg_code, _bg_code


print('Normal text             \x1b[7mInverted text          \x1b[0m')
for color_code, color_name in enumerate(['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
                                         'gray', 'bright red', 'bright green', 'bright yellow',
                                         'bright blue', 'bright magenta', 'bright cyan', 'bright white']):
    fg_color, bg_color = color_code_convert(color_code)
    print(f'\x1b[{fg_color}mColor \x1b[1m{color_name:<14}    '
          f'\x1b[22m\x1b[39m\x1b[{bg_color}mColor \x1b[1m{color_name:<14}   \x1b[0m')
