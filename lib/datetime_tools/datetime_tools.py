import datetime
from typing import Optional, Union

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
