"""
Reimplementing and extending ``strftime`` function (like GNU coreutils' date(1) utility)

Extended from Python's ``datetime.datetime.strftime`` method.
currently, ``'+'`` pad type are not supported.

Implementation note: ``%r`` will use Python's ``datetime.datetime.strftime('%r')`` first,
however if this is not implemented(for example, using the older C library), ``'%I:%M:%S %p'`` will be used as fallback.
"""

import re
from datetime import datetime
from typing import Literal

# re_token = re.compile(r'%([\-_0+^#]?)([1-9][0-9]*)?([%aAbBcCdDeFgGHIjklmMnNpPqrRsStTuUVwWxXyYZ]|:{0,3}z)')
re_token = re.compile(r"%([\-_0])?([1-9][0-9]*)?([%aAbBcCdDefFgGhHIjklmMnNpPqrRsStTuUVwWxXyYZ]|:{0,3}z)")


def parse_timezone(dt: datetime, tzspec=Literal["z", ":z", "::z", ":::z", "Z"]):
    if dt.tzinfo is None:
        return ""
    tz_offset = dt.tzinfo.utcoffset(datetime.now())
    tz_offset_abs = abs(tz_offset.seconds)
    tz_offset_sign = "+" if tz_offset.seconds >= 0 else "-"
    match tzspec:
        case "Z":
            return dt.strftime("%Z")
        case "z":
            return f"{tz_offset_sign}{tz_offset_abs // 3600:02d}{(tz_offset_abs % 3600) // 60:02d}"
        case ":z":
            return f"{tz_offset_sign}{tz_offset_abs // 3600:02d}:{(tz_offset_abs % 3600) // 60:02d}"
        case "::z":
            return (
                f"{tz_offset_sign}"
                f"{tz_offset_abs // 3600:02d}:{(tz_offset_abs % 3600) // 60:02d}:{tz_offset_abs % 60:02d}"
            )
        case ":::z":
            if tz_offset_abs % 3600 == 0:
                return f"{tz_offset_sign}{tz_offset_abs // 3600:02d}"
            elif tz_offset_abs % 60 == 0:
                return f"{tz_offset_sign}{tz_offset_abs // 3600:02d}:{(tz_offset_abs % 3600) // 60:02d}"
            else:
                return (
                    f"{tz_offset_sign}"
                    f"{tz_offset_abs // 3600:02d}:{(tz_offset_abs % 3600) // 60:02d}:{tz_offset_abs % 60:02d}"
                )


def strftime(dt: datetime, fmt: str) -> str:
    year = dt.year  # %Y
    month = dt.month  # %m

    iso_calendar_year, iso_calendar_week, iso_calendar_weekday = dt.isocalendar()  # %G, %V, %u
    day = dt.day  # %d

    hour = dt.hour  # %H
    minute = dt.minute  # %M
    second = dt.second  # %S
    timestamp = int(dt.timestamp())  # %s
    microseconds = dt.microsecond  # %f (for compatibility with Python)
    nanoseconds = microseconds * 1000  # %N (for compatibility with GNU coreutils' date(1))

    def replace(m: re.Match) -> str:
        pad: Literal["", ">", "0"] = ""
        width: int = 0
        value: str | int = ""
        match m[3]:
            case "%":
                pad, width, value = ">", 1, "%"
            case "t":
                pad, width, value = ">", 1, "\t"
            case "n":
                pad, width, value = ">", 1, "\n"

            case "Y":
                pad, width, value = "0", 4, year
            case "C":
                pad, width, value = "0", 2, year // 100
            case "y":
                pad, width, value = "0", 2, year % 100

            case "q":
                pad, width, value = "0", 1, (month - 1) // 3 + 1
            case "m":
                pad, width, value = "0", 2, month

            case "d":
                pad, width, value = "0", 2, day
            case "e":
                pad, width, value = ">", 2, day
            case "j":
                pad, width, value = "0", 3, int(dt.strftime("%j"))

            case "H":
                pad, width, value = "0", 2, hour
            case "I":
                pad, width, value = "0", 2, (hour % 12 if hour % 12 != 0 else 12)
            case "k":
                pad, width, value = ">", 2, hour
            case "l":
                pad, width, value = ">", 2, (hour % 12 if hour % 12 != 0 else 12)

            case "M":
                pad, width, value = "0", 2, minute
            case "S":
                pad, width, value = "0", 2, second
            case "s":
                pad, width, value = "0", 1, timestamp
            case "f":
                pad, width, value = "0", 6, microseconds
            case "N":
                pad, width, value = "0", 9, nanoseconds
            case "Z" | "z" | ":z" | "::z" | ":::z" as tzspec:
                pad, width, value = "", 0, parse_timezone(dt, tzspec)

            case "G":
                pad, width, value = "0", 4, iso_calendar_year
            case "g":
                pad, width, value = "0", 2, iso_calendar_year % 100
            case "V":
                pad, width, value = "0", 2, iso_calendar_week
            case "u":
                pad, width, value = "0", 1, iso_calendar_weekday

            # some predefined patterns
            case "a" | "A" | "b" | "B" | "c" | "p" | "x" | "X" as predefined_pattern:
                pad, width, value = ">", 1, dt.strftime("%" + predefined_pattern)
            case "U" | "W" as predefined_pattern:
                pad, width, value = "0", 2, int(dt.strftime("%" + predefined_pattern))
            case "w" as predefined_pattern:
                pad, width, value = "0", 1, int(dt.strftime("%" + predefined_pattern))
            case "P":
                pad, width, value = ">", 1, dt.strftime("%p").lower()
            case "h":
                pad, width, value = ">", 1, dt.strftime("%b")
            case "D":
                pad, width, value = ">", 1, dt.strftime("%m/%d/%y")
            case "R":
                pad, width, value = ">", 1, dt.strftime("%H:%M")
            case "F":
                pad, width, value = ">", 1, dt.strftime("%Y-%m-%d")
            case "T":
                pad, width, value = ">", 1, dt.strftime("%H:%M:%S")
            case "r":
                try:
                    pad, width, value = ">", 1, dt.strftime("%r")
                except ValueError:
                    pad, width, value = ">", 1, dt.strftime("%I:%M:%S %p")

        if width_str := m[2]:
            width = int(width_str)

        match m[1]:
            case "-":
                pad = ""
                width = 0
            case "_":
                pad = ">"
            case "0":
                pad = "0"
        return f"{value:{pad}{width}}"

    return re.sub(re_token, replace, fmt)


if __name__ == "__main__":
    pass
