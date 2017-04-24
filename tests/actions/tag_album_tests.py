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


class TestAlbum(unittest.TestCase):
    def setUp(self):
        tracks = [
            ('foobar.mp3', {
                'album': 'Foo',
                'title': 'Bar',
                'albumArtist': 'Qaz',
            }),
            ('foobaz.mp3', {
                'album': 'Foo',
                'title': 'Baz',
                'track': 9,
                'albumArtist': None
            })
        ]
        self.target = sut.Album(tracks)

    def test_assign(self):
        self.target.assign('albumArtist', 'Quux')
        self.assertEqual(self.target.tracks[0][1]['albumArtist'], 'Quux')
        self.assertEqual(self.target.tracks[1][1]['albumArtist'], 'Quux')

    def test_assignToBlankExists(self):
        self.target.assignToBlank('albumArtist', 'Quux')
        self.assertEqual(self.target.tracks[0][1]['albumArtist'], 'Qaz')
        self.assertEqual(self.target.tracks[1][1]['albumArtist'], 'Quux')

    def test_assignToBlankMissing(self):
        self.target.assignToBlank('totalDisc', 2)
        self.assertEqual(self.target.tracks[0][1]['totalDisc'], 2)
        self.assertEqual(self.target.tracks[1][1]['totalDisc'], 2)

    def test_assignTotalTrack(self):
        self.target.assignTotalTrack()
        self.assertEqual(self.target.tracks[0][1]['totalTrack'], 9)
        self.assertEqual(self.target.tracks[1][1]['totalTrack'], 9)

    def test_findVariations(self):
        self.target.findVariations()
        self.assertEqual(len(self.target.variations['album']), 1)
        self.assertIn('Foo', self.target.variations['album'])
        self.assertEqual(len(self.target.variations['title']), 0)
        self.assertEqual(len(self.target.variations['track']), 0)
        self.assertEqual(len(self.target.variations['albumArtist']), 2)
        self.assertIn('Qaz', self.target.variations['albumArtist'])
        self.assertIn('', self.target.variations['albumArtist'])

    def test_name(self):
        self.target.variations['album'].add('FOOOOOO')
        actual = self.target.name
        self.assertEqual(actual, 'FOOOOOO')
        self.assertEqual(len(self.target.variations['album']), 1)

    def test_nameEmpty(self):
        actual = self.target.name
        self.assertEqual(actual, u'Unknown')

    def test_nameAndDisc_noDisc(self):
        self.target.variations['album'].add('FOOOOOO')
        actual = self.target.nameAndDisc
        self.assertEqual(actual, 'FOOOOOO ****')

    def test_nameAndDisc_1Disc(self):
        self.target.variations['album'].add('FOOOOOO')
        self.target.variations['disc'].add(8)
        actual = self.target.nameAndDisc
        self.assertEqual(actual, 'FOOOOOO **8**')

    def test_nameAndDisc_2Disc(self):
        self.target.variations['album'].add('FOOOOOO')
        self.target.variations['disc'].add('')
        self.target.variations['disc'].add(8)
        actual = self.target.nameAndDisc
        self.assertEqual(actual, 'FOOOOOO ****')


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
    unittest.main()
