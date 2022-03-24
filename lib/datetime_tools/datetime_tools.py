import datetime
from typing import Literal, Optional, Union

UTC = datetime.timezone(datetime.timedelta(hours=0), name="UTC")
UNIX_TIME_EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=UTC)


def _convert_to_local_time(t: datetime.datetime) -> datetime.datetime:
    """시간을 로컬 시간대로 변경"""
    return datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)


def convert_timestamp_to_datetime(ts: Union[int, float], tz: Optional[datetime.timezone] = UTC) -> datetime.datetime:
    r"""타임스탬프를 ``datetime.datetime`` 객체로 변환한다.

    Parameters
    ----------
    ts : int or float
        타임스탬프, ``datetime.datetime(1970, 1, 1, 0, 0, 0, 0, UTC)``\으로부터 경과한 초
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


T_Timespec = Literal["microseconds", "milliseconds", "seconds", "minutes"]


def truncate_datetime(dt: datetime.datetime, timespec: T_Timespec = "seconds") -> datetime.datetime:
    """시각 dt를 대상 timespec 정밀도까지 표현하며, 그보다 작은 단위는 0으로 나타낸다.

    Parameters
    ----------
    dt : datetime.datetime
        datetime 객체
    timespec : {'microseconds', 'milliseconds', 'seconds', 'minutes'}
        시각 정밀도

    Returns
    -------
    truncated_dt : datetime.datetime
        잘라낸 시각
    """
    date_parts = ((_date := dt.date()).year, _date.month, _date.day)

    if timespec == "microseconds":
        return dt
    elif timespec == "milliseconds":
        return datetime.datetime(
            *date_parts, dt.hour, dt.minute, dt.second, dt.microsecond // 1000 * 1000, tzinfo=dt.tzinfo
        )
    elif timespec == "seconds":
        return datetime.datetime(*date_parts, dt.hour, dt.minute, dt.second, tzinfo=dt.tzinfo)
    else:
        return datetime.datetime(*date_parts, dt.hour, dt.minute, tzinfo=dt.tzinfo)
