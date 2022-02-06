import collections.abc
from typing import Callable, TypeVar

T = TypeVar('T')


class Memoize(collections.abc.Callable):
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
        if args in self._stored.keys():
            return self._stored[args]
        else:
            returns = self.func(*args)
            self._stored[args] = returns
            return returns

    def __repr__(self):
        return f'Memoize({self.func.__name__})'


@Memoize
def fib(n: int) -> int:
    """피보나치 수열을 구한다.
    """
    if n < 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


if __name__ == '__main__':
    for i in range(501):
        print(f'F({i}) = {fib(i)}')
