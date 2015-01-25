import unittest
import os
import sys
import shutil
import random
import pyTagger
import uuid
import binascii

class TestUpdateFromSnapshot(unittest.TestCase):

    def setUp(self):
        assert sys.version < '3', 'This test must be run in Python 2.x'

        self.sourceDirectory = r'C:\dvp\MP3Tools\SampleData'
        self.resultDirectory = r'C:\dvp\MP3Tools\TestOutput\mp3s'
        if not os.path.exists(self.resultDirectory):
            os.makedirs(self.resultDirectory)

        self.verifier = pyTagger.Mp3Snapshot()
        self.stringFields = ['title',  'artist', 'albumArtist', 'album',
                             'composer', 'conductor', 'remixer', 'publisher',
                             'genre', 'group', 'subtitle']
        self.numberFields = ['track', 'totalTrack', 'bpm', 'disc', 'totalDisc',
                             'playCount']
        self.dateFields = ['year', 'releaseDate', 'originalReleaseDate',
                           'recordingDate', 'encodingDate', 'taggingDate']
        self.readOnlyFields = ['bitRate', 'fileHash', 'length', 'vbr']
        self.collectionFields = ['comments', 'id', 'lyrics', 'ufid']
        self.enumFields = {'key' : ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
                           'language' : ['ENG', 'DEU'],
                           'media' : ['DIG', 'CD', 'TT/33'],
                           'compilation' : ['0', '1']
                           }
        self.text = ['abc', 'def', 'ghi', 'jkl', u'Bj\xf6rk']

    def tearDown(self):
        shutil.rmtree(self.resultDirectory)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def createTestableFile(self, path):
        subdir, filename = os.path.split(path)
        fromFile = os.path.join(self.sourceDirectory, path)
        shutil.copy(fromFile, self.resultDirectory)
        return os.path.join(self.resultDirectory, filename)

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

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_deleteSimple_v22(self):
        file = self.createTestableFile(r'Test Files\iTunes 9 256 kbps.MP3')
        
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)
        tags = self.buildSimpleTagsForDelete(track.tag.version)
        target._writeSimple(track,tags)
        target._saveID3(track, (2,3,0))

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        
        for k in tags.keys():
            assert not actualTags[k], k + ' : ' + repr(actualTags[k])

    def test_deleteSimple_v23(self):
        file = self.createTestableFile('08 - Killa Brew.mp3')
        
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)
        tags = self.buildSimpleTagsForDelete(track.tag.version)
        target._writeSimple(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        
        for k in tags.keys():
            assert not actualTags[k], k + ' : ' + repr(actualTags[k])

    def test_deleteSimple_v24(self):
        file = self.createTestableFile(r'The King Of Limbs\05 LotusFlower.MP3')
        
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)
        tags = self.buildSimpleTagsForDelete(track.tag.version)
        target._writeSimple(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        
        for k in tags.keys():
            assert not actualTags[k], k + ' : ' + repr(actualTags[k])

    #def test_writeSimple_v10(self):
    #    file = self.createTestableFile(r'Test Files\ID3V1.MP3')

    def test_writeSimple_v22(self):
        file = self.createTestableFile(r'Test Files\iTunes 9 256 kbps.MP3')
        
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)
        tags = self.buildSimpleTags(track.tag.version)
        target._writeSimple(track,tags)
        target._saveID3(track, (2,3,0))

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        
        for k in tags.keys():
            assert actualTags[k] == tags[k], k + ' : ' + repr(actualTags[k])

    def test_writeSimple_v23(self):
        file = self.createTestableFile('08 - Killa Brew.mp3')
        
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)
        tags = self.buildSimpleTags(track.tag.version)
        target._writeSimple(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        
        for k in tags.keys():
            assert actualTags[k] == tags[k], k + ' : ' + repr(actualTags[k])

    def test_writeSimple_v24(self):
        file = self.createTestableFile(r'The King Of Limbs\05 LotusFlower.MP3')
        
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)
        tags = self.buildSimpleTags(track.tag.version)
        target._writeSimple(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        
        for k in tags.keys():
            assert actualTags[k] == tags[k], k + ' : ' + repr(actualTags[k])

    def test_writeCollection_addComment(self):
        file = self.createTestableFile(r'09 - Bite It.mp3')
        tags = { 'comments' : [{'lang': 'eng', 'text': 'here is some text', 'description': ''}]}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['comments']

        assert actual
        assert len(actual) == 1
        assert actual[0]['text'] == 'here is some text'

    def test_writeCollection_addAnotherComment(self):
        file = self.createTestableFile('10 World\'s Famous.mp3')
        tags = { 'comments' : [{'lang': 'eng', 'text': '0.80', 'description': 'echonest dance'}]}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['comments']

        assert actual
        assert len(actual) == 2
        assert '0.80' == actual[1]['text'] if actual[1]['description'] == 'echonest dance' else actual[0]['text']

    def test_writeCollection_updateComment(self):
        file = self.createTestableFile(r'Test Files\From Amazon.mp3')
        tags = { 'comments' : [{'lang': 'eng', 'text': 'here is some text', 'description': ''}]}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['comments']

        assert actual
        assert len(actual) == 1
        assert actual[0]['text'] == 'here is some text'

    def test_writeCollection_deleteComment(self):
        file = self.createTestableFile(r'Test Files\From Amazon.mp3')
        tags = { 'comments' : [{'lang': 'eng', 'text': '', 'description': ''}]}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)

        assert not actualTags['comments']

    def test_writeCollection_addLyrics(self):
        file = self.createTestableFile('07 - Toddler Hiway.mp3')
        tags = { 'lyrics' : [{'lang': 'eng', 'text': 'tippie toe to the front room', 'description': ''}]}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['lyrics']

        assert actual
        assert len(actual) == 1
        assert actual[0]['text'] == 'tippie toe to the front room'

    def test_writeCollection_addAnotherLyrics(self):
        file = self.createTestableFile('08 Kaulana Na Pua.mp3')
        tags = { 'lyrics' : [{'lang': 'haw', 'text': 'kaulana na pua', 'description': ''}]}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['lyrics']

        assert actual
        assert len(actual) == 2
        assert 'kaulana na pua' == actual[1]['text'] if actual[1]['lang'] == 'haw' else actual[0]['text']

    def test_writeCollection_updateLyrics(self):
        file = self.createTestableFile('08 Kaulana Na Pua.mp3')
        tags = { 'lyrics' : [{'lang': 'eng', 'text': 'the english translation', 'description': ''}]}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['lyrics']

        assert actual
        assert len(actual) == 1
        assert actual[0]['text'] == 'the english translation'

    def test_writeCollection_deleteLyrics(self):
        file = self.createTestableFile('05 - In Da Club.mp3')
        tags = { 'lyrics' : [{'lang': 'eng', 'text': '', 'description': ''}]}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)

        assert not actualTags['lyrics']

    def test_writeCollection_addFileId(self):
        file = self.createTestableFile(r'The King Of Limbs\05 LotusFlower.MP3')
        id = uuid.uuid1()
        tags = { 'ufid' : {'DJTagger': id.bytes}}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['ufid']

        assert actual
        assert len(actual) == 1
        assert actual['DJTagger'] == binascii.b2a_base64(id.bytes).strip()

    def test_writeCollection_addAnotherFileId(self):
        file = self.createTestableFile(r'05 - In Da Club.mp3')
        id = uuid.uuid1()
        tags = { 'ufid' : {'CDDB': id.bytes}}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['ufid']

        assert actual
        assert len(actual) == 2
        assert actual['DJTagger'] == 'C3KEMBFzlkKrEy/e1xTKuA=='
        assert actual['CDDB'] == binascii.b2a_base64(id.bytes).strip()

    def test_writeCollection_updateFileId(self):
        file = self.createTestableFile('05 - In Da Club.mp3')
        id = uuid.uuid1()
        tags = { 'ufid' : {'DJTagger': id.bytes}}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['ufid']

        assert actual
        assert len(actual) == 1
        assert actual['DJTagger'] == binascii.b2a_base64(id.bytes).strip()

    def test_writeCollection_deleteFileId(self):
        file = self.createTestableFile('05 - In Da Club.mp3')
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        tags = { 'ufid' : {'DJTagger': ''}}
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)

        target._writeCollection(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        actual = actualTags['ufid']

        assert not actualTags['ufid']

if __name__ == '__main__':

    unittest.main()