import unittest
import os
import sys
import shutil
import random
import pyTagger

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
                tags[k] = '2015-01-19' if k != 'year' else '2015'
        else:
            tags['year'] = '2015'
        return tags

    def test_deleteSimple(self):
        file = os.path.join(self.sourceDirectory, '08 - Killa Brew.mp3')
        shutil.copy(file, self.resultDirectory)
        
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)
        tags = self.buildSimpleTags(track.tag.version)
        for k,v in tags.items():
            tags[k] = None
        del tags['bpm']
        del tags['playCount']
        target._writeSimple(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        
        for k in tags.keys():
            assert not actualTags[k], k + ' : ' + repr(actualTags[k])

    def test_writeSimple(self):
        file = os.path.join(self.sourceDirectory, '08 - Killa Brew.mp3')
        shutil.copy(file, self.resultDirectory)
        
        target = pyTagger.update_from_snapshot.UpdateFromSnapshot()
        track = target._loadID3(file)
        tags = self.buildSimpleTags(track.tag.version)
        target._writeSimple(track,tags)
        target._saveID3(track)

        self.formatter = pyTagger.mp3_snapshot.Formatter(tags.keys())
        actualTags = self.verifier.extractTags(file, self.formatter)
        
        for k in tags.keys():
            assert actualTags[k] == tags[k], k + ' : ' + repr(actualTags[k])

if __name__ == '__main__':

    unittest.main()