import datetime
import re
from typing import Dict, Literal, Optional

iso8601_date_regex = re.compile(
    r"^(?P<year>\d{4})(?:(?P<ymd_hyphen>-?)(?P<month>\d{2})(?P=ymd_hyphen)(?P<day>\d{2})|"
    r"(?P<ywd_hyphen>-?)W(?P<week>\d{2})(?P=ywd_hyphen)(?P<weekday>[1-7])|"
    r"-?(?P<ordinalday>\d{3}))$")
iso8601_time_regex = re.compile(
    r"^T?(?P<time>(?P<hour>\d{2})(?:(?P<hms_colon>:?)(?P<minute>\d{2})"
    r"(?:(?P=hms_colon)(?P<second>\d{2})(?:\.(?P<microsecond>\d+))?)?)?)"
    r"(?P<tzinfo>Z|(?P<tzsign>[+\-\u2212])(?P<tzhour>\d{2})(?::?(?P<tzminute>\d{2})(?::?(?P<tzsecond>\d{2}))?)?)?$")
iso8601_datetime_regex = re.compile(
    r"^(?P<date>(?P<year>\d{4})(?:(?P<ymd_hyphen>-?)(?P<month>\d{2})(?P=ymd_hyphen)(?P<day>\d{2})|"
    r"(?P<ywd_hyphen>-?)W(?P<week>\d{2})(?P=ywd_hyphen)(?P<weekday>[1-7])|"
    r"-?(?P<ordinalday>\d{3})))"
    r"[ T](?P<fulltime>(?P<time>(?P<hour>\d{2})(?:(?P<hms_colon>:?)(?P<minute>\d{2})"
    r"(?:(?P=hms_colon)(?P<second>\d{2})(?:\.(?P<microsecond>\d+))?)?)?)"
    r"(?P<tzinfo>Z|(?P<tzsign>[+\-\u2212])(?P<tzhour>\d{2})(?::?(?P<tzminute>\d{2})(?::?(?P<tzsecond>\d{2}))?)?)?)$")
iso8601_datetimespan_regex = re.compile(
    r"^P(?P<datespan>(?:(?P<yearspan>\d+)Y)?(?:(?P<monthspan>\d+)M)?(?:(?P<dayspan>\d+)D)?)?"
    r"(?:T(?P<timespan>(?:(?P<hourspan>\d+)H)?(?:(?P<minutespan>\d+)M)?(?:(?P<secondspan>\d+(?:\.\d+)?)S)?))?$"
)


def _copysign(x: int, y: int) -> int:
    """math.copysign(x, y)와 비슷하나, 이 쪽은 정수만을 받고 정수만을 반환한다."""
    if y >= 0:
        return abs(x)
    else:
        return -abs(x)


def parse_iso8601_date(s: str) -> datetime.date:
    """ISO 8601 형식으로 표시된 날짜를 해석한다.

    ISO 8601 형식 시각 표기는 다음과 같다:

    ::

        date         ::= year "-" month "-" day | year month day
                       | year "-W" week "-" weekday | year "W" week weekday
                       | year ["-"] ordinalday
        year         ::= <4 digits>
        month        ::= <2 digits, from 01 to 12>
        day          ::= <2 digits, from 01 to 31>
        week         ::= <2 digits, from 01 to 53>   # week 01 is the week containing Jan 4.
        weekday      ::= <1 digit, from 1 to 7>   # 1=Mon, 2=Tue, ..., 7=Sun
        ordinalday   ::= <3 digits, from 001 to 366>

    Parameters
    ----------
    s : str
        ISO 8601 형식 날짜 표기법

    Returns
    -------
    dt : datetime.datetime
        변환한 날짜

    Exceptions
    ----------
    ValueError
        s가 올바른 ISO 8601 형식 시각 표기법이 아닐 때
    """
    if matches := iso8601_date_regex.match(s):
        _year = int(matches['year'])
        if month_str := matches['month']:
            _date = datetime.date(_year, int(month_str), int(matches['day']))

        elif week_str := matches['week']:
            _date = datetime.date.fromisocalendar(_year, int(week_str), int(matches['weekday']))
        else:
            _date = datetime.date(_year, 1, 1) + datetime.timedelta(days=int(matches['ordinalday']) - 1)

        return _date
    else:
        raise ValueError(f"{s} is not a valid ISO8601 format")


