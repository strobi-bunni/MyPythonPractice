"""
Look-and-say sequence

introduced by John Conway
if starts with 1:
1, 11, 21, 1211, 111221, 312211, ...

1 : one 1 -> 11
11 : two 1s -> 21
21 : one 2 one 1 -> 1211
1211 : one 1 one 2 two 1s -> 111221
111221 : three 1s two 2s one 1 -> 312211

see more information : https://en.wikipedia.org/wiki/Look-and-say_sequence
"""

from itertools import groupby


def lookandsay_gen(x0):
    while True:
        yield x0
        x0 = ''.join(str(len(list(j))) + i for i, j in groupby(x0))


las = lookandsay_gen('1')
print('n\tlength')
for n in range(1, 51):
    x = next(las)
    print(f'{n}\t{len(x)}')
