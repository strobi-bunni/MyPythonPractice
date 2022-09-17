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
    returns = default
    for item in items:
        if pred(item):
            returns = item
            break
    return returns


__all__ = ["coalesce"]
