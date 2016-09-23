import unittest
from pyTagger.operations.find_duplicates import findDuplicates
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestFindDuplicates(unittest.TestCase):
    @patch('pyTagger.operations.find_duplicates.Client', spec=True)
    def test_findDuplicates(self, client):
        client.search.return_value = {
            u"aggregations": {
                u"duplicates": {
                    u"buckets": [{
                        u"key": u"foo",
                        u"files": {
                            u"buckets": [
                                {u"key": u"bar"},
                                {u"key": u"baz"},
                            ]
                        }
                    }]
                }
            }
        }

        actual = list(findDuplicates(client))
        client.search.assert_called_once()
        self.assertEqual(actual, [
            (u'foo', u'bar'),
            (u'foo', u'baz')
        ])

if __name__ == '__main__':
    unittest.main()
