import datetime
import unittest

from lib.datetime_tools.datetime_tools import truncate_datetime


class TestDateTimeTools(unittest.TestCase):
    def test_truncate_datetime(self):
        test_time = datetime.datetime(2021, 2, 3, 4, 5, 6, 123456)
        self.assertEqual(truncate_datetime(test_time, "microseconds"), datetime.datetime(2021, 2, 3, 4, 5, 6, 123456))
        self.assertEqual(truncate_datetime(test_time, "milliseconds"), datetime.datetime(2021, 2, 3, 4, 5, 6, 123000))
        self.assertEqual(truncate_datetime(test_time, "seconds"), datetime.datetime(2021, 2, 3, 4, 5, 6))
        self.assertEqual(truncate_datetime(test_time, "minutes"), datetime.datetime(2021, 2, 3, 4, 5))


if __name__ == "__main__":
    unittest.main()
