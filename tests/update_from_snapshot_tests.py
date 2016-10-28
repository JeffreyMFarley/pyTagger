import itertools
import os
import pyTagger
import random
import shutil
import sys
import unittest
import uuid
from tests import *
from contextlib import contextmanager
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import generateUfid

SANDBOX_DIRECTORY = os.path.join(RESULT_DIRECTORY, r'mp3s')


def setUpModule():
    if sampleFilesExist and not os.path.exists(SANDBOX_DIRECTORY):
        os.makedirs(SANDBOX_DIRECTORY)


def tearDownModule():
    if os.path.exists(SANDBOX_DIRECTORY):
        shutil.rmtree(SANDBOX_DIRECTORY)


class BaseSpecifications(unittest.TestCase):
    stringFields = ['title',  'artist', 'albumArtist', 'album',
                    'composer', 'conductor', 'remixer', 'publisher',
                    'genre', 'group', 'subtitle']
    numberFields = ['track', 'totalTrack', 'bpm', 'disc', 'totalDisc',
                    'playCount']
    dateFields = ['releaseDate', 'originalReleaseDate',
                  'recordingDate', 'encodingDate', 'taggingDate']
    readOnlyFields = ['bitRate', 'fileHash', 'length', 'vbr']
    collectionFields = ['comments', 'id', 'lyrics', 'ufid']
    enumFields = {'key': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
                  'language': ['ENG', 'DEU'],
                  'media': ['DIG', 'CD', 'TT/33'],
                  'compilation': ['0', '1']}
    text = ['abc', 'def', 'ghi', 'jkl', u'Bj\xf6rk']

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def setUp(self):
        self.target = pyTagger.update_from_snapshot.UpdateFromSnapshot()

    @contextmanager
    def useFile(self, path, tags, actual):
        subdir, filename = os.path.split(path)
        fromFile = os.path.join(SOURCE_DIRECTORY, path)
        shutil.copy(fromFile, SANDBOX_DIRECTORY)
        fileName = os.path.join(SANDBOX_DIRECTORY, filename)
        id3Reader = ID3Proxy(tags.keys())
        track = id3Reader.loadID3(fileName)
        yield track
        self.saveTrack(track)
        actual.update(id3Reader.extractTags(fileName))

    def saveTrack(self, track):
        self.target._saveID3(track)

    # -------------------------------------------------------------------------
    # Required Overrides
    # -------------------------------------------------------------------------

    def test_adds_missing_simple_tags(self):
        raise NotImplementedError

    def test_updates_simple_tags(self):
        raise NotImplementedError

    def test_removes_simple_tags(self):
        raise NotImplementedError

    def test_adds_comment_when_none_exist(self):
        raise NotImplementedError

    def test_adds_comment_when_some_exist(self):
        raise NotImplementedError

    def test_removes_comment_when_some_exist(self):
        raise NotImplementedError

    def test_updates_comment_when_some_exist(self):
        raise NotImplementedError

    def test_adds_lyric_when_none_exist(self):
        raise NotImplementedError

    def test_adds_lyric_when_some_exist(self):
        raise NotImplementedError

    def test_removes_lyric_when_some_exist(self):
        raise NotImplementedError

    def test_updates_lyric_when_some_exist(self):
        raise NotImplementedError

    def test_adds_ufid_when_none_exist(self):
        raise NotImplementedError

    def test_adds_ufid_when_some_exist(self):
        raise NotImplementedError

    def test_removes_ufid_when_some_exist(self):
        raise NotImplementedError

    def test_updates_ufid_when_some_exist(self):
        raise NotImplementedError


