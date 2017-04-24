from __future__ import unicode_literals
import copy
import io
import os
import sys
import unittest
import pyTagger.actions.tag_album as sut
from pyTagger.utils import configurationOptions
from pyTagger.utils import loadJson
from tests import *

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


def loadSnapshot():
    fileName = os.path.dirname(__file__) + '/tag_album_fixture_snapshot.json'
    return loadJson(fileName)


class TestAlbumTagger(unittest.TestCase):
    def setUp(self):
        snapshot = loadSnapshot()
        self.target = sut.AlbumTagger.createFromSnapshot(snapshot)

    def test_createFromSnapshot(self):
        self.assertEqual(len(self.target.albums), 21)
        self.assertEqual(self.target.albums['now1'].status, 'pending')

    @unittest.skipUnless(sampleFilesExist, 'No results directory to use')
    def test_save(self):
        outFile = os.path.join(RESULT_DIRECTORY, 'tag_album.json')
        expected = loadSnapshot()

        self.target.save(outFile)
        actual = loadJson(outFile)
        self.assertEqual(actual, expected)


class TestTagAlbumProcess(unittest.TestCase):
    def setUp(self):
        import sys
        with patch.object(sys, 'argv', ['test']):
            self.options = configurationOptions('tag-album')

        self.target = Mock(spec=['conduct', 'save'])
        self.target.userDiscard = False

        p = patch('pyTagger.actions.tag_album.loadJson')
        self.addCleanup(p.stop)
        self.loadJson = p.start()
        self.loadJson.return_value = loadSnapshot

        p = patch('pyTagger.actions.tag_album.AlbumTagger.createFromSnapshot')
        self.addCleanup(p.stop)
        self.create = p.start()
        self.create.return_value = self.target

    def test_process_success(self):
        actual = sut.process(self.options)
        self.assertEqual(self.loadJson.call_count, 1)
        self.assertEqual(self.target.conduct.call_count, 1)
        self.assertEqual(self.target.save.call_count, 1)
        self.assertEqual(actual, 'Success')

    def test_process_discard(self):
        self.target.userDiscard = True
        actual = sut.process(self.options)
        self.assertEqual(self.loadJson.call_count, 1)
        self.assertEqual(self.target.conduct.call_count, 1)
        self.assertEqual(self.target.save.call_count, 0)
        self.assertEqual(actual, 'Not Complete')

if __name__ == '__main__':
    unittest.main(failfast=True)
