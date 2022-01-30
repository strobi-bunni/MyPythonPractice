import unittest
from datetime import datetime, timedelta, timezone

from lib.datetime_tools.parse import parse_iso8601_datetime, parse_iso8601_datetimespan, timedelta_isoformat


class TestISO8601Parse(unittest.TestCase):
    def test_parse_datetime(self):
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04'), datetime(2020, 1, 2, 3, 4))
        self.assertEqual(parse_iso8601_datetime('2020-01-02T03:04'), datetime(2020, 1, 2, 3, 4))
        self.assertEqual(parse_iso8601_datetime('2020-01-02T03:04:05'), datetime(2020, 1, 2, 3, 4, 5))
        self.assertEqual(parse_iso8601_datetime('2020-01-02T03:04:44.123'), datetime(2020, 1, 2, 3, 4, 44, 123000))
        self.assertEqual(parse_iso8601_datetime('2020-01-02T03:04:56.789012'),
                         datetime(2020, 1, 2, 3, 4, 56, 789012))
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04:56Z'),
                         datetime(2020, 1, 2, 3, 4, 56, tzinfo=timezone.utc))
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04:56+09'),
                         datetime(2020, 1, 2, 3, 4, 56, tzinfo=timezone(timedelta(hours=9))))
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04-0930'),
                         datetime(2020, 1, 2, 3, 4, tzinfo=timezone(timedelta(hours=-9, minutes=-30))))
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04-0930'),
                         datetime(2020, 1, 2, 3, 4, tzinfo=timezone(timedelta(hours=-9, minutes=-30))))

    def test_parse_datetimespan(self):
        self.assertEqual(parse_iso8601_datetimespan('P1Y'), timedelta(days=365))
        self.assertEqual(parse_iso8601_datetimespan('P2M'), timedelta(days=60))
        self.assertEqual(parse_iso8601_datetimespan('P34D'), timedelta(days=34))
        self.assertEqual(parse_iso8601_datetimespan('P123DT45H'), timedelta(days=123, hours=45))
        self.assertEqual(parse_iso8601_datetimespan('PT12H34M'), timedelta(hours=12, minutes=34))
        self.assertEqual(parse_iso8601_datetimespan('PT12H34M56S'),
                         timedelta(hours=12, minutes=34, seconds=56))
        self.assertEqual(parse_iso8601_datetimespan('PT12H34M56.789S'),
                         timedelta(hours=12, minutes=34, seconds=56, milliseconds=789))
        self.assertEqual(parse_iso8601_datetimespan('PT12H333.3S'),
                         timedelta(hours=12, seconds=333, milliseconds=300))


class TestISO8601Convert(unittest.TestCase):
    def test_timedelta_isoformat(self):
        test_case_1 = timedelta(seconds=1234, milliseconds=12)
        self.assertEqual(timedelta_isoformat(timedelta()), 'PT0S')
        self.assertEqual(timedelta_isoformat(test_case_1), 'PT20M34.012S')
        self.assertEqual(timedelta_isoformat(test_case_1, upper_timespec='seconds'), 'PT1234.012S')
        self.assertEqual(timedelta_isoformat(test_case_1, upper_timespec='minutes'), 'PT20M34.012S')
        self.assertEqual(timedelta_isoformat(test_case_1, upper_timespec='hours'), 'PT0H20M34.012S')
        self.assertEqual(timedelta_isoformat(test_case_1, upper_timespec='days'), 'P0DT0H20M34.012S')
        self.assertEqual(timedelta_isoformat(test_case_1, timespec='microseconds'), 'PT20M34.012000S')
        self.assertEqual(timedelta_isoformat(test_case_1, timespec='milliseconds'), 'PT20M34.012S')
        self.assertEqual(timedelta_isoformat(test_case_1, timespec='seconds'), 'PT20M34S')


if __name__ == '__main__':
    unittest.main()
