#!/usr/bin/env python
"""
This script roughly shows how to parse the scanf pattern

reference: https://docs.python.org/3/library/re.html#simulating-scanf
"""

import re
from typing import Any, Callable, List


def convert_oct_to_int(s: str) -> int:
    return int(s, base=8)


def convert_hex_to_int(s: str) -> int:
    return int(s, base=16)


def auto_convert_to_int(s: str) -> int:
    if re.match(r'[-+]?0[xX][\dA-Fa-f]+', s):
        return convert_hex_to_int(s)
    elif re.match(r'[-+]?0[0-7]*', s):
        return convert_oct_to_int(s)
    else:
        return int(s)


def scanf(pattern: str, s: str) -> tuple:
    # Split pattern string to tokens
    re_token_split = re.compile(r'(%(?:\d*c|[%deEfgiosuxX]))')
    tokens = re_token_split.split(pattern)
    inferred_types: List[Callable[[str], Any]] = []

    # Convert the tokens to regex
    constructed_regex_pattern = ''
    for token in tokens:
        # How to refactor this code block with Python3.10's match-case syntax?
        if token == '%%':  # %% -> literal "%"
            constructed_regex_pattern += '%'
        elif matches := re.match(r'^%(\d*)c$', token):  # "%[num]c" -> [num] character[s]
            if matches[1]:
                constructed_regex_pattern += f'(.{{{matches[1]}}})'
            else:
                constructed_regex_pattern += '(.)'
            inferred_types.append(str)
        elif token == '%d':  # %d -> positive, negative, or zero decimal integers
            constructed_regex_pattern += r'([-+]?\d+)'
            inferred_types.append(int)
        elif token in ['%f', '%g', '%e', '%E']:  # %e, %E, %f, %g -> float
            constructed_regex_pattern += r'([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)'
            inferred_types.append(float)
        elif token == '%s':  # %s -> non-whitespace chars
            constructed_regex_pattern += r'(\S+)'
            inferred_types.append(str)
        elif token == '%o':  # %o -> octal numbers(no leading zeros)
            constructed_regex_pattern += r'([-+]?[0-7]+)'
            inferred_types.append(convert_oct_to_int)
        elif token in ['%x', '%X']:  # %x, %X -> hexadecimal(leading 0x or 0X)
            constructed_regex_pattern += r'([-+]?(?:0[xX])?[\dA-Fa-f]+)'
            inferred_types.append(convert_hex_to_int)
        elif token == '%u':  # %u -> unsigned number
            constructed_regex_pattern += r'(\d+)'
            inferred_types.append(int)
        elif token == '%i':  # %i -> any integer types: decimal, hexadecimal or octal
            constructed_regex_pattern += r'([-+]?(?:0[xX][\dA-Fa-f]+|0[0-7]*|\d+))'
            inferred_types.append(auto_convert_to_int)
        else:  # None of these: literal string
            constructed_regex_pattern += re.escape(token)

    # Match str
    returns = []
    regex = re.compile(constructed_regex_pattern)
    if str_matches := regex.match(s):
        for group, inferred_type in zip(str_matches.groups(), inferred_types):
            returns.append(inferred_type(group))
    else:
        raise TypeError(f'{s} is not matched with form {pattern}')
    return tuple(returns)


if __name__ == '__main__':
    print(scanf('%s - %d errors, %d warnings', '/usr/sbin/sendmail - 0 errors, 4 warnings'))
