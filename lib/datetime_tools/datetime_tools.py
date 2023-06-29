import datetime
from typing import Literal

UNIX_TIME_EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)

T_Timespec = Literal["microseconds", "milliseconds", "seconds", "minutes", "hours", "days"]


def truncate_datetime(dt: datetime.datetime, timespec: T_Timespec = "seconds") -> datetime.datetime:
    """시각 dt를 대상 timespec 정밀도까지 표현하며, 그보다 작은 단위는 0으로 나타낸다.

    Parameters
    ----------
    dt : datetime.datetime
        datetime 객체
    timespec : {'microseconds', 'milliseconds', 'seconds', 'minutes', 'hours', 'days'}
        시각 정밀도. 기본값은 'seconds'이다.

    Returns
    -------
    truncated_dt : datetime.datetime
        잘라낸 시각
    """
    if timespec == "microseconds":
        return dt
    elif timespec == "milliseconds":
        return dt.replace(microsecond=dt.microsecond // 1000 * 1000)
    elif timespec == "seconds":
        return dt.replace(microsecond=0)
    elif timespec == "minutes":
        return dt.replace(second=0, microsecond=0)
    elif timespec == "hours":
        return dt.replace(minute=0, second=0, microsecond=0)
    elif timespec == "days":
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError('Invalid timespec')