def parse_iso8601_time(s: str) -> datetime.time:
    """ISO 8601 형식으로 표시된 시각을 해석한다.

    ISO 8601 형식 시각 표기는 다음과 같다:

    ::

        time         ::= hour ":" minute [":" second ["." microsecond]] | hour minute [second ["." microsecond]]
        hour         ::= <2 digits, from 00 to 23>
        minute       ::= <2 digits, from 00 to 59>
        second       ::= <2 digits, from 00 to 59>
        microsecond  ::= <digits>
        tzinfo       ::= "Z" | tzhour [[":"] tzminute]
        tzhour       ::= ("+" | "-") <2 digits>
        tzminute     ::= <2 digits, from 00 to 59>

    Parameters
    ----------
    s : str
        ISO 8601 형식 시각 표기법

    Returns
    -------
    dt : datetime.datetime
        변환한 날짜

    Exceptions
    ----------
    ValueError
        s가 올바른 ISO 8601 형식 시각 표기법이 아닐 때
    """
    if matches := iso8601_time_regex.match(s):
        _hour: int = int(matches['hour'])
        _minute: int = int(minute_str) if (minute_str := matches['minute']) else 0
        _second: int = int(second_str) if (second_str := matches['second']) else 0
        _microsecond: int = int(f'{microsecond_str:0<6}'[:6]) if (microsecond_str := matches['microsecond']) else 0

        if tzinfo_str := matches['tzinfo']:
            if tzinfo_str == 'Z':
                _tzinfo = datetime.timezone.utc
            else:
                _tzsign: int = 1 if matches['tzsign'] == '+' else -1
                _tzhour: int = int(matches['tzhour']) * _tzsign
                _tzminute: int = int(minute_str) * _tzsign if (minute_str := matches['tzminute']) else 0
                _tzsecond: int = int(second_str) * _tzsign if (second_str := matches['tzsecond']) else 0
                _tzinfo = datetime.timezone(datetime.timedelta(hours=_tzhour, minutes=_tzminute, seconds=_tzsecond))
        else:
            _tzinfo = None
        _time = datetime.time(_hour, _minute, _second, _microsecond, _tzinfo)

        return _time
    else:
        raise ValueError(f"{s} is not a valid ISO8601 format")


def parse_iso8601_datetime(s: str) -> datetime.datetime:
    """ISO 8601 형식으로 표시된 날짜 및 시각을 해석한다.

    ISO 8601 형식 날짜 및 시각 표기는 다음과 같다:

    ::

        datetime     ::= date datetime_sep time [tzinfo]
        date         ::= year "-" month "-" day | year month day
                       | year "-W" week "-" weekday | year "W" week weekday
                       | year ["-"] ordinalday
        year         ::= <4 digits>
        month        ::= <2 digits, from 01 to 12>
        day          ::= <2 digits, from 01 to 31>
        week         ::= <2 digits, from 01 to 53>   # week 01 is the week containing Jan 4.
        weekday      ::= <1 digit, from 1 to 7>   # 1=Mon, 2=Tue, ..., 7=Sun
        ordinalday   ::= <3 digits, from 001 to 366>
        datetime_sep ::= " " | "T"   # ISO 8601 standard uses 'T', but nonstandard ' ' is often used too.
        time         ::= hour ":" minute [":" second ["." microsecond]] | hour minute [second ["." microsecond]]
        hour         ::= <2 digits, from 00 to 23>
        minute       ::= <2 digits, from 00 to 59>
        second       ::= <2 digits, from 00 to 59>
        microsecond  ::= <digits>
        tzinfo       ::= "Z" | tzhour [[":"] tzminute]
        tzhour       ::= ("+" | "-") <2 digits>
        tzminute     ::= <2 digits, from 00 to 59>

    Parameters
    ----------
    s : str
        ISO 8601 형식 날짜 및 시각 표기법

    Returns
    -------
    dt : datetime.datetime
        변환한 날짜

    Exceptions
    ----------
    ValueError
        s가 올바른 ISO 8601 형식 날짜 및 시각 표기법이 아닐 때
    """
    if matches := iso8601_datetime_regex.match(s):
        _date = parse_iso8601_date(matches['date'])
        _time = parse_iso8601_time(matches['fulltime'])
        return datetime.datetime.combine(_date, _time)
    else:
        raise ValueError(f"{s} is not a valid ISO8601 format")


def parse_iso8601_datetimespan(s: str) -> datetime.timedelta:
    """ISO 8601 형식으로 표시된 시간을 표시한다.

    ISO 8601 형식 시간은 다음과 같다.

    ::

        datetimespan ::= "P" [datespan] ["T" timespan]
        datespan     ::= [yearspan "Y"] [monthspan "M"] [dayspan "D"]
        yearspan     ::= digits+
        monthspan    ::= digits+
        dayspan      ::= digits+
        timespan     ::= [hourspan "H"] [minutespan "M"] [secondspan "S"]
        hourspan     ::= digits+
        minutespan   ::= digits+
        secondspan   ::= digits+ ["." digits+]

    .. note::
        1년은 정확히 365일, 1달은 정확히 30일로 간주한다.

        >>> parse_iso8601_datetimespan('P1Y') == parse_iso8601_datetimespan('P365D')
        True
        >>> parse_iso8601_datetimespan('P1M') == parse_iso8601_datetimespan('P30D')
        True

    Parameters
    ----------
    s : str
        ISO 8601 시간 표현

    Returns
    -------
    td : datetime.timedelta
        timedelta로 변환한 값.

    Exceptions
    ----------
    ValueError
        s가 올바른 ISO 8601 시간 형식이 아닐 때
    """
    if matches := iso8601_datetimespan_regex.match(s):
        year = int(matches["yearspan"]) if matches["yearspan"] else 0
        month = int(matches["monthspan"]) if matches["monthspan"] else 0
        day = int(matches["dayspan"]) if matches["dayspan"] else 0
        hour = int(matches["hourspan"]) if matches["hourspan"] else 0
        minute = int(matches["minutespan"]) if matches["minutespan"] else 0
        second_str = matches["secondspan"]
        if second_str:
            second_part, _, microsecond_part = second_str.partition(".")
            second = int(second_part)
            microsecond = int(f'{microsecond_part:0<6}'[:6])
        else:
            second = 0
            microsecond = 0
        return datetime.timedelta(
            days=year * 365 + month * 30 + day, hours=hour, minutes=minute, seconds=second, microseconds=microsecond
        )
    else:
        raise ValueError(f"{s} is not a valid ISO8601 format")


def timedelta_isoformat(
        td: datetime.timedelta,
        timespec: Optional[Literal["seconds", "milliseconds", "microseconds"]] = None,
        upper_timespec: Optional[Literal["seconds", "minutes", "hours", "days"]] = None,
):
    """현재 timedelta를 ISO 8601 형식으로 바꾼다.

    Parameters
    ----------
    td : datetime.timedelta
        timedelta 객체
    timespec : {'seconds', 'milliseconds', 'microseconds'} : Optional
        시간의 최소 단위, 만약 None이면 자동으로 알맞은 최소 단위를 찾는다.
    upper_timespec : {'seconds', 'minutes', 'hours', 'days'} : Optional
        시간의 최대 단위, 만약 None이면 자동으로 알맞는 최대 단위를 찾는다.

    Returns
    -------
    s : str
        ISO 8601 형식으로 지정된 시간간격

    Examples
    --------
    >>> timedelta_isoformat(datetime.timedelta(seconds=1234, milliseconds=567))
    'PT20M34.567S'

    Notes
    -----
    모호성 때문에 upper_timespec 값으로 'months', 'years'는 지원하지 않는다.
    """
    # days, hours, minutes, seconds, milliseconds, microseconds
    label = ["days", "hours", "minutes", "seconds", "milliseconds", "microseconds"]
    timedelta_parts = [
        td.days,
        td.seconds // 3600,
        td.seconds % 3600 // 60,
        td.seconds % 60,
        td.microseconds // 1000,
        td.microseconds % 1000,
    ]

    # 잘라내기
    if upper_timespec == "days":
        upper_index = 0
    elif upper_timespec == "hours":
        timedelta_parts[1] += timedelta_parts[0] * 24
        upper_index = 1
    elif upper_timespec == "minutes":
        timedelta_parts[2] += timedelta_parts[1] * 60
        timedelta_parts[2] += timedelta_parts[0] * 1440
        upper_index = 2
    elif upper_timespec == "seconds":
        timedelta_parts[3] += timedelta_parts[2] * 60
        timedelta_parts[3] += timedelta_parts[1] * 3600
        timedelta_parts[3] += timedelta_parts[0] * 86400
        upper_index = 3
    else:
        upper_index = (
            0
            if timedelta_parts[0] != 0
            else 1
            if timedelta_parts[0] == 0 and timedelta_parts[1] != 0
            else 2
            if timedelta_parts[1] == 0 and timedelta_parts[1] == 0 and timedelta_parts[2] != 0
            else 3
        )

    if timespec == "microseconds":
        lower_index = 6
    elif timespec == "milliseconds":
        lower_index = 5
    elif timespec == "seconds":
        lower_index = 4
    else:
        lower_index = 6 if timedelta_parts[5] != 0 else 5 if timedelta_parts[5] == 0 and timedelta_parts[4] != 0 else 4

    label = label[upper_index:lower_index]
    timedelta_parts = timedelta_parts[upper_index:lower_index]
    timedelta_dict: Dict[str, int] = dict(zip(label, timedelta_parts))

    # 문자열로 변환
    days_part = f'{timedelta_dict["days"]}D' if "days" in timedelta_dict else ""
    hours_part = f'{timedelta_dict["hours"]}H' if "hours" in timedelta_dict else ""
    minutes_part = f'{timedelta_dict["minutes"]}M' if "minutes" in timedelta_dict else ""
    seconds_part = (
        f'{timedelta_dict["seconds"]}S'
        if lower_index == 4
        else f'{timedelta_dict["seconds"]}.{timedelta_dict["milliseconds"]:03d}S'
        if lower_index == 5
        else f'{timedelta_dict["seconds"]}.{timedelta_dict["milliseconds"]:03d}{timedelta_dict["microseconds"]:03d}S'
    )

    return f"P{days_part}T{hours_part}{minutes_part}{seconds_part}"


__all__ = ["parse_iso8601_date", "parse_iso8601_datetime", "parse_iso8601_time", "parse_iso8601_datetimespan",
           "timedelta_isoformat"]
