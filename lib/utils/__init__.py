from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


def coalesce(*items: T, pred: Callable[[T], Any] = bool, default: Optional[T] = None) -> Optional[T]:
    """items의 값 중 처음으로 pred의 조건을 만족하는 항목을 반환한다.

    Parameters
    ----------
    items : T
        항목들
    pred : Callable, (T) -> Any
        각각의 항목들에 대해서 조건을 판별할 함수
    default : T : Optional
        조건을 만족는 항목을 찾지 못할 시 대신 반환할 값

    Returns
    -------
    first_true : T
        처음으로 True인 값. 만약 없으면 default 값을 반환한다.
    """
    for item in items:
        if pred(item):
            return item
    return default


def getattr_with_default(obj, *attrs: str, default=None):
    r"""getattr와 비슷하나 obj.attr가 없을 시 default를 반환한다.

    예를 들어 ``getattr_with_default(obj, 'attr1', 'attr2')`` 는 우선 ``obj.attr1`` 을 반환하려고 시도하며
    ``obj.attr1`` 가 없다면 ``obj.attr2`` 를 반환하려고 한다.

    Parameters
    ----------
    obj : Object
        아무 오브젝트
    attrs : str
        반환할 속성들.
    default : Any
        아무 것도 반환하지 못했을 떄 반환할 값

    Returns
    -------
    attr : Any
        해당 속성.

    Examples
    --------
    >>> add_to_collection = lambda x: getattr_with_default(x, 'add', 'append')
    >>> a = {1, 2, 3, 4}
    >>> b = [1, 2, 3, 4]
    >>> add_to_collection(a)(5)  # a.add(5)
    >>> print(a)
    {1, 2, 3, 4, 5}
    >>> add_to_collection(b)(5)  # b.add(5) fails, so tries b.append(5)
    >>> print(b)
    [1, 2, 3, 4, 5]
    """
    for attr in attrs:
        if hasattr(obj, attr):
            return getattr(obj, attr)
    return default


__all__ = ["coalesce", "getattr_with_default"]
