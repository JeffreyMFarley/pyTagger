import unittest
import os
import sys
import shutil
import random
import pyTagger
import uuid
import binascii
from tests import *

SANDBOX_DIRECTORY = os.path.join(RESULT_DIRECTORY, r'mp3s')

class TestUpdateFromSnapshot(unittest.TestCase):
    stringFields = ['title',  'artist', 'albumArtist', 'album', 
                    'composer', 'conductor', 'remixer', 'publisher',
                    'genre', 'group', 'subtitle']
    numberFields = ['track', 'totalTrack', 'bpm', 'disc', 'totalDisc', 
                    'playCount']
    dateFields = ['year', 'releaseDate', 'originalReleaseDate',
                  'recordingDate', 'encodingDate', 'taggingDate']
    readOnlyFields = ['bitRate', 'fileHash', 'length', 'vbr']
    collectionFields = ['comments', 'id', 'lyrics', 'ufid']
    enumFields = {'key' : ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
                  'language' : ['ENG', 'DEU'],
                  'media' : ['DIG', 'CD', 'TT/33'],
                  'compilation' : ['0', '1'] }
    text = ['abc', 'def', 'ghi', 'jkl', u'Bj\xf6rk']

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(SANDBOX_DIRECTORY):
            os.makedirs(SANDBOX_DIRECTORY)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(SANDBOX_DIRECTORY)

    def setUp(self):
        assert sys.version < '3', 'This test must be run in Python 2.x'
        self.target = pyTagger.update_from_snapshot.UpdateFromSnapshot()

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def createTestableFile(self, path):
        subdir, filename = os.path.split(path)
        fromFile = os.path.join(SOURCE_DIRECTORY, path)
        shutil.copy(fromFile, SANDBOX_DIRECTORY)
        return os.path.join(SANDBOX_DIRECTORY, filename)

    def buildSimpleTags(self, version):
        tags = {}
        for k in self.stringFields:
            tags[k] = 'abc'
        for k in self.numberFields:
            tags[k] = random.randint(1,5)
        for k, values in self.enumFields.items():
            tags[k] = random.choice(values)

        if version[1] == 4:
            for k in self.dateFields:
                if k != 'year':
                    tags[k] = '2015-01-19'
        else:
            tags['year'] = '2015'
        return tags

    def buildSimpleTagsForDelete(self, version):
        tags = {}
        for k in self.stringFields:
            tags[k] = None
        for k in self.numberFields:
            if k not in ['bpm', 'playCount']:
                tags[k] = None
        for k, values in self.enumFields.items():
            tags[k] = None

        if version[1] == 4:
            for k in self.dateFields:
                if k != 'year':
                    tags[k] = None
        else:
            tags['year'] = None
        return tags

    def actualTags(self, tags, file):
        formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        verifier = pyTagger.Mp3Snapshot()
        return verifier.extractTags(file, formatter)

    # -------------------------------------------------------------------------
    # Write Simple Tests
    # -------------------------------------------------------------------------

    def test_deleteSimple_v22(self):
        file = self.createTestableFile(r'Test Files\iTunes 9 256 kbps.MP3')
        track = self.target._loadID3(file)
        tags = self.buildSimpleTagsForDelete(track.tag.version)

        self.target._writeSimple(track,tags)
        self.target._saveID3(track, (2,3,0))

        actualTags = self.actualTags(tags, file)
        for k in tags.keys():
            assert not actualTags[k], k + ' : ' + repr(actualTags[k])

    def test_deleteSimple_v23(self):
        file = self.createTestableFile('08 - Killa Brew.mp3')
        track = self.target._loadID3(file)
        tags = self.buildSimpleTagsForDelete(track.tag.version)

        self.target._writeSimple(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        for k in tags.keys():
            assert not actualTags[k], k + ' : ' + repr(actualTags[k])

    def test_deleteSimple_v24(self):
        file = self.createTestableFile(r'The King Of Limbs\05 LotusFlower.MP3')
        track = self.target._loadID3(file)
        tags = self.buildSimpleTagsForDelete(track.tag.version)

        self.target._writeSimple(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        for k in tags.keys():
            assert not actualTags[k], k + ' : ' + repr(actualTags[k])

    #def test_writeSimple_v10(self):
    #    file = self.createTestableFile(r'Test Files\ID3V1.MP3')

    def test_writeSimple_v22(self):
        file = self.createTestableFile(r'Test Files\iTunes 9 256 kbps.MP3')
        track = self.target._loadID3(file)
        tags = self.buildSimpleTags(track.tag.version)

        self.target._writeSimple(track,tags)
        self.target._saveID3(track, (2,3,0))

        actualTags = self.actualTags(tags, file)
        for k in tags.keys():
            assert actualTags[k] == tags[k], k + ' : ' + repr(actualTags[k])

    def test_writeSimple_v23(self):
        file = self.createTestableFile('08 - Killa Brew.mp3')
        track = self.target._loadID3(file)
        tags = self.buildSimpleTags(track.tag.version)

        self.target._writeSimple(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        for k in tags.keys():
            assert actualTags[k] == tags[k], k + ' : ' + repr(actualTags[k])

    def test_writeSimple_v24(self):
        file = self.createTestableFile(r'The King Of Limbs\05 LotusFlower.MP3')
        track = self.target._loadID3(file)
        tags = self.buildSimpleTags(track.tag.version)

        self.target._writeSimple(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        for k in tags.keys():
            assert actualTags[k] == tags[k], k + ' : ' + repr(actualTags[k])

    # -------------------------------------------------------------------------
    # Write Collection Tests
    # -------------------------------------------------------------------------

    def test_writeCollection_addComment(self):
        file = self.createTestableFile(r'09 - Bite It.mp3')
        track = self.target._loadID3(file)
        tags = { 'comments' : [{'lang': 'eng', 'text': 'here is some text', 'description': ''}]}

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['comments']
        assert actual
        assert len(actual) == 1
        assert actual[0]['text'] == 'here is some text'

    def test_writeCollection_addAnotherComment(self):
        file = self.createTestableFile('10 World\'s Famous.mp3')
        tags = { 'comments' : [{'lang': 'eng', 'text': '0.80', 'description': 'echonest dance'}]}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['comments']
        assert actual
        assert len(actual) == 2
        assert '0.80' == actual[1]['text'] if actual[1]['description'] == 'echonest dance' else actual[0]['text']

    def test_writeCollection_updateComment(self):
        file = self.createTestableFile(r'Test Files\From Amazon.mp3')
        tags = { 'comments' : [{'lang': 'eng', 'text': 'here is some text', 'description': ''}]}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['comments']
        assert actual
        assert len(actual) == 1
        assert actual[0]['text'] == 'here is some text'

    def test_writeCollection_deleteComment(self):
        file = self.createTestableFile(r'Test Files\From Amazon.mp3')
        tags = { 'comments' : [{'lang': 'eng', 'text': '', 'description': ''}]}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        assert not actualTags['comments']

    def test_writeCollection_addLyrics(self):
        file = self.createTestableFile('07 - Toddler Hiway.mp3')
        tags = { 'lyrics' : [{'lang': 'eng', 'text': 'tippie toe to the front room', 'description': ''}]}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['lyrics']
        assert actual
        assert len(actual) == 1
        assert actual[0]['text'] == 'tippie toe to the front room'

    def test_writeCollection_addAnotherLyrics(self):
        file = self.createTestableFile('08 Kaulana Na Pua.mp3')
        tags = { 'lyrics' : [{'lang': 'haw', 'text': 'kaulana na pua', 'description': ''}]}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['lyrics']
        assert actual
        assert len(actual) == 2
        assert 'kaulana na pua' == actual[1]['text'] if actual[1]['lang'] == 'haw' else actual[0]['text']

    def test_writeCollection_updateLyrics(self):
        file = self.createTestableFile('08 Kaulana Na Pua.mp3')
        tags = { 'lyrics' : [{'lang': 'eng', 'text': 'the english translation', 'description': ''}]}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['lyrics']
        assert actual
        assert len(actual) == 1
        assert actual[0]['text'] == 'the english translation'

    def test_writeCollection_deleteLyrics(self):
        file = self.createTestableFile('05 - In Da Club.mp3')
        tags = { 'lyrics' : [{'lang': 'eng', 'text': '', 'description': ''}]}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        assert not actualTags['lyrics']

    def test_writeCollection_addFileId(self):
        file = self.createTestableFile(r'The King Of Limbs\05 LotusFlower.MP3')
        id = uuid.uuid1()
        tags = { 'ufid' : {'DJTagger': id.bytes}}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['ufid']
        assert actual
        assert len(actual) == 1
        assert actual['DJTagger'] == binascii.b2a_base64(id.bytes).strip()

    def test_writeCollection_addAnotherFileId(self):
        file = self.createTestableFile(r'05 - In Da Club.mp3')
        id = uuid.uuid1()
        tags = { 'ufid' : {'CDDB': id.bytes}}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['ufid']
        assert actual
        assert len(actual) == 2
        assert actual['DJTagger'] == 'C3KEMBFzlkKrEy/e1xTKuA=='
        assert actual['CDDB'] == binascii.b2a_base64(id.bytes).strip()

    def test_writeCollection_updateFileId(self):
        file = self.createTestableFile('05 - In Da Club.mp3')
        id = uuid.uuid1()
        tags = { 'ufid' : {'DJTagger': id.bytes}}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['ufid']
        assert actual
        assert len(actual) == 1
        assert actual['DJTagger'] == binascii.b2a_base64(id.bytes).strip()

    def test_writeCollection_deleteFileId(self):
        file = self.createTestableFile('05 - In Da Club.mp3')
        tags = { 'ufid' : {'DJTagger': ''}}
        track = self.target._loadID3(file)

        self.target._writeCollection(track,tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        actual = actualTags['ufid']
        assert not actualTags['ufid']

    # -------------------------------------------------------------------------
    # Other Write Tests
    # -------------------------------------------------------------------------
    def test_writeConsolidated(self):
        file = self.createTestableFile(r'The King Of Limbs\05 LotusFlower.MP3')
        id = uuid.uuid1()
        tags = self.buildSimpleTags((2,4,0))
        tags['comments'] = [{'lang': 'eng', 'text': 'here is some text', 'description': ''}]
        tags['ufid'] = {'DJTagger': id.bytes}
        tags['lyrics'] = [{'lang': 'eng', 'text': 'I will shake myself into your pocket\nInvisible', 'description': ''}]
        track = self.target._loadID3(file)

        self.target._writeSimple(track,tags)
        self.target._writeCollection(track, tags)
        self.target._saveID3(track)

        actualTags = self.actualTags(tags, file)
        for k in tags.keys():
            if k == 'comments':
                assert len(actualTags[k]) == 1
                assert actualTags[k][0]['text'] == 'here is some text'
            elif k == 'ufid':
                assert len(actualTags[k]) == 1
                assert actualTags[k]['DJTagger'] == binascii.b2a_base64(id.bytes).strip()
            elif k == 'lyrics':
                assert len(actualTags[k]) == 1
                assert actualTags[k][0]['text'] == 'I will shake myself into your pocket\nInvisible'
            else:
                assert actualTags[k] == tags[k], k + ' : ' + repr(actualTags[k])

    # -------------------------------------------------------------------------
    # Find Delta Tests
    # -------------------------------------------------------------------------

    def test_a_greaterThan_b(self):
        a = {'title' : 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {'album': 'ghi'}
        expected = {'title' : 'abc',  'artist': 'def'}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lessThan_b(self):
        a = {'album': 'ghi'}
        b = {'title' : 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_isNull(self):
        a = {}
        b = {'title' : 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_isNull(self):
        a = {'title' : 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {}
        expected = a
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleEqual_b(self):
        a = {'title' : 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {'title' : 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleNotEqual_b(self):
        a = {'title' : 'cde',  'artist': 'def', 'album': 'ghi'}
        b = {'title' : 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {'title' : 'cde'}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleIsNull(self):
        a = {'title' : '',  'artist': 'def', 'album': 'ghi'}
        b = {'title' : 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {'title' : None}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_simpleIsNull(self):
        a = {'title' : 'cde',  'artist': 'def', 'album': 'ghi'}
        b = {'title' : '',  'artist': 'def', 'album': 'ghi'}
        expected = {'title' : 'cde'}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentsGreaterThan_b(self):
        a = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                            {'lang': 'esp', 'text': 'hola', 'description': ''},
                            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                            ]}
        b = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        expected = { 'comments' : [{'lang': 'esp', 'text': 'hola', 'description': ''},
                                   {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                                   ]}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_commentsGreaterThan_a(self):
        a = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        b = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                            {'lang': 'esp', 'text': 'hola', 'description': ''},
                            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                            ]}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentEqual_b(self):
        a = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                            {'lang': 'esp', 'text': 'hola', 'description': ''},
                            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                            ]}
        b = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                            {'lang': 'esp', 'text': 'hola', 'description': ''},
                            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                            ]}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentNotEqual_b(self):
        a = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                            {'lang': 'esp', 'text': 'hola', 'description': ''},
                            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                            ]}
        b = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                            {'lang': 'esp', 'text': 'hola', 'description': ''},
                            {'lang': 'fra', 'text': 'bon', 'description': ''}
                            ]}
        expected = { 'comments' : [{'lang': 'fra', 'text': 'bonjour', 'description': ''}]}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentIsNull(self):
        a = { 'comments' : []}
        b = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                            {'lang': 'esp', 'text': 'hola', 'description': ''},
                            {'lang': 'fra', 'text': 'bon', 'description': ''}
                            ]}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_commentIsNull(self):
        a = { 'comments' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                            {'lang': 'esp', 'text': 'hola', 'description': ''},
                            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                            ]}
        b = { 'comments' : []}
        expected = a
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricsGreaterThan_b(self):
        a = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        expected = { 'lyrics' : [{'lang': 'esp', 'text': 'hola', 'description': ''},
                                 {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                                 ]}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_lyricsGreaterThan_a(self):
        a = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        b = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricEqual_b(self):
        a = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricNotEqual_b(self):
        a = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bon', 'description': ''}
                          ]}
        expected = { 'lyrics' : [{'lang': 'fra', 'text': 'bonjour', 'description': ''}]}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricIsNull(self):
        a = { 'lyrics' : []}
        b = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bon', 'description': ''}
                          ]}
        expected = {}
        
        actual = self.target._findDelta(a, b);
        
        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_lyricIsNull(self):
        a = { 'lyrics' : [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = { 'lyrics' : []}
        expected = a
        
        actual = self.target._findDelta(a, b);

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idsGreaterThan_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = { 'ufid' : {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = { 'ufid' : {'def': id2.bytes}}
        expected = { 'ufid' : {'abc': id1.bytes, 'ghi': id3.bytes}}

        actual = self.target._findDelta(a, b);

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_idsGreaterThan_a(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = { 'ufid' : {'def': id2.bytes}}
        b = { 'ufid' : {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = self.target._findDelta(a, b);

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idEqual_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = { 'ufid' : {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = { 'ufid' : {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = self.target._findDelta(a, b);

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idNotEqual_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        id4 = uuid.uuid1()
        a = { 'ufid' : {'abc': id4.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = { 'ufid' : {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = { 'ufid' : {'abc': id4.bytes}}

        actual = self.target._findDelta(a, b);

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idIsNull(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = { 'ufid' : {} }
        b = { 'ufid' : {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = self.target._findDelta(a, b);

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_idIsNull(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = { 'ufid' : {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = { 'ufid' : {} }
        expected = a

        actual = self.target._findDelta(a, b);

        self.assertDictEqual(expected, actual, repr(actual))

if __name__ == '__main__':

    unittest.main()