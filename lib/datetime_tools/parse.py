import datetime
import re
from typing import Literal, Optional

iso8601_datetime_regex = re.compile(
    r'^(?P<date>(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}))'  # yyyy-mm-dd
    r'[ T]'  # 날짜와 시간 구분자(원칙은 "T"이지만 간혹 " "을 쓰는 경우도 있다.
    r'(?P<time>(?P<hour>\d{2}):(?P<minute>\d{2})(?::(?P<second>\d{2})(?:\.(?P<microsecond>\d{,6}))?)?)'
    # hh:mm[:ss[.ffffff]]
    r'(?P<tzinfo>Z|(?P<tzhour>[+\-]\d{2})(?::?(?P<tzminute>\d{2}))?)?$'  # Z 혹은 ±hh[[:]mm]
)
iso8601_datetimespan_regex = re.compile(
    r'^P(?P<datespan>(?:(?P<yearspan>\d+)Y)?(?:(?P<monthspan>\d+)M)?(?:(?P<dayspan>\d+)D)?)?'
    r'(?:T(?P<timespan>(?:(?P<hourspan>\d+)H)?(?:(?P<minutespan>\d+)M)?(?:(?P<secondspan>\d+(?:\.\d{,6})?)S)?))?$'
)


def _copysign(x: int, y: int) -> int:
    """math.copysign(x, y)와 비슷하나, 이 쪽은 정수만을 받고 정수만을 반환한다.
    """
    if y >= 0:
        return abs(x)
    else:
        return -abs(x)


def parse_iso8601_datetime(s: str) -> datetime.datetime:
    """ISO 8601 형식으로 표시된 시각을 해석한다.

    ISO 8601 형식 시각 표기는 다음과 같다:

    ::

        datetime     ::= date datetime_sep time [tzinfo]
        date         ::= year "-" month "-" day
        year         ::= <4 digits>
        month        ::= <2 digits, from 01 to 12>
        day          ::= <2 digits, from 01 to 31>
        datetime_sep ::= " " | "T"
        time         ::= hour ":" minute [":" second ["." microsecond]]
        hour         ::= <2 digits, from 00 to 23>
        minute       ::= <2 digits, from 00 to 59>
        second       ::= <2 digits, from 00 to 59>
        microsecond  ::= <3 or 6 digits>
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
    if matches := iso8601_datetime_regex.match(s):
        year: int = int(matches['year'])  # 연도
        month: int = int(matches['month'])  # 월
        day: int = int(matches['day'])  # 일
        hour: int = int(matches['hour'])  # 시
        minute: int = int(matches['minute'])  # 분
        second: int = int(matches['second']) if matches['second'] else 0  # 초
        microsecond_str = matches['microsecond']
        if microsecond_str is None:
            microsecond = 0
        else:  # 마이크로초
            microsecond = int(microsecond_str + (6 - len(microsecond_str)) * '0')

        tzinfo_str = matches['tzinfo']
        if tzinfo_str is None:  # 로컬 시각
            tzinfo = None
        elif tzinfo_str == 'Z':  # Zulu Time(UTC)
            tzinfo = datetime.timezone.utc
        else:
            tzhour: int = int(matches['tzhour'])
            tzminute: int = _copysign(int(matches['tzminute']), tzhour) if matches['tzminute'] else 0
            tzinfo = datetime.timezone(datetime.timedelta(hours=tzhour, minutes=tzminute))
        return datetime.datetime(year, month, day, hour, minute, second, microsecond, tzinfo)
    else:
        raise ValueError(f'{s} is not a valid ISO8601 format')


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
        secondspan   ::= digits+ ["." <3 or 6 digits>]

    .. note::
        1년은 정확히 365일, 1달은 정확히 30일로 간주한다.

        >>> parse_iso8601_datetimespan('P1Y') == parse_iso8601_datetimespan('P365D')
        True
        >>> parse_iso8601_datetimespan('P1M') == parse_iso8601_datetimespan('P30D')
        True

    :param s:
    :return:
    """
    if matches := iso8601_datetimespan_regex.match(s):
        year = int(matches['yearspan']) if matches['yearspan'] else 0
        month = int(matches['monthspan']) if matches['monthspan'] else 0
        day = int(matches['dayspan']) if matches['dayspan'] else 0
        hour = int(matches['hourspan']) if matches['hourspan'] else 0
        minute = int(matches['minutespan']) if matches['minutespan'] else 0
        second_str = matches['secondspan']
        if second_str:
            second_part, _, microsecond_part = second_str.partition('.')
            second = int(second_part)
            microsecond = int(microsecond_part + (6 - len(microsecond_part)) * '0')
        else:
            second = 0
            microsecond = 0
        return datetime.timedelta(days=year * 365 + month * 30 + day, hours=hour, minutes=minute,
                                  seconds=second, microseconds=microsecond)
    else:
        raise ValueError(f'{s} is not a valid ISO8601 format')


