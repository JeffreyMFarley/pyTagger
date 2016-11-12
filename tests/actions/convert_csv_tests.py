from __future__ import unicode_literals
import unittest
import pyTagger.actions.convert_csv as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestConverCsvAction(unittest.TestCase):
    def setUp(self):
        import sys
        with patch.object(sys, 'argv', ['test', 'foo.csv']):
            self.options = configurationOptions('convert-csv')

    def test_getOutputName_fileSpecified(self):
        self.options.outfile = 'bar.json'
        actual = target._getOutputName(self.options)
        self.assertEqual(actual, 'bar.json')

    def test_getOutputName_notSpecified(self):
        actual = target._getOutputName(self.options)
        self.assertEqual(actual, 'foo.json')

    @patch('pyTagger.actions.convert_csv.convert')
    def test_process(self, convert):
        convert.return_value = (99, 1)
        actual = target.process(self.options)
        self.assertEqual(actual, '99 rows\n1 fail(s)')
        self.assertEqual(convert.call_count, 1)

if __name__ == '__main__':
    unittest.main()
