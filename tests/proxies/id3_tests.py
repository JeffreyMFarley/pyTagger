from __future__ import unicode_literals
import unittest
import itertools
import pyTagger.proxies.id3 as sut
import random
import shutil
from tests import *
from contextlib import contextmanager
from pyTagger.models import Snapshot
from pyTagger.operations.hash import hashBuffer, hashFile
from pyTagger.utils import generateUfid

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

SANDBOX_DIRECTORY = os.path.join(RESULT_DIRECTORY, 'mp3s')


def setUpModule():
    if sampleFilesExist and not os.path.exists(SANDBOX_DIRECTORY):
        os.makedirs(SANDBOX_DIRECTORY)


def tearDownModule():
    if os.path.exists(SANDBOX_DIRECTORY):
        shutil.rmtree(SANDBOX_DIRECTORY)


def buildFormula():
    greek_lower_d = '\u03b4'
    dot_multiply = '\u00b7'
    greater_than_or_equal = '\u2265'
    divide = '\u2044'
    pi = '\u03c0'
    title = ''.join([
        greek_lower_d, 'p', dot_multiply, greek_lower_d, 'q',
        greater_than_or_equal, 'h', divide, '4', pi
    ])
    return title


class TestID3Proxy(unittest.TestCase):
    def setUp(self):
        self.target = sut.ID3Proxy()

    def test_allFieldsGrouped(self):
        columns = Snapshot.orderedAllColumns()
        missing = set(self.target.columns) - set(columns)
        assert not missing

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extractImages(self):
        fileName = os.path.join(SOURCE_DIRECTORY, '08 - Aeroplane.mp3')

        track = self.target.loadID3(fileName)
        for image_data, mime_type in self.target.extractImages(track):
            hashed = hashBuffer(image_data)
            self.assertEqual(hashed, 'I7chTVcNee01gK3FwAxV6lrXoWk=')
            self.assertEqual(mime_type, 'jpeg')

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_basic(self):
        self.target = sut.ID3Proxy(Snapshot.basic)
        fileName = os.path.join(
            SOURCE_DIRECTORY, 'The King Of Limbs', '05 LotusFlower.MP3'
        )

        row = self.target.extractTags(fileName)

        assert row
        assert row['title'] == 'Lotus Flower'
        assert 'fileHash' not in row

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_full_v10(self):
        fileName = os.path.join(SOURCE_DIRECTORY, 'Test Files', 'ID3V1.mp3')

        row = self.target.extractTags(fileName)

        assert row
        assert row['version'] == '1.0.0', row['version']
        assert row['title'] == 'West End Girls', row['title']
        assert row['artist'] == 'Petshop Boys', row['artist']

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_full_v22(self):
        fileName = os.path.join(
            SOURCE_DIRECTORY, 'Test Files', 'iTunes 9 256 kbps.mp3'
        )

        row = self.target.extractTags(fileName)

        assert row
        assert row['version'] == '2.2.0', row['version']
        assert row['track'] == 1, row['track']
        assert row['title'] == 'Granddad\'s Opening Address', row['title']
        assert row['artist'] == 'Geggy Tah', row['artist']
        assert row['year'] == '1996', row['year']

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_full_v23(self):
        fileName = os.path.join(SOURCE_DIRECTORY, '01 - Bust A Move.mp3')

        row = self.target.extractTags(fileName)

        assert row
        assert row['version'] == '2.3.0', row['version']
        assert row['track'] == 1, row['track']
        assert row['title'] == 'Bust A Move', row['title']
        assert row['artist'] == 'Young MC', row['artist']
        assert row['year'] == '1989', row['year']

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_full_v24(self):
        fileName = os.path.join(
            SOURCE_DIRECTORY, 'The King Of Limbs', '05 LotusFlower.MP3'
        )

        row = self.target.extractTags(fileName)

        assert row
        assert row['version'] == '2.4.0', row['version']
        assert row['track'] == 5, row['track']
        assert row['title'] == 'Lotus Flower', row['title']
        assert row['artist'] == 'Radiohead', row['artist']
        assert row['year'] == '2011', row['year']
        assert 'fileHash' in row
        assert row['fileHash']

    def test_extract_badfile(self):
        fileName = os.path.join(SOURCE_DIRECTORY, 'kafafasfaafaf.mp3')

        row = self.target.extractTags(fileName)

        assert not row

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_utf8(self):
        fileName = os.path.join(SOURCE_DIRECTORY, '08 - Aeroplane.mp3')

        row = self.target.extractTags(fileName)

        assert row
        assert row['artist'] == 'Bj\xf6rk'

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_non_ascii_filename(self):
        title = buildFormula()
        fileName = os.path.join(SOURCE_DIRECTORY, '10 '+title+'.mp3')

        row = self.target.extractTags(fileName)

        assert row
        assert row['title'] == title
        assert row['artist'] == 'T\xe9l\xe9popmusik'

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_calculate_hash(self):
        fileName = os.path.join(SOURCE_DIRECTORY, '10 World\'s Famous.mp3')
        track = self.target.loadID3(fileName)
        actual = self.target._calculateHash(track, fileName)
        self.assertEqual(actual, 'Bf4eOMgTeKkeNxKH345RQHF2GLU=')

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_calculate_hash_only_hashes_mp3data(self):
        fileName = os.path.join(SOURCE_DIRECTORY, '10 World\'s Famous.mp3')
        track = self.target.loadID3(fileName)
        hash1 = self.target._calculateHash(track, fileName)
        hash2 = hashFile(fileName)
        self.assertNotEqual(hash1, hash2)


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
    text = ['abc', 'def', 'ghi', 'jkl', 'Bj\xf6rk']

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def setUp(self):
        pass

    @contextmanager
    def useFile(self, path, tags, actual):
        subdir, filename = os.path.split(path)
        fromFile = os.path.join(SOURCE_DIRECTORY, path)
        shutil.copy(fromFile, SANDBOX_DIRECTORY)
        fileName = os.path.join(SANDBOX_DIRECTORY, filename)
        id3Reader = sut.ID3Proxy(tags.keys())
        track = id3Reader.loadID3(fileName)
        yield track
        self.saveTrack(track)
        actual.update(id3Reader.extractTags(fileName))

    def saveTrack(self, track):
        track.tag.save()

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

        with self.useFile('Her Majesty.mp3', tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_removes_simple_tags(self):
        tags = {'title': '', 'artist': '', 'album': ''}
        actual = {}
        expected = {'title': None, 'artist': None, 'album': None}

        with self.useFile('Her Majesty.mp3', tags, actual) as track:
            sut._update(track, tags)

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

        with self.useFile('Her Majesty.mp3', tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_removes_simple_tags(self):
        tags = {'track': '', 'title': '', 'artist': '', 'album': ''}
        actual = {}
        expected = {
            'track': None, 'title': None, 'artist': None, 'album': None
        }

        with self.useFile('13 aussois.mp3', tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text',
            'description': 'ID3v1.x Comment'
        }]}
        actual = {}

        with self.useFile('13 aussois.mp3', tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))


