from __future__ import unicode_literals
import copy
import io
import os
import sys
import unittest
import pyTagger.actions.tag_album as sut
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

    @patch('pyTagger.actions.tag_album.askMultipleChoice')
    def test_proceed_yes(self, ask):
        self.target._triage = Mock()
        ask.return_value = 'Y'
        actual = self.target.proceed()
        self.assertEqual(self.target._triage.call_count, 1)
        self.assertTrue(actual)

    @patch('pyTagger.actions.tag_album.askMultipleChoice')
    def test_proceed_no(self, ask):
        self.target._triage = Mock()
        ask.return_value = 'N'
        actual = self.target.proceed()
        self.assertEqual(self.target._triage.call_count, 1)
        self.assertFalse(actual)

    def test_conduct(self):
        self.target.applyAutoFix = Mock(return_value=True)
        self.target.askManualFix = Mock(return_value=True)
        self.target._reportStatus = Mock()

        actual = self.target.conduct()
        self.assertEqual(self.target.applyAutoFix.call_count, 1)
        self.assertEqual(self.target.askManualFix.call_count, 1)
        self.assertEqual(self.target._reportStatus.call_count, 1)
        self.assertEqual(actual, True)

if __name__ == '__main__':
    unittest.main(failfast=True)