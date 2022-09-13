"""
This script roughly shows how to parse the scanf pattern

reference: https://docs.python.org/3/library/re.html#simulating-scanf
"""

import re
from typing import List, Tuple


def scanf(pattern: str, s: str) -> Tuple[...]:
    # Split pattern string to tokens
    re_token_split = re.compile(r'(%(?:\d*c|[%deEfgiosuxX]))')
    tokens = re_token_split.split(pattern)
    inferred_types: List[type] = []

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
        # and so on...
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
