import unittest
import sys
import pyTagger.actions.rename as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestRenameAction(unittest.TestCase):
    def setUp(self):
        with patch.object(sys, 'argv', ['test', '/path/foo', '/path/bar']):
            self.options = configurationOptions('rename')

    @patch('pyTagger.actions.rename.ID3Proxy')
    @patch('pyTagger.actions.rename.renameFiles')
    def test_process_directory(self, renameFiles, id3Proxy):
        id3Proxy.return_value = 'id3Proxy'
        renameFiles.return_value = 'passed'

        actual = target.process(self.options)

        self.assertEqual(id3Proxy.call_count, 1)
        renameFiles.assert_called_once_with(
            '/path/foo', '/path/bar', 'id3Proxy'
        )
        self.assertEqual(actual, 'passed')


if __name__ == '__main__':
    unittest.main()
