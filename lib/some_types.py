from abc import abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class Comparable(Protocol[T_co]):
    """비교를 위한 제너릭 클래스

    DEPRECATED: 제대로 작동하지 않고 사용하는 데가 없음
    """

    @abstractmethod
    def __lt__(self, other: "Comparable[T_co]") -> bool:
        pass
