import unittest

from lib.str_tools.str_tools import *


class TestStrTools(unittest.TestCase):
    def test_findall(self):
        self.assertEqual(list(findall("==hello python hello world hello==", "hello")), [2, 15, 27])
        self.assertEqual(list(findall("trololololol", "lol")), [3, 7])
        self.assertEqual(list(findall("trololololol", "lol", overlap=True)), [3, 5, 7, 9])

    def test_convert_newline(self):
        self.assertEqual(convert_newline('abcde\rfghij\r\nklmno\npqrst', 'cr'), 'abcde\rfghij\rklmno\rpqrst')
        self.assertEqual(convert_newline('abcde\rfghij\r\nklmno\npqrst', 'lf'), 'abcde\nfghij\nklmno\npqrst')
        self.assertEqual(convert_newline('abcde\rfghij\r\nklmno\npqrst', 'crlf'), 'abcde\r\nfghij\r\nklmno\r\npqrst')
        self.assertEqual(convert_newline(b'abcde\rfghij\r\nklmno\npqrst', 'cr'), b'abcde\rfghij\rklmno\rpqrst')
        self.assertEqual(convert_newline(b'abcde\rfghij\r\nklmno\npqrst', 'lf'), b'abcde\nfghij\nklmno\npqrst')
        self.assertEqual(convert_newline(b'abcde\rfghij\r\nklmno\npqrst', 'crlf'), b'abcde\r\nfghij\r\nklmno\r\npqrst')


if __name__ == "__main__":
    unittest.main()
