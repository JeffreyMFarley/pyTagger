from __future__ import unicode_literals
import unittest
import pyTagger.actions.reripped as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch, Mock, MagicMock
except ImportError:
    from mock import patch, Mock, MagicMock


class TestRerippedAction(unittest.TestCase):
    def setUp(self):
        import sys
        self.snapshot = {'foo': 'bar'}
        with patch.object(sys, 'argv', ['test', '1']):
            self.options = configurationOptions('reripped')

    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_isonom_ok(self, isonom):
        isonom.process.return_value = "Success"
        with self.assertRaises(AssertionError):
            target.process(self.options)

    @patch('pyTagger.actions.reripped.isonom')
    def test_process_step1_isonom_fails(self, isonom):
        isonom.process.return_value = 'Foo'
        actual = target.process(self.options)
        self.assertEqual(actual, 'Foo')

    def test_process_step2(self):
        self.options.step = 2
        actual = target.process(self.options)
        self.assertEqual(actual, "Not Implemented")

if __name__ == '__main__':
    unittest.main()
