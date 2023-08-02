import inspect
import warnings
from functools import reduce, wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def identity(x: T) -> T:
    """항등 함수

    이 함수는 다른 함수의 인자로 사용할 용도로 만들어졌다.

    Parameters
    ----------
    x : Any
        아무 값

    Returns
    -------
    x : Any
        아무 값
    """
    return x


def multi_func(func: Callable[[T], T], n: int) -> Callable[[T], T]:
    r"""함수 func를 여러 번 중첩한 함수를 반환한다.

    예를 들어 ``double = lambda x: x * 2``\일 때 ``multi_func(double, 3)(2)``는
    ``double(double(double(2))) == 16``\과 같다.

    Parameters
    ----------
    func : Callable object
        중첩할 함수
    n : int
        중첩할 횟수

    Returns
    -------
    f : Callable object
        n번 중첩된 함수

    Exceptions
    ----------
    ValueError
        n < 0일 경우
    RecursionError
        재귀 한계에 도달할 경우

    Notes
    -----
    이 함수는 재귀적으로 동작한다. 따라서 ``n``\이 994를 초과할 경우 Python의 재귀 한계에 걸리게 된다.

    Examples
    --------
    >>> double = lambda x: x * 2
    >>> list((multi_func(double, i)(1)) for i in range(5))
    [1, 2, 4, 8, 16]
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return lambda x: x
    else:
        return lambda x: func(multi_func(func, n - 1)(x))


def deprecated(since=None, remove=None, instead=None):
    """함수가 Deprecated 되는 것을 알려주는 데코레이터

    Parameters
    ----------
    since
        대상 함수가 언제부터 Deprecated 되었는지
    remove
        대상 함수가 언제 제거될 것인지
    instead
        대신 사용할 함수를 알려 줌

    Examples
    --------
    다음 코드는 대상 함수가 Deprecated 되었다는 것을 알려준다.

    >>> @deprecated(since='3.4', remove='3.10', instead='built-in math.gcd')
    ... def get_gcd(a, b):
    ...     return get_gcd(b, a % b) if a % b else b
    """

    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            warning_message = (
                f"'{func.__name__}' is deprecated"
                + (f" since {since}" if since else "")
                + (f", and will be removed at {remove}" if remove else "")
                + (f". Use {instead} instead." if instead else ".")
            )
            warnings.warn(warning_message, DeprecationWarning)
            return func(*args, **kwargs)

        return decorated_func

    return decorator


def compose(*funcs: Callable[[T], T]) -> Callable[[T], T]:
    """여러 개의 함수를 하나로 합친다.

    compose(f, g, h)(x) -> f(g(h(x)))
    """
    return reduce(lambda f, g: lambda x: f(g(x)), funcs)


def is_equal(value: T) -> Callable[[T], bool]:
    """해당 값과 value가 서로 일치하는지 알려주는 함수를 반환

    Parameters
    ----------
    value : Any
        대상 값

    Returns
    -------
    func : Callable
        value와 일치하는지 여부를 알려주는 함수

    Examples
    --------
    >>> equals_to_three = is_equal(3)
    >>> equals_to_three(3)
    True
    >>> equals_to_three(10)
    False
    """
    return lambda x: x == value


def invert_bool(pred: Callable[[T], Any]) -> Callable[[T], bool]:
    """pred 함수의 실행 결과의 부울을 반대로 한 함수를 반환한다.

    Parameters
    ----------
    pred : Callable
        실행할 함수

    Returns
    -------
    inverted_pred : Callable
        부울이 반대가 된 함수

    Examples
    --------
    >>> iszero = invert_bool(int)
    >>> iszero('0')
    True
    """
    return lambda x: not pred(x)


def null_safety(argname: str, fallback_value: Any = None):
    """함수에 변수 argname의 값이 None일 경우 fallback_value를 대신 반환하게 설정하는 데코레이터

    Parameters
    ----------
    argname : str
        변수 이름
    fallback_value : Any
        argname이 None일 때 대신 반환하는 값

    Examples
    --------
    다음과 같이 적용할 수 있다.

    .. code:: python

        from typing import List, TypeVar
        T = TypeVar('T')

        @null_safety('items')
        def get_index(items: List[T], x: T) -> int:
            return items.index(x)

        print(get_index([1, 2, 3, 4], 2))   # 1
        print(get_index(None, 1))   # None

    데코레이터를 여러 개 쓸 경우 위쪽이 우선시된다.

    .. code:: python

        @null_safety('items', None)  # 이쪽이 우선순위가 높음
        @null_safety('x', -1)
        def get_index(items: List[T], x: T) -> int:
            return items.index(x)

        print(get_index([1, 2, 3, 4], 2))   # 1
        print(get_index(None, 1))   # None
        print(get_index([1, 2, 3], None))   # -1
        print(get_index(None, None))   # None

    기본값이 None인 인자에는 적용되지 않는다.

    .. code:: python

        @null_safety('items', None)  # 이쪽이 우선순위가 높음
        @null_safety('x', -1)
        @null_safety('fallback', -999)   # fallback의 기본값이 None이므로 적용 안됨
        def get_index(items: List[T], x: T, fallback=None) -> int:
            if x in items:
                return items.index(x)
            else:
                return fallback

        print(get_index([1, 2, 3, 4], 2))   # 1
        print(get_index(None, 1))   # None
        print(get_index([1, 2, 3], None))   # -1
        print(get_index([1, 2, 3], 9, None))   # None, not -999
    """

    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            signature = inspect.signature(func)
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            if bound_args.arguments[argname] is None and signature.parameters[argname].default is not None:
                return fallback_value

            return func(*args, **kwargs)

        return decorated_func

    return decorator


__all__ = ["compose", "deprecated", "identity", "invert_bool", "is_equal", "multi_func", "null_safety"]
