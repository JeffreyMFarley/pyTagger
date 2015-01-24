# -*- coding: utf-8 -*

import unittest
import os
import sys
import pyTagger

class TestMp3Snapshot(unittest.TestCase):

    def setUp(self):
        assert sys.version < '3', 'This test must be run in Python 2.x'

        self.sourceDirectory = r'C:\dvp\MP3Tools\SampleData'
        self.resultDirectory = r'C:\dvp\MP3Tools\TestOutput'
        if not os.path.exists(self.resultDirectory):
            os.makedirs(self.resultDirectory)

    def tearDown(self):
        pass

    def buildFormula(self):
        greek_lower_d = u'\u03b4'
        dot_multiply = u'\u00b7'
        greater_than_or_equal = u'\u2265'
        divide = u'\u2044'
        pi = u'\u03c0'
        title = u''.join([greek_lower_d, 'p', dot_multiply, greek_lower_d, 'q', greater_than_or_equal, 'h', divide, '4', pi])
        return title

    def test_allFieldsGrouped(self):
        target = pyTagger.mp3_snapshot.Formatter()
        columns = target.orderedAllColumns()

        # for testing that all fields are grouped
        missing = set(target.columns) - set(columns)
        assert not missing

    def test_normalizeToAsciiEasy(self):
        target = pyTagger.mp3_snapshot.Formatter()
        title = u'Bj\xf6rk';

        result = target.normalizeToAscii(title)
        
        assert result == 'Bjork', result

    def test_normalizeToAsciiHard(self):
        target = pyTagger.mp3_snapshot.Formatter()
        title = self.buildFormula();

        result = target.normalizeToAscii(title)
        
        assert result == '?p??q?h?4?', result

    def test_extract_basic(self):
        target = pyTagger.Mp3Snapshot()
        formatter = pyTagger.mp3_snapshot.Formatter(pyTagger.mp3_snapshot.Formatter.basic)
        file = os.path.join(self.sourceDirectory, r'The King Of Limbs\05 LotusFlower.MP3')

        row = target.extractTags(file, formatter)
        
        assert row
        assert row['title'] == 'Lotus Flower'
        assert 'fileHash' not in row

    def test_extract_full_v10(self):
        target = pyTagger.Mp3Snapshot()
        formatter = pyTagger.mp3_snapshot.Formatter()
        file = os.path.join(self.sourceDirectory, r'Test Files\ID3V1.MP3')

        row = target.extractTags(file, formatter)
        
        assert row
        assert row['version'] == '1.0.0', row['version']
        assert row['title'] == 'West End Girls', row['title']
        assert row['artist'] == 'Petshop Boys', row['artist']

    def test_extract_full_v22(self):
        target = pyTagger.Mp3Snapshot()
        formatter = pyTagger.mp3_snapshot.Formatter()
        file = os.path.join(self.sourceDirectory, r'Test Files\iTunes 9 256 kbps.MP3')

        row = target.extractTags(file, formatter)
        
        assert row
        assert row['version'] == '2.2.0', row['version']
        assert row['track'] == 1, row['track']
        assert row['title'] == 'Granddad\'s Opening Address', row['title']
        assert row['artist'] == 'Geggy Tah', row['artist']
        assert row['year'] == '1996', row['year']

    def test_extract_full_v23(self):
        target = pyTagger.Mp3Snapshot()
        formatter = pyTagger.mp3_snapshot.Formatter()
        file = os.path.join(self.sourceDirectory, r'01 - Bust A Move.MP3')

        row = target.extractTags(file, formatter)
        
        assert row
        assert row['version'] == '2.3.0', row['version']
        assert row['track'] == 1, row['track']
        assert row['title'] == 'Bust A Move', row['title']
        assert row['artist'] == 'Young MC', row['artist']
        assert row['year'] == '1989', row['year']

    def test_extract_full_v24(self):
        target = pyTagger.Mp3Snapshot()
        formatter = pyTagger.mp3_snapshot.Formatter()
        file = os.path.join(self.sourceDirectory, r'The King Of Limbs\05 LotusFlower.MP3')

        row = target.extractTags(file, formatter)
        
        assert row
        assert row['version'] == '2.4.0', row['version']
        assert row['track'] == 5, row['track']
        assert row['title'] == 'Lotus Flower', row['title']
        assert row['artist'] == 'Radiohead', row['artist']
        assert row['year'] == '2011', row['year']
        assert 'fileHash' in row
        assert row['fileHash']

    def test_extract_badfile(self):
        target = pyTagger.Mp3Snapshot()
        formatter = pyTagger.mp3_snapshot.Formatter(pyTagger.mp3_snapshot.Formatter.basic)
        file = os.path.join(self.sourceDirectory, 'kafafasfaafaf.mp3')

        row = target.extractTags(file, formatter)
        
        assert not row

    def test_extract_utf8(self):
        target = pyTagger.Mp3Snapshot()
        formatter = pyTagger.mp3_snapshot.Formatter(pyTagger.mp3_snapshot.Formatter.basic)
        file = os.path.join(self.sourceDirectory, '08 - Aeroplane.mp3')

        row = target.extractTags(file, formatter)
        
        assert row
        assert row['artist'] == u'Bj\xf6rk'

    def test_extract_non_ascii_filename(self):
        target = pyTagger.Mp3Snapshot()
        formatter = pyTagger.mp3_snapshot.Formatter(pyTagger.mp3_snapshot.Formatter.basic)
        title = self.buildFormula();
        file = os.path.join(self.sourceDirectory, u'10 '+title+u'.MP3')

        row = target.extractTags(file, formatter)
        
        assert row
        assert row['title'] == title
        assert row['artist'] == u'T\xe9l\xe9popmusik'

    def test_calculate_hash(self):
        target = pyTagger.Mp3Snapshot()
        file = os.path.join(self.sourceDirectory, '10 World\'s Famous.mp3')
        track = target._loadID3(file)

        hash = target._calculateHash(track, file)

        assert hash == 'Bf4eOMgTeKkeNxKH345RQHF2GLU=', 'actual:' + hash

if __name__ == '__main__':

    unittest.main()