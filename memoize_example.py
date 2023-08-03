#!/usr/bin/env python
"""
이 스크립트는 메모이제이션의 예제이다.

메모이제이션(Memoization)은 동적 계획법의 한 방법으로 이미 계산된 값을 메모리에 저장해서 나중에 사용하는 기법이다.
이를 사용하면 메모리를 좀 더 사용하는 대신 계산 속도를 높일 수 있다.
"""
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class Memoize(Callable):
    def __init__(self, func: Callable[..., T]):
        """순수 함수에 메모이제이션을 구현하는 래퍼 클래스

        ``@Memoize`` 와 같이 데코레이터 형태로 쓸 수 있다.

        Parameter
        ---------
        func
            적용할 함수
        """

        self.func = func
        self._stored = {}
        self.__doc__ = func.__doc__

    def __call__(self, *args) -> T:
        if args in self._stored:
            return self._stored[args]
        else:
            returns = self.func(*args)
            self._stored[args] = returns
            return returns

    def __repr__(self):
        return f"Memoize({self.func.__name__})"


@Memoize
def fib(n: int) -> int:
    """피보나치 수열을 구한다."""
    if n < 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    for i in range(501):
        print(f"F({i}) = {fib(i)}")
