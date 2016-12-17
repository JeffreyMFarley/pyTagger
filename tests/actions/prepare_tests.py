from __future__ import unicode_literals
import io
import unittest
import pyTagger.actions.prepare as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestPrepareAction(unittest.TestCase):
    def setUp(self):
        import sys
        with patch.object(sys, 'argv', ['test', '1']):
            self.options = configurationOptions('prepare')

    @patch('pyTagger.actions.prepare.writeCsv')
    @patch('pyTagger.actions.prepare.loadJson')
    @patch('pyTagger.actions.prepare.buildSnapshot')
    @patch('pyTagger.actions.prepare.prepareForLibrary')
    def test_process_step1(self, a, b, c, d):
        b.return_value = 99, 1

        actual = target.process(self.options)

        self.assertEqual(actual, "Success")
        self.assertEqual(a.call_count, 1)
        self.assertEqual(b.call_count, 1)
        self.assertEqual(c.call_count, 1)
        self.assertEqual(d.call_count, 1)

    def test_process_step2_needs_csv(self):
        self.options.step = 2
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Ready")

    @patch('pyTagger.actions.prepare.renameFiles')
    @patch('pyTagger.actions.prepare.updateFromSnapshot')
    @patch('pyTagger.actions.prepare.ID3Proxy')
    @patch('pyTagger.actions.prepare.loadJson')
    @patch('pyTagger.actions.prepare.convert')
    @patch('pyTagger.actions.prepare.os.path.exists')
    def test_process_step2(self, exists, a, b, c, d, e):
        exists.return_value = True
        a.return_value = 99, 1
        d.return_value = 99, 1

        target._step2(self.options)

        self.assertEqual(a.call_count, 1)
        self.assertEqual(b.call_count, 1)
        self.assertEqual(c.call_count, 1)
        self.assertEqual(d.call_count, 1)
        self.assertEqual(e.call_count, 1)

    def test_process_step3(self):
        self.options.step = 3
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Implemented")

if __name__ == '__main__':
    unittest.main()
