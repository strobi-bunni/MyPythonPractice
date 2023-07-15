#!/usr/bin/env python
"""
Regular expression for ISO 8601 datetime format.

NOTE: This regex is not strict. For example, a datetime with month is greater than 12 passes this regex.
"""

import re
from itertools import product

# minimalist form (no useful groups, for checking-only)
regex_iso8601_datetime_minimalist = re.compile(
    r"^\d{4}(?:(-?)\d{2}\1\d{2}|(-?)W\d{2}\2[1-7]|-?\d{3})"
    r"T\d{2}(?:(:?)\d{2}(?:\3\d{2}(?:\.\d{1,6})?)?)?(?:Z|[+\-\u2212]\d{2}(?::?\d{2}(?::?\d{2})?)?)?$"
)

# expanded(verbose) form (for parsing)
regex_iso8601_datetime = re.compile(r"""^
(?P<date>         (?# ISO 8601 date format)
    (?P<year>\d{4})
    (?:
        (?P<ymd_hyphen>-?)          (?# yyyy-mm-dd or yyyymmdd format)
        (?P<month>\d{2})
        (?P=ymd_hyphen)
        (?P<day>\d{2})
        |
        (?P<ywd_hyphen>-?)          (?# yyyy-Www-d for yyyyWwwd format)
        W
        (?P<week>\d{2})
        (?P=ywd_hyphen)
        (?P<weekday>[1-7])
        |
        -?                          (?# yyyy-ddd or yyyyddd format)
        (?P<ordinalday>\d{3})
    )
)
T
(?P<time>         (?# ISO 8601 time format: hh[:mm[:ss[.ffffff]]] or hh[mm[ss[.ffffff]]])
    (?P<hour>\d{2})
    (?:
        (?P<hms_colon>:?)
        (?P<minute>\d{2})
        (?:
            (?P=hms_colon)
            (?P<second>\d{2})
            (?:
                \.
                (?P<microsecond>\d{1,6})
            )?
        )?
    )?
)
(?P<tzinfo>       (?# ISO 8601 timezone info: Z or +-hh[[:]mm])
    Z
    |
    (?P<tzsign>[+\-\u2212])
    (?P<tzhour>\d{2})
    (?:
        :?
        (?P<tzminute>\d{2})
        (?:
            :?
            (?P<tzsecond>\d{2})
        )?
    )?
)?
$""", re.X)

# test cases
test_cases_date = ['2020-01-02', '20200102', '2020-W01-2', '2020W012', '2020123', '2020-123']
test_cases_time = ['12:34:56', '123456', '12:34:56.123456', '123456.123456']
test_cases_tzinfo = ['', 'Z', '+12:34', '+1234', '+12', '+123456']
for (test_case_date, test_case_time, test_case_tzinfo) in product(test_cases_date, test_cases_time, test_cases_tzinfo):
    test_case = f'{test_case_date}T{test_case_time}{test_case_tzinfo}'
    if matches := regex_iso8601_datetime.match(test_case):
        print(f'{test_case}: date={matches["date"]}, time={matches["time"]}, tzinfo={matches["tzinfo"]}')
    else:
        print(f'{test_case}: not matched')
