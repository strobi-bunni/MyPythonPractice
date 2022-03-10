import unittest

from lib.str_tools.str_tools import *


class TestStrTools(unittest.TestCase):
    def test_findall(self):
        self.assertEqual(list(findall('==hello python hello world hello==', 'hello')), [2, 15, 27])
        self.assertEqual(list(findall('trololololol', 'lol')), [3, 7])
        self.assertEqual(list(findall('trololololol', 'lol', overlap=True)), [3, 5, 7, 9])


if __name__ == '__main__':
    unittest.main()