def timedelta_isoformat(td: datetime.timedelta,
                        timespec: Optional[Literal['seconds', 'milliseconds', 'microseconds']] = None,
                        upper_timespec: Optional[Literal['seconds', 'minutes', 'hours', 'days']] = None,
                        suppress_leading_zeros=True,
                        suppress_trailing_zeros=True,
                        suppress_interleaving_zeros=True) -> str:
    """현재 timedelta를 ISO 8601 형식으로 바꾼다.
    
    :param td: timedelta 객체
    :param timespec: 시간의 최소 단위, 만약 None이면 자동으로 알맞은 최소 단위를 찾는다. 
    :param upper_timespec: 시간의 최대 단위, 만약 None이면 자동으로 알맞는 최대 단위를 찾는다.
    :param suppress_leading_zeros: 선행 0 단위를 생략할지 여부
    :param suppress_trailing_zeros: 후행 0 단위를 생략할지 여부
    :param suppress_interleaving_zeros: 중간 0 단위를 생략할지 여부
    :return:
    """
    # TODO: 이 함수를 구현할 것
    # days, hours, minutes, seconds, milliseconds, microseconds
    label = ['days', 'hours', 'minutes', 'seconds', 'milliseconds', 'microseconds']
    timedelta_parts = [td.days, td.seconds // 3600, td.seconds % 3600 // 60, td.seconds % 60,
                       td.microseconds // 1000, td.microseconds % 1000]

    # 잘라내기
    if upper_timespec == 'days':
        upper_index = 0
    elif upper_timespec == 'hours':
        timedelta_parts[1] += timedelta_parts[0] * 24
        upper_index = 1
    elif upper_timespec == 'minutes':
        timedelta_parts[2] += timedelta_parts[1] * 60
        timedelta_parts[2] += timedelta_parts[0] * 1440
        upper_index = 2
    elif upper_timespec == 'seconds':
        timedelta_parts[3] += timedelta_parts[2] * 60
        timedelta_parts[3] += timedelta_parts[1] * 3600
        timedelta_parts[3] += timedelta_parts[0] * 86400
        upper_index = 3
    else:
        upper_index = 0 if timedelta_parts[0] != 0 \
            else 1 if timedelta_parts[0] == 0 and timedelta_parts[1] != 0 \
            else 2 if timedelta_parts[1] == 0 and timedelta_parts[1] == 0 and timedelta_parts[2] != 0 \
            else 3

    if timespec == 'microseconds':
        lower_index = 6
    elif timespec == 'milliseconds':
        lower_index = 5
    elif timespec == 'seconds':
        lower_index = 4
    else:
        lower_index = 6 if timedelta_parts[5] != 0 \
            else 5 if timedelta_parts[5] == 0 and timedelta_parts[4] != 0 \
            else 4

    label = label[upper_index:lower_index]
    timespec = timespec[upper_index:lower_index]
    # TODO: suppress_~~~를 구현할 것
