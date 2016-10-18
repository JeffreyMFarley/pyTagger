import unittest
import pyTagger.actions.scan as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestScanAction(unittest.TestCase):
    def setUp(self):
        self.options = configurationOptions('scan')

    @patch('pyTagger.actions.scan.ID3Proxy')
    @patch('pyTagger.actions.scan.buildSnapshot')
    def test_process(self, buildSnapshot, id3Proxy):
        id3Proxy.return_value = 'id3Proxy goes here'
        buildSnapshot.return_value = (420, 99)

        actual = target.process(self.options)

        self.assertEqual(id3Proxy.call_count, 1)
        buildSnapshot.assert_called_once_with(self.options.path,
                                              self.options.outfile,
                                              'id3Proxy goes here',
                                              False)
        self.assertEqual(actual, 'Extracted tags from 420 files\nFailed 99')

if __name__ == '__main__':
    unittest.main()