class ID3V10_Snapshot(BaseSpecifications):
    def test_adds_missing_simple_tags(self):
        pass

    def test_updates_simple_tags(self):
        tags = {
            'title': 'abc', 'artist': 'def', 'album': 'ghi', 'year': '1999',
            'genre': 'Blues'
        }
        actual = {}

        with self.useFile(r'Her Majesty.mp3', tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_removes_simple_tags(self):
        tags = {'title': '', 'artist': '', 'album': ''}
        actual = {}
        expected = {'title': None, 'artist': None, 'album': None}

        with self.useFile(r'Her Majesty.mp3', tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_adds_comment_when_none_exist(self):
        pass

    def test_adds_comment_when_some_exist(self):
        pass

    def test_removes_comment_when_some_exist(self):
        pass

    def test_updates_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text',
            'description': 'ID3v1.x Comment'
        }]}
        actual = {}

        with self.useFile(r'Her Majesty.mp3', tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_lyric_when_none_exist(self):
        pass

    def test_adds_lyric_when_some_exist(self):
        pass

    def test_removes_lyric_when_some_exist(self):
        pass

    def test_updates_lyric_when_some_exist(self):
        pass

    def test_adds_ufid_when_none_exist(self):
        pass

    def test_adds_ufid_when_some_exist(self):
        pass

    def test_removes_ufid_when_some_exist(self):
        pass

    def test_updates_ufid_when_some_exist(self):
        pass


class ID3V11_Snapshot(ID3V10_Snapshot):
    def test_updates_simple_tags(self):
        tags = {
            'track': 1, 'title': 'abc', 'artist': 'def', 'album': 'ghi',
            'year': '1983', 'genre': 'Blues'
        }
        actual = {}

        with self.useFile('13 aussois.mp3', tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_removes_simple_tags(self):
        tags = {'track': '', 'title': '', 'artist': '', 'album': ''}
        actual = {}
        expected = {
            'track': None, 'title': None, 'artist': None, 'album': None
        }

        with self.useFile('13 aussois.mp3', tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text',
            'description': 'ID3v1.x Comment'
        }]}
        actual = {}

        with self.useFile('13 aussois.mp3', tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))


class ID3V22_Snapshot(BaseSpecifications):
    minimal = '05 Mr. Zebra.mp3'
    hasComments = '06 Getting Ahead In The Lucrative Field Of Artist Managmt.mp3'
    hasLyrics = '06 Getting Ahead In The Lucrative Field Of Artist Managmt.mp3'
    hasUfid = os.sep.join(['Test Files', 'iTunes 9 256 kbps.mp3'])

    def buildSimpleTags(self):
        tags = {}
        for k in self.stringFields:
            tags[k] = random.choice(self.text)
        for k in self.numberFields:
            tags[k] = random.randint(1, 5)
        for k, values in self.enumFields.items():
            tags[k] = random.choice(values)
        tags['year'] = '2015'
        return tags

    def saveTrack(self, track):
        self.target._saveID3(track, (2, 3, 0))

    def test_adds_missing_simple_tags(self):
        tags = {
            'albumArtist': 'abc', 'bpm': 120, 'composer': 'ghi', 'key': 'G',
            'language': 'ENG', 'disc': 1, 'totalDisc': 1
        }
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_updates_simple_tags(self):
        tags = self.buildSimpleTags()
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_removes_simple_tags(self):
        tags = {k: None for k in itertools.chain(self.stringFields,
                                                 self.numberFields,
                                                 self.enumFields.keys(),
                                                 ['year'])
                if k not in ['bpm', 'playCount']}
        expected = dict(tags)
        expected.update({'track': 0, 'year': '', 'genre': ''})
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_adds_comment_when_none_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': 'other'
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            self.target._writeCollection(track, tags)

        innerActual = actual['comments']
        assert len(innerActual) == 3
        expected = [x for x in innerActual if x['description'] == 'other']
        assert len(expected) == 1
        assert 'here is some text' == expected[0]['text']

    def test_removes_comment_when_some_exist(self):
        tags = {'comments': [
            {'lang': 'eng', 'text': '', 'description': 'iTunNORM'},
            {'lang': 'eng', 'text': '', 'description': 'iTunes_CDDB_IDs'}
        ]}
        actual = {}
        expected = {'comments': []}

        with self.useFile(self.hasComments, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text',
            'description': 'iTunNORM'
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            self.target._writeCollection(track, tags)

        innerActual = actual['comments']
        assert len(innerActual) == 2
        expected = [x for x in innerActual if x['description'] == 'iTunNORM']
        assert len(expected) == 1
        assert 'here is some text' == expected[0]['text']

    def test_adds_lyric_when_none_exist(self):
        tags = {'lyrics': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_lyric_when_some_exist(self):
        tags = {'lyrics': [{
            'lang': 'eng', 'text': 'here is some text', 'description': 'other'
        }]}
        actual = {}

        with self.useFile(self.hasLyrics, tags, actual) as track:
            self.target._writeCollection(track, tags)

        innerActual = actual['lyrics']
        assert len(innerActual) == 2
        expected = [x for x in innerActual if x['description'] == 'other']
        assert len(expected) == 1
        assert 'here is some text' == expected[0]['text']

    def test_removes_lyric_when_some_exist(self):
        tags = {'lyrics': [{
            'lang': 'eng', 'text': '', 'description': ''
        }]}
        actual = {}
        expected = {'lyrics': []}

        with self.useFile(self.hasLyrics, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_lyric_when_some_exist(self):
        tags = {'lyrics': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_ufid_when_none_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'DJTagger': ufid}}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeCollection(track, tags)

        assert len(actual['ufid']) == 1
        assert actual['ufid']['DJTagger'] == ufid

    def test_adds_ufid_when_some_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'DJTagger': ufid}}
        actual = {}

        with self.useFile(self.hasUfid, tags, actual) as track:
            self.target._writeCollection(track, tags)

        innerActual = actual['ufid']
        assert len(innerActual) == 2
        expected = {k: innerActual[k] for k in innerActual if k == 'DJTagger'}
        assert len(expected) == 1
        assert expected['DJTagger'] == ufid

    def test_removes_ufid_when_some_exist(self):
        tags = {'ufid': {'http://www.cddb.com/id3/taginfo1.html': None}}
        actual = {}
        expected = {'ufid': {}}

        with self.useFile(self.hasUfid, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_ufid_when_some_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'http://www.cddb.com/id3/taginfo1.html': ufid}}
        actual = {}
        expected = tags

        with self.useFile(self.hasUfid, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))


