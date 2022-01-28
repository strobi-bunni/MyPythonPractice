from datetime import datetime
from typing import Literal

from .parse import parse_iso8601_datetime, parse_iso8601_datetimespan, timedelta_isoformat

T_Timespec = Literal['microseconds', 'milliseconds', 'seconds', 'minutes']


def truncate_datetime(dt: datetime, timespec: T_Timespec = 'seconds') -> datetime:
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

    if timespec == 'microseconds':
        return dt
    elif timespec == 'milliseconds':
        return datetime(*date_parts, dt.hour, dt.minute, dt.second, dt.microsecond // 1000 * 1000, tzinfo=dt.tzinfo)
    elif timespec == 'seconds':
        return datetime(*date_parts, dt.hour, dt.minute, dt.second, tzinfo=dt.tzinfo)
    else:
        return datetime(*date_parts, dt.hour, dt.minute, tzinfo=dt.tzinfo)


__all__ = ['parse_iso8601_datetime', 'parse_iso8601_datetimespan', 'timedelta_isoformat', 'truncate_datetime']