class ID3V22_Snapshot(BaseSpecifications):
    minimal = '05 Mr. Zebra.mp3'
    hasLyrics = '06 Getting Ahead In The Lucrative Field Of Artist Managmt.mp3'
    hasComments = hasLyrics
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
        track.tag.save(version=(2, 3, 0))

    def test_adds_missing_simple_tags(self):
        tags = {
            'albumArtist': 'abc', 'bpm': 120, 'composer': 'ghi', 'key': 'G',
            'language': 'ENG', 'disc': 1, 'totalDisc': 1
        }
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_updates_simple_tags(self):
        tags = self.buildSimpleTags()
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_adds_comment_when_none_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': 'other'
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text',
            'description': 'iTunNORM'
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_lyric_when_some_exist(self):
        tags = {'lyrics': [{
            'lang': 'eng', 'text': 'here is some text', 'description': 'other'
        }]}
        actual = {}

        with self.useFile(self.hasLyrics, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_lyric_when_some_exist(self):
        tags = {'lyrics': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_ufid_when_none_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'DJTagger': ufid}}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            sut._update(track, tags)

        assert len(actual['ufid']) == 1
        assert actual['ufid']['DJTagger'] == ufid

    def test_adds_ufid_when_some_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'DJTagger': ufid}}
        actual = {}

        with self.useFile(self.hasUfid, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_ufid_when_some_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'http://www.cddb.com/id3/taginfo1.html': ufid}}
        actual = {}
        expected = tags

        with self.useFile(self.hasUfid, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_updates_simple_tags(self):
        tags = self.buildSimpleTags()
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_adds_comment_when_none_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': 'other'
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_comment_when_some_exist(self):
        tags = {'comments': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_lyric_when_none_exist(self):
        tags = {'lyrics': [{
            'lang': 'haw', 'text': u'Kaulana n\u0101 pua a\u02bbo Hawai\u02bbi',
            'description': ''
        }]}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_lyric_when_some_exist(self):
        tags = {'lyrics': [{
            'lang': 'haw', 'text': u'Kaulana n\u0101 pua a\u02bbo Hawai\u02bbi',
            'description': 'other'
        }]}
        actual = {}

        with self.useFile(self.hasLyrics, tags, actual) as track:
            sut._update(track, tags)

        innerActual = actual['lyrics']
        assert len(innerActual) == 2
        expected = [x for x in innerActual if x['description'] == 'other']
        assert len(expected) == 1
        self.assertEqual(
            u'Kaulana n\u0101 pua a\u02bbo Hawai\u02bbi', expected[0]['text']
        )

    def test_removes_lyric_when_some_exist(self):
        tags = {'lyrics': [{'lang': 'eng', 'text': '', 'description': ''}]}
        actual = {}
        expected = {'lyrics': []}

        with self.useFile(self.hasLyrics, tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_lyric_when_some_exist(self):
        tags = {'lyrics': [{
            'lang': 'eng', 'text': 'here is some text', 'description': ''
        }]}
        actual = {}

        with self.useFile(self.hasComments, tags, actual) as track:
            sut._update(track, tags)

        self.assertDictEqual(tags, actual, repr(actual))

    def test_adds_ufid_when_none_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'DJTagger': ufid}}
        actual = {}

        with self.useFile(self.minimal, tags, actual) as track:
            sut._update(track, tags)

        assert len(actual['ufid']) == 1
        assert actual['ufid']['DJTagger'] == ufid

    def test_adds_ufid_when_some_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'echonest': ufid}}
        actual = {}

        with self.useFile(self.hasUfid, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_updates_ufid_when_some_exist(self):
        ufid = generateUfid()
        tags = {'ufid': {'DJTagger': ufid}}
        actual = {}
        expected = tags

        with self.useFile(self.hasUfid, tags, actual) as track:
            sut._update(track, tags)

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
            sut._update(track, tags)

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
            sut._update(track, tags)

        self.assertDictEqual(expected, actual, repr(actual))

    @unittest.skip('The test file does not contain an existing UFID')
    def test_adds_ufid_when_some_exist(self):
        pass


del(BaseSpecifications)

if __name__ == '__main__':
    unittest.main()