class ID3V23_Snapshot(BaseSpecifications):
    minimal = os.sep.join(['Test Files', 'WMP 10 256kbps.mp3'])
    hasComments = '05 - In Da Club.mp3'
    hasLyrics = '05 - In Da Club.mp3'
    hasUfid = '05 - In Da Club.mp3'

    def buildSimpleTags(self):
        tags = {}
        for k in self.stringFields:
            tags[k] = random.choice(self.text)
        for k in self.numberFields:
            tags[k] = random.randint(1, 5)
        for k, values in self.enumFields.items():
            tags[k] = random.choice(values)
        tags['year'] = '2015'
        return tags

    def test_adds_missing_simple_tags(self):
        tags = {
            'albumArtist': 'abc', 'bpm': 120, 'composer': 'ghi', 'key': 'G',
            'language': 'ENG', 'disc': 1, 'totalDisc': 1
        }
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_updates_simple_tags(self):
        tags = self.buildSimpleTags()
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_removes_simple_tags(self):
        tags = {k: None for k in itertools.chain(self.stringFields,
                                                 self.numberFields,
                                                 self.enumFields.keys(),
                                                 ['year'])
                if k not in ['bpm', 'playCount']}
        expected = dict(tags)
        expected.update({'year': '', 'genre': ''})
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_adds_comment_when_none_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': 'other'
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            self.target._writeCollection(track, tags)

        innerActual = actual['comments']
        assert len(innerActual) == 2
        expected = [x for x in innerActual if x['description'] == 'other']
        assert len(expected) == 1
        assert 'here is some text' == expected[0]['text']

    def test_removes_comment_when_some_exist(self):
        tags = {'comments': [{'lang': 'eng', 'text': '', 'description': ''}]}
        actual = {}
        expected = {'comments': []}

        with self.useFile(self.hasComments, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_comment_when_some_exist(self):
        tags = {'comments': [{'lang': 'eng', 'text': 'here is some text', 'description': ''}]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_lyric_when_none_exist(self):
        tags = {'lyrics': [{'lang': 'eng', 'text': 'here is some text', 'description': ''}]}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_lyric_when_some_exist(self):
        tags = {'lyrics': [{'lang': 'eng', 'text': 'here is some text', 'description': 'other'}]}
        actual = {}

        with self.useFile(self.hasLyrics, tags, actual) as track:
            self.target._writeCollection(track, tags)

        innerActual = actual['lyrics']
        assert len(innerActual) == 2
        expected = [x for x in innerActual if x['description'] == 'other']
        assert len(expected) == 1
        assert 'here is some text' == expected[0]['text']

    def test_removes_lyric_when_some_exist(self):
        tags = {'lyrics': [{'lang': 'eng', 'text': '', 'description': ''}]}
        actual = {}
        expected = {'lyrics': []}

        with self.useFile(self.hasLyrics, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_lyric_when_some_exist(self):
        tags = {'lyrics': [{'lang': 'eng', 'text': 'here is some text', 'description': ''}]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_ufid_when_none_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'DJTagger': ufid}}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeCollection(track, tags)

        assert len(actual['ufid']) == 1
        assert actual['ufid']['DJTagger'] == ufid

    def test_adds_ufid_when_some_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'echonest': ufid}}
        actual = {}

        with self.useFile(self.hasUfid, tags, actual) as track:
            self.target._writeCollection(track, tags)

        innerActual = actual['ufid']
        self.assertEqual(2, len(innerActual))
        expected = {k: innerActual[k] for k in innerActual if k == 'echonest'}
        assert len(expected) == 1
        assert expected['echonest'] == ufid

    def test_removes_ufid_when_some_exist(self):
        tags = {'ufid': {'DJTagger': None}}
        actual = {}
        expected = {'ufid': {}}

        with self.useFile(self.hasUfid, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_ufid_when_some_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'DJTagger': ufid}}
        actual = {}
        expected = tags

        with self.useFile(self.hasUfid, tags, actual) as track:
            self.target._writeCollection(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))


