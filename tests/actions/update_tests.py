import unittest
import pyTagger.actions.update as target
from pyTagger.utils import configurationOptions
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestUpdateAction(unittest.TestCase):
    def setUp(self):
        import sys
        with patch.object(sys, 'argv', ['test', 'foo.json']):
            self.options = configurationOptions('update')

    @patch('pyTagger.actions.update.loadJson')
    @patch('pyTagger.actions.update.ID3Proxy')
    @patch('pyTagger.actions.update.updateFromSnapshot')
    def test_process(self, updateFromSnapshot, id3Proxy, loadJson):
        id3Proxy.return_value = 'id3Proxy goes here'
        loadJson.return_value = 'loadJson goes here'

        actual = target.process(self.options)

        self.assertEqual(id3Proxy.call_count, 1)
        self.assertEqual(loadJson.call_count, 1)
        updateFromSnapshot.assert_called_once_with('id3Proxy goes here',
                                                   'loadJson goes here',
                                                   False)

if __name__ == '__main__':
    unittest.main()
