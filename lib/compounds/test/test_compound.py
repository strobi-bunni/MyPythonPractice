import unittest

from lib.compounds import get_json_tree_item


class JSONLocator(unittest.TestCase):

    def test_get_item_tree(self):
        # 더 직관적으로 보이기 위해 풀어헤쳤다.
        test_dict = {
            'aaa': {
                'bbb': {
                    'ccc': 1,
                    'ddd': 0.5,
                    'eee': True,
                    'fff': False
                },
                'ggg': [
                    10,
                    20,
                    'test',
                    'hello',
                    'world'
                ]
            },
            'hhh': [
                0.1,
                0.2,
                [
                    0.3,
                    0.4,
                    0.5
                ],
                {
                    'iii': 'python'
                }
            ]
        }
        # 딕셔너리
        self.assertEqual(get_json_tree_item(test_dict),
                         {'aaa': {'bbb': {'ccc': 1, 'ddd': 0.5, 'eee': True, 'fff': False},
                                  'ggg': [10, 20, 'test', 'hello', 'world']},
                          'hhh': [0.1, 0.2, [0.3, 0.4, 0.5], {'iii': 'python'}]})
        self.assertEqual(get_json_tree_item(test_dict, 0), None)
        self.assertEqual(get_json_tree_item(test_dict, 'aaa'),
                         {'bbb': {'ccc': 1, 'ddd': 0.5, 'eee': True, 'fff': False},
                          'ggg': [10, 20, 'test', 'hello', 'world']})
        self.assertEqual(get_json_tree_item(test_dict, 'aaa', 'bbb'), {'ccc': 1, 'ddd': 0.5, 'eee': True, 'fff': False})
        self.assertEqual(get_json_tree_item(test_dict, 'aaa', 'ggg'), [10, 20, 'test', 'hello', 'world'])
        self.assertEqual(get_json_tree_item(test_dict, 'aaa', 'ggg', 2), 'test')
        self.assertEqual(get_json_tree_item(test_dict, 'aaa', 10), None)
        self.assertEqual(get_json_tree_item(test_dict, 'hhh'), [0.1, 0.2, [0.3, 0.4, 0.5], {'iii': 'python'}])
        self.assertEqual(get_json_tree_item(test_dict, 'hhh', 3), {'iii': 'python'})


if __name__ == '__main__':
    unittest.main()