class ID3V24_Snapshot(ID3V23_Snapshot):
    minimal = '06 - Faust Arp.MP3'
    hasComments = '11 Swept Away.mp3'
    hasLyrics = '01 Bloom.MP3'
    hasUfid = '03 - Kitten Moon.mp3'

    def buildSimpleTags(self):
        tags = {}
        for k in self.stringFields:
            tags[k] = random.choice(self.text)
        for k in self.numberFields:
            tags[k] = random.randint(1, 5)
        for k, values in self.enumFields.items():
            tags[k] = random.choice(values)
        for k in self.dateFields:
            tags[k] = '2015-01-31'
        return tags

    def test_updates_simple_tags(self):
        tags = self.buildSimpleTags()
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_removes_simple_tags(self):
        tags = {k: None for k in itertools.chain(self.stringFields,
                                                 self.numberFields,
                                                 self.enumFields.keys(),
                                                 self.dateFields)
                if k not in ['bpm', 'playCount']}
        expected = dict(tags)
        expected.update({'genre': ''})
        expected.update({k: '' for k in self.dateFields})
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            self.target._writeSimple(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    @unittest.skip('The test file does not contain an existing UFID')
    def test_adds_ufid_when_some_exist(self):
        pass


class TestFindDelta(unittest.TestCase):
    def setUp(self):
        self.target = pyTagger.update_from_snapshot.UpdateFromSnapshot()

    def test_a_greaterThan_b(self):
        a = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {'album': 'ghi'}
        expected = {'title': 'abc',  'artist': 'def'}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lessThan_b(self):
        a = {'album': 'ghi'}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_isNull(self):
        a = {}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_isNull(self):
        a = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {}
        expected = a

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleEqual_b(self):
        a = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleNotEqual_b(self):
        a = {'title': 'cde',  'artist': 'def', 'album': 'ghi'}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {'title': 'cde'}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleIsNull(self):
        a = {'title': '',  'artist': 'def', 'album': 'ghi'}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {'title': None}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_simpleIsNull(self):
        a = {'title': 'cde',  'artist': 'def', 'album': 'ghi'}
        b = {'title': '',  'artist': 'def', 'album': 'ghi'}
        expected = {'title': 'cde'}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentsGreaterThan_b(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        expected = {'comments': [{'lang': 'esp', 'text': 'hola', 'description': ''},
                                 {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                                 ]}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_commentsGreaterThan_a(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentEqual_b(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentNotEqual_b(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bon', 'description': ''}
                          ]}
        expected = {'comments': [{'lang': 'fra', 'text': 'bonjour', 'description': ''}]}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentIsNull(self):
        a = {'comments': []}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bon', 'description': ''}
                          ]}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_commentIsNull(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = {'comments': []}
        expected = a

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricsGreaterThan_b(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        expected = {'lyrics': [{'lang': 'esp', 'text': 'hola', 'description': ''},
                               {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                               ]}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_lyricsGreaterThan_a(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricEqual_b(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricNotEqual_b(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bon', 'description': ''}
                        ]}
        expected = {'lyrics': [{'lang': 'fra', 'text': 'bonjour', 'description': ''}]}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricIsNull(self):
        a = {'lyrics': []}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bon', 'description': ''}
                        ]}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_lyricIsNull(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        b = {'lyrics': []}
        expected = a

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idsGreaterThan_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = {'ufid': {'def': id2.bytes}}
        expected = {'ufid': {'abc': id1.bytes, 'ghi': id3.bytes}}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_idsGreaterThan_a(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {'def': id2.bytes}}
        b = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idEqual_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idNotEqual_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        id4 = uuid.uuid1()
        a = {'ufid': {'abc': id4.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {'ufid': {'abc': id4.bytes}}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idIsNull(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {}}
        b = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_idIsNull(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = {'ufid': {}}
        expected = a

        actual = self.target._findDelta(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_empty_comments_not_added(self):
        a = [{'lang': 'eng', 'text': '', 'description': ''},
             {'lang': 'esp', 'text': '', 'description': ''},
             {'lang': 'fra', 'text': '', 'description': ''}]
        b = [{'lang': 'deu', 'text': 'guten tag', 'description': ''}]
        expected = []

        actual = self.target._findDeltaDLT(a, b)

        self.assertListEqual(expected, actual, repr(actual))


del(BaseSpecifications)

if __name__ == '__main__':
    unittest.main()
