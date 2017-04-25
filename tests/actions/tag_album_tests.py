from __future__ import unicode_literals
import copy
import io
import logging
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
        self.target.log.setLevel(logging.NOTSET)

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

        self._triage = self.target._triage
        self.target._triage = Mock()

        self.mockAlbum = Mock(spec=sut.Album)

    # -------------------------------------------------------------------------

    @patch('pyTagger.actions.tag_album.ask')
    def test_routeAssign_toAll(self, ask):
        ask.askMultipleChoice.return_value = 'A'
        self.mockAlbum.variations = {'foo': ['bar', 'baz']}
        self.target._routeAssign(self.mockAlbum, 'foo', 'qaz')
        self.mockAlbum.assign.assert_called_once_with('foo', 'qaz')
        self.assertEqual(self.mockAlbum.assignToBlank.call_count, 0)

    @patch('pyTagger.actions.tag_album.ask')
    def test_routeAssign_toBlank(self, ask):
        ask.askMultipleChoice.return_value = 'B'
        self.mockAlbum.variations = {'foo': ['bar', 'baz']}
        self.target._routeAssign(self.mockAlbum, 'foo', 'qaz')
        self.mockAlbum.assignToBlank.assert_called_once_with('foo', 'qaz')
        self.assertEqual(self.mockAlbum.assign.call_count, 0)

    @patch('pyTagger.actions.tag_album.ask')
    def test_routeAssign_direct(self, ask):
        self.mockAlbum.variations = {'foo': ['bar']}
        self.target._routeAssign(self.mockAlbum, 'foo', 'baz')
        self.mockAlbum.assign.assert_called_once_with('foo', 'baz')
        self.assertEqual(self.mockAlbum.assignToBlank.call_count, 0)
        self.assertEqual(ask.askMultipleChoice.call_count, 0)

    def test_triage(self):
        self.target._triageOne = Mock()
        self.target._triage = self._triage
        self.target._triage()
        self.assertEqual(self.target._triageOne.call_count, 21)

    def test_triageOne(self):
        album = self.target.albums['go1']
        album.findVariations()
        self.mockAlbum.variations = album.variations
        self.target._triageOne(self.mockAlbum)

        af = self.target.autoFixes
        self.assertEqual(af[0][0], self.mockAlbum.assign)
        self.assertEqual(af[0][1], (u'compilation', u'1'))
        self.assertEqual(af[1][0], self.mockAlbum.assign)
        self.assertEqual(af[1][1], (u'media', u'CD'))
        self.assertEqual(af[2][0], self.mockAlbum.assign)
        self.assertEqual(af[2][1], (u'publisher', u'Sony'))
        self.assertEqual(af[3][0], self.mockAlbum.assign)
        self.assertEqual(af[3][1], (u'subtitle', u'1999-08-12'))
        self.assertEqual(af[4][0], self.mockAlbum.assignTotalTrack)
        self.assertEqual(af[4][1], ())

        mf = self.target.manualFixes
        self.assertEqual(mf[0][1], u'albumArtist')
        self.assertEqual(mf[1][1], u'barcode')
        self.assertEqual(mf[2][1], u'genre')
        self.assertEqual(mf[3][1], u'year')

    # -------------------------------------------------------------------------

    def test_createFromSnapshot(self):
        self.assertEqual(len(self.target.albums), 21)

    @patch('pyTagger.actions.tag_album._buildAlbums')
    def test_rebuild(self, _buildAlbums):
        snapshot = loadSnapshot()
        self.target.rebuild()
        _, args, _ = _buildAlbums.mock_calls[0]
        self.assertEqual(snapshot, args[0])

    @unittest.skipUnless(sampleFilesExist, 'No results directory to use')
    def test_save(self):
        outFile = os.path.join(RESULT_DIRECTORY, 'tag_album.json')
        expected = loadSnapshot()

        self.target.save(outFile)
        actual = loadJson(outFile)
        self.assertEqual(actual, expected)

    # -------------------------------------------------------------------------

    def test_applyAutoFix_empty(self):
        actual = self.target.applyAutoFix()
        self.assertEqual(actual, True)

    def test_applyAutoFix_many(self):
        self.target._addToAuto(self.assertEqual, 99, 99)
        actual = self.target.applyAutoFix()
        self.assertEqual(actual, True)

    def test_askAlbumNames(self):
        pass

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_empty(self, ask):
        actual = self.target.askManualFix()
        self.assertEqual(actual, True)
        self.assertEqual(ask.askOrEnterMultipleChoice.call_count, 0)

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_option1(self, ask):
        self.target._addToAsk(self.mockAlbum, 'foo', [u'alpha', u'beta'])
        ask.askOrEnterMultipleChoice.return_value = '1'
        ra = Mock()
        self.target._routeAssign = ra

        actual = self.target.askManualFix()

        self.assertEqual(actual, True)
        _, args, _ = ask.askOrEnterMultipleChoice.mock_calls[0]
        self.assertIn('foo', args[1])
        self.assertEqual(args[2]['1'], u'alpha')
        self.assertEqual(args[2]['2'], u'beta')
        ra.assert_called_once_with(self.mockAlbum, 'foo', u'alpha')

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_optionI(self, ask):
        self.target._addToAsk(self.mockAlbum, 'foo', [])
        ask.askOrEnterMultipleChoice.return_value = 'I'
        self.target._routeAssign = Mock()

        actual = self.target.askManualFix()

        self.assertEqual(actual, True)
        self.assertEqual(self.target._routeAssign.call_count, 0)
        self.assertEqual(self.target.userQuit, False)
        self.assertEqual(self.target.userDiscard, False)

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_optionX(self, ask):
        self.target._addToAsk(self.mockAlbum, 'foo', [])
        ask.askOrEnterMultipleChoice.return_value = 'X'
        self.target._routeAssign = Mock()

        actual = self.target.askManualFix()

        self.assertEqual(actual, True)
        self.assertEqual(self.target._routeAssign.call_count, 0)
        self.assertEqual(self.target.userQuit, True)
        self.assertEqual(self.target.userDiscard, False)

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_optionZ(self, ask):
        self.target._addToAsk(self.mockAlbum, 'foo', [])
        ask.askOrEnterMultipleChoice.return_value = 'Z'
        self.target._routeAssign = Mock()

        actual = self.target.askManualFix()

        self.assertEqual(actual, True)
        self.assertEqual(self.target._routeAssign.call_count, 0)
        self.assertEqual(self.target.userQuit, False)
        self.assertEqual(self.target.userDiscard, True)

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_enter_compliation_1(self, ask):
        self.target._addToAsk(self.mockAlbum, 'compilation', [])
        ask.askOrEnterMultipleChoice.return_value = '1'
        ra = Mock()
        self.target._routeAssign = ra

        actual = self.target.askManualFix()

        self.assertEqual(actual, True)
        ra.assert_called_once_with(self.mockAlbum, 'compilation', 1)

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_enter_compilation_y(self, ask):
        self.target._addToAsk(self.mockAlbum, 'compilation', [])
        ask.askOrEnterMultipleChoice.return_value = 'y'
        self.target._routeAssign = Mock()
        a2a = Mock()
        self.target._addToAsk = a2a

        actual = self.target.askManualFix()

        self.assertEqual(actual, True)
        self.assertEqual(self.target._routeAssign.call_count, 0)
        a2a.assert_called_once_with(self.mockAlbum, 'compilation', [])

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_enter_value(self, ask):
        self.target._addToAsk(self.mockAlbum, 'foo', [u'alpha', u'beta'])
        ask.askOrEnterMultipleChoice.return_value = 'bar'
        ra = Mock()
        self.target._routeAssign = ra

        actual = self.target.askManualFix()

        self.assertEqual(actual, True)
        ra.assert_called_once_with(self.mockAlbum, 'foo', 'bar')

    @patch('pyTagger.actions.tag_album.ask')
    def test_askManualFix_control_c(self, ask):
        self.target._addToAsk(self.mockAlbum, 'foo', [u'alpha', u'beta'])
        self.target._addToAsk(self.mockAlbum, 'bar', [u'alpha', u'beta'])
        ask.askOrEnterMultipleChoice.side_effect = KeyboardInterrupt
        actual = self.target.askManualFix()
        self.assertEqual(actual, False)
        self.assertEqual(self.target.userDiscard, True)

    def test_bail_userQuit(self):
        self.target.userQuit = True
        self.assertEqual(self.target.bail(), True)

    def test_bail_userDiscard(self):
        self.target.userDiscard = True
        self.assertEqual(self.target.bail(), True)

    def test_bail_default(self):
        self.assertEqual(self.target.bail(), False)

    @patch('pyTagger.actions.tag_album.ask')
    def test_conduct_option1(self, ask):
        ask.askMultipleChoice.return_value = '1'
        self.target.bail = Mock(side_effect=[False, True])
        self.target.applyAutoFix = Mock()

        self.target.conduct({})
        self.assertEqual(self.target._triage.call_count, 2)
        self.assertEqual(self.target.applyAutoFix.call_count, 1)

    @patch('pyTagger.actions.tag_album.ask')
    def test_conduct_option2(self, ask):
        ask.askMultipleChoice.return_value = '2'
        self.target.bail = Mock(side_effect=[False, True])
        self.target.askManualFix = Mock()

        self.target.conduct({})
        self.assertEqual(self.target._triage.call_count, 2)
        self.assertEqual(self.target.askManualFix.call_count, 1)

    @patch('pyTagger.actions.tag_album.ask')
    def test_conduct_option3(self, ask):
        ask.askMultipleChoice.return_value = '3'
        self.target.bail = Mock(side_effect=[False, True])
        self.target.askAlbumName = Mock()
        self.target.rebuild = Mock()

        self.target.conduct({})
        self.assertEqual(self.target._triage.call_count, 2)
        self.assertEqual(self.target.askAlbumName.call_count, 1)
        self.assertEqual(self.target.rebuild.call_count, 1)

    @patch('pyTagger.actions.tag_album.ask')
    def test_conduct_optionS(self, ask):
        ask.askMultipleChoice.return_value = 'S'
        self.target.bail = Mock(side_effect=[False, True])
        self.target.save = Mock()

        import sys
        with patch.object(sys, 'argv', ['test', '--tag-album-file', 'f.json']):
            options = configurationOptions('tag-album')

        self.target.conduct(options)
        self.assertEqual(self.target._triage.call_count, 1)
        self.target.save.assert_called_once_with('f.json')

    @patch('pyTagger.actions.tag_album.ask')
    def test_conduct_optionX(self, ask):
        ask.askMultipleChoice.return_value = 'X'
        self.target.conduct({})
        self.assertEqual(self.target._triage.call_count, 1)
        self.assertEqual(self.target.userQuit, True)
        self.assertEqual(self.target.userDiscard, False)

    @patch('pyTagger.actions.tag_album.ask')
    def test_conduct_optionZ(self, ask):
        ask.askMultipleChoice.return_value = 'Z'
        self.target.conduct({})
        self.assertEqual(self.target._triage.call_count, 1)
        self.assertEqual(self.target.userQuit, False)
        self.assertEqual(self.target.userDiscard, True)

    @patch('pyTagger.actions.tag_album.ask')
    def test_conduct_control_c(self, ask):
        ask.askMultipleChoice.side_effect = KeyboardInterrupt
        self.target.conduct({})
        self.assertEqual(self.target._triage.call_count, 1)
        self.assertEqual(self.target.userQuit, False)
        self.assertEqual(self.target.userDiscard, True)


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
    logging.basicConfig()
    unittest.main()
