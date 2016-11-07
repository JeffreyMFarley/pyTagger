from __future__ import unicode_literals
import unittest
import pyTagger.actions.export as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestExportAction(unittest.TestCase):
    def setUp(self):
        import sys
        with patch.object(sys, 'argv', ['test', 'foo.json']):
            self.options = configurationOptions('to-csv')

    def test_getOutputName_fileSpecified(self):
        self.options.outfile = 'bar.txt'
        actual = target._getOutputName(self.options)
        self.assertEqual(actual, 'bar.txt')

    def test_getOutputName_csv_true(self):
        self.options.csv_format = True
        actual = target._getOutputName(self.options)
        self.assertEqual(actual, 'foo.csv')

    def test_getOutputName_csv_false(self):
        self.options.csv_format = False
        actual = target._getOutputName(self.options)
        self.assertEqual(actual, 'foo.txt')

    @patch('pyTagger.actions.export.writeCsv')
    @patch('pyTagger.actions.export.loadJson')
    def test_process(self, loadJson, writeCsv):
        actual = target.process(self.options)
        self.assertEqual(actual, "Exported to foo.txt")
        self.assertEqual(loadJson.call_count, 1)
        self.assertEqual(writeCsv.call_count, 1)

if __name__ == '__main__':
    unittest.main()
