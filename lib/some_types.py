from abc import abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

T_co = TypeVar('T_co', covariant=True)


@runtime_checkable
class Comparable(Protocol[T_co]):
    @abstractmethod
    def __lt__(self, other: 'Comparable[T_co]') -> bool:
        pass
