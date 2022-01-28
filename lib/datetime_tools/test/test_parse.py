import datetime
import unittest

from ..parse import parse_iso8601_datetime, parse_iso8601_datetimespan


class TestISO8601Parse(unittest.TestCase):
    def test_parse_datetime(self):
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04'),
                         datetime.datetime(2020, 1, 2, 3, 4))
        self.assertEqual(parse_iso8601_datetime('2020-01-02T03:04'),
                         datetime.datetime(2020, 1, 2, 3, 4))
        self.assertEqual(parse_iso8601_datetime('2020-01-02T03:04:05'),
                         datetime.datetime(2020, 1, 2, 3, 4, 5))
        self.assertEqual(parse_iso8601_datetime('2020-01-02T03:04:44.123'),
                         datetime.datetime(2020, 1, 2, 3, 4, 44, 123000))
        self.assertEqual(parse_iso8601_datetime('2020-01-02T03:04:56.789012'),
                         datetime.datetime(2020, 1, 2, 3, 4, 56, 789012))
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04:56Z'),
                         datetime.datetime(2020, 1, 2, 3, 4, 56, tzinfo=datetime.timezone.utc))
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04:56+09'),
                         datetime.datetime(2020, 1, 2, 3, 4, 56,
                                           tzinfo=datetime.timezone(datetime.timedelta(hours=9))))
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04-0930'),
                         datetime.datetime(2020, 1, 2, 3, 4,
                                           tzinfo=datetime.timezone(datetime.timedelta(hours=-9, minutes=-30))))
        self.assertEqual(parse_iso8601_datetime('2020-01-02 03:04-0930'),
                         datetime.datetime(2020, 1, 2, 3, 4,
                                           tzinfo=datetime.timezone(datetime.timedelta(hours=-9, minutes=-30))))

    def test_parse_datetimespan(self):
        self.assertEqual(parse_iso8601_datetimespan('P1Y'), datetime.timedelta(days=365))
        self.assertEqual(parse_iso8601_datetimespan('P2M'), datetime.timedelta(days=60))
        self.assertEqual(parse_iso8601_datetimespan('P34D'), datetime.timedelta(days=34))
        self.assertEqual(parse_iso8601_datetimespan('P123DT45H'), datetime.timedelta(days=123, hours=45))
        self.assertEqual(parse_iso8601_datetimespan('PT12H34M'), datetime.timedelta(hours=12, minutes=34))
        self.assertEqual(parse_iso8601_datetimespan('PT12H34M56S'),
                         datetime.timedelta(hours=12, minutes=34, seconds=56))
        self.assertEqual(parse_iso8601_datetimespan('PT12H34M56.789S'),
                         datetime.timedelta(hours=12, minutes=34, seconds=56, milliseconds=789))
        self.assertEqual(parse_iso8601_datetimespan('PT12H333.3S'),
                         datetime.timedelta(hours=12, seconds=333, milliseconds=300))
