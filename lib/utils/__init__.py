import datetime
from collections.abc import Callable, Mapping
from itertools import groupby
from typing import Optional, TypeVar, Union

from .func_utils import identity

KT = TypeVar('KT')
VT = TypeVar('VT')
T = TypeVar('T')
UTC = datetime.timezone(datetime.timedelta(hours=0), name='UTC')
UNIX_TIME_EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=UTC)


def _convert_to_local_time(t: datetime.datetime) -> datetime.datetime:
    """시간을 로컬 시간대로 변경
    """
    return datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)


def convert_timestamp_to_datetime(ts: Union[int, float], tz: Optional[datetime.timezone] = UTC) -> datetime.datetime:
    """타임스탬프를 ``datetime.datetime`` 객체로 변환한다.

    Parameters
    ----------
    ts : int or float
        타임스탬프, ``datetime.datetime(1970, 1, 1, 0, 0, 0, 0, UTC)``으로부터 경과한 초
    tz : datetime.timezone : Optional
        시간대, 기본값은 UTC이다. 만약 지역 시각(즉 시간대가 없는)을 사용하려면 tz=None으로 설정한다.

    Returns
    -------
    t : datetime.datetime
        해당 유닉스 시간을 ``datetime.datetime`` 객체로 변환한 값

    Examples
    --------
    >>> convert_timestamp_to_datetime(1000000000, tz=None)
    datetime.datetime(2001, 9, 9, 1, 46, 40)
    """
    local_time = UNIX_TIME_EPOCH + datetime.timedelta(seconds=ts)
    if tz is None:
        return _convert_to_local_time(local_time)
    else:
        return local_time.astimezone(tz)


def group_dict(d: Mapping[KT, VT], key: Callable[[VT], T] = None) -> dict[T, dict[KT, VT]]:
    """딕셔너리의 값을 키를 사용해서 묶는다

    Parameters
    ----------
    d: dict
        대상 딕셔너리
    key: Callable object : optional
        딕셔너리의 값을 받을 수 있는 함수. 반드시 Hashable한 값을 반환해야 한다. 기본값은 항등함수이다.

    Returns
    -------
    grouped_dict: dict
        값이 정렬된 딕셔너리.
        ``grouped_dict`` 의 키는 ``d`` 의 값을 받아서 ``key`` 함수로 처리한 결과이다.
        ``grouped_dict`` 의 값은 ``key`` 함수의 결과값에 따라 묶인 ``d``의 항목들이 저장된 딕셔너리이다.

    Examples
    --------
    >>> d1 = {1: 'a', 2: 'b', 3: 'a', 4: 'c', 5: 'b'}
    >>> for k, v in group_dict(d1).items():
    ...     print(f'{{{k}: {v}}}')
    {'a': {1: 'a', 3: 'a'}}
    {'b': {2: 'b', 5: 'b'}}
    {'c': {4: 'c'}}
    >>> data = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake',
    ...         'horse', 'sheep', 'monkey', 'rooster', 'dog', 'pig']
    >>> d2 = dict(enumerate(data))
    >>> # 문자열의 길이대로 키를 묶는다.
    >>> for k, v in group_dict(d2, key=len).items():
    ...     print(f'{{{k}: {v}}}')
    {2: {1: 'ox'}}
    {3: {0: 'rat', 10: 'dog', 11: 'pig'}}
    {5: {2: 'tiger', 5: 'snake', 6: 'horse', 7: 'sheep'}}
    {6: {3: 'rabbit', 4: 'dragon', 8: 'monkey'}}
    {7: {9: 'rooster'}}
    """
    if key is None:
        key = identity
    items = sorted(d.items(), key=lambda x: key(x[1]))
    return {k: dict(g) for (k, g) in groupby(items, key=lambda x: key(x[1]))}


__all__ = ['convert_timestamp_to_datetime', 'group_dict']
