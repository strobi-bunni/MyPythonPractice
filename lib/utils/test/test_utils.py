import unittest

from lib.utils import coalesce


class TestUtils(unittest.TestCase):
    def test_coalesce(self):
        self.assertEqual(coalesce(), None)
        self.assertEqual(coalesce(0), None)
        self.assertEqual(coalesce(1), 1)
        self.assertEqual(coalesce(0, 1), 1)
        self.assertEqual(coalesce(1, 0), 1)
        self.assertEqual(coalesce(1, 2, 0, 3), 1)
        self.assertEqual(coalesce(0, 0, 1, 2, 3), 1)

        def is_not_null(x):
            return x is not None

        self.assertEqual(coalesce(), None)
        self.assertEqual(coalesce(None, pred=is_not_null), None)
        self.assertEqual(coalesce(0, pred=is_not_null), 0)
        self.assertEqual(coalesce(1, pred=is_not_null), 1)
        self.assertEqual(coalesce(0, 1, pred=is_not_null), 0)
        self.assertEqual(coalesce(1, None, pred=is_not_null), 1)
        self.assertEqual(coalesce(1, 2, None, 3, pred=is_not_null), 1)
        self.assertEqual(coalesce(None, 0, 1, 2, 3, pred=is_not_null), 0)
        self.assertEqual(coalesce(None, 1, 2, 3, pred=is_not_null), 1)


if __name__ == '__main__':
    unittest.main()
