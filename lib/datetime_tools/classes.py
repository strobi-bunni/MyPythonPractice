from datetime import datetime, timedelta
from itertools import count
from typing import Container, Iterable, Iterator, Optional, Union

from .parse import timedelta_isoformat


class Interval(Container[datetime]):
    start_time: datetime
    end_time: datetime

    def __init__(self, t1: Union[datetime, timedelta], t2: Union[datetime, timedelta]):
        if isinstance(t1, datetime):
            self.start_time = t1
            if isinstance(t2, datetime):
                self.end_time = t2
            elif isinstance(t2, timedelta):
                self.end_time = self.start_time + t2
            else:
                raise TypeError("`t2` should be datetime.datetime or datetime.timedelta object.")

        elif isinstance(t1, timedelta):
            if isinstance(t2, datetime):
                self.end_time = t2
                self.start_time = self.end_time - t1
            else:
                raise TypeError("`t2` should be datetime.timedelta object if `t1` is datetime.datetime object.")

        else:
            raise TypeError("`t2` should be datetime.datetime or datetime.timedelta object.")

    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    def __contains__(self, item: object) -> bool:
        if isinstance(item, datetime):
            return self.start_time <= item < self.end_time
        else:
            raise TypeError("`item` should be datetime object.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.start_time!r}, {self.end_time!r})"

    def __str__(self) -> str:
        return f"{self.start_time.isoformat()}/{self.end_time.isoformat()}"


class TimeRepeat(Iterable[datetime]):
    start_time: datetime
    period: timedelta
    max_number: Optional[int]

    def __init__(self, start_time: datetime, period: timedelta, max_number: Optional[int]):
        if max_number is not None and max_number < 0:
            raise ValueError("`max_number` should be non-negative value.")

        self.start_time = start_time
        self.period = period
        self.max_number = max_number

    def __iter__(self) -> Iterator[datetime]:
        if self.max_number is None:
            return (self.start_time + self.period * i for i in count())
        else:
            return (self.start_time + self.period * i for i in range(self.max_number))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.start_time!r}, {self.period!r}, {self.max_number!r})"

    def __str__(self) -> str:
        if self.max_number is None:
            return f"R/{self.start_time.isoformat()}/{timedelta_isoformat(self.period)}"
        else:
            return f"R{self.max_number}/{self.start_time.isoformat()}/{timedelta_isoformat(self.period)}"
