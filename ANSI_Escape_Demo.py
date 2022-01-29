from textwrap import dedent

code_mapping = [
    (0, 'Reset All'), (1, 'Bold'), (2, 'Faint'), (3, 'Italic'), (4, 'Underline'), (5, 'Slow Blink'), (6, 'Rapid Blink'),
    (7, 'Invert'), (8, 'Hide'), (9, 'Crossed Out'), (21, 'Double Underline/Bold Off'), (22, 'Normal Color'),
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
