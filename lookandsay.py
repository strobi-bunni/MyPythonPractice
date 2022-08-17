r"""
Look-and-say sequence

John Conway가 제안한 수열으로, 숫자를 읽은 말을 그대로 다음 수로 하는 수열이다. 다음과 같이 정의된다.

- 1에서부터 시작한다.
- 1은 한 개의 1이므로 "one 1"으로 읽을 수 있으며 이는 '11'으로 이어진다.
- 11은 두 개의 1이므로 "two 1s"으로 읽을 수 있으며 이는 '21'으로 이어진다.
- 21은 한 개의 2, 한 개의 1이므로 "one 2, one 1"으로 읽을 수 있으며 이는 '1211'으로 이어진다.
- 1211은 한 개의 1, 한 개의 2, 두 개의 1이므로 "one 1, one 2, two 1s"으로 읽을 수 있으며 이는 '111221'으로 이어진다.
- 111221은 세 개의 1, 두 개의 2, 한 개의 1이므로 "three 1s, two 2s, one 1"으로 읽을 수 있으며 이는 '312211'으로 이어진다.
- 이렇게 계속한다.

이런 식으로 숫자를 '연속된 숫자의 갯수'-'연속된 숫자' 식으로 읽은 말을 다음 수로 정의한다.

Look-and-say sequence는 :math:`a(1) = 1`\부터 시작해서 다음과 같이 이어진다. (OEIS: `A005150`_)

.. _`A005150`: https://oeis.org/A005150

::

    1, 11, 21, 1211, 111221, 312211, ...

see more information : https://en.wikipedia.org/wiki/Look-and-say_sequence
"""
from itertools import groupby
from typing import Iterator


def lookandsay_gen(x0: str) -> Iterator[str]:
    while True:
        yield x0
        x0 = ''.join(f'{len(list(j))}{i}' for i, j in groupby(x0))  # type: i: str; j: Iterator[str]


las = lookandsay_gen('1')
print('n\tlength')
for n in range(1, 51):
    x = next(las)
    print(f'{n}\t{len(x)}')
