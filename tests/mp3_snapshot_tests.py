# -*- coding: utf-8 -*

import unittest
import os
import sys
from tests import *
from collections import namedtuple
try:
    from unittest.mock import Mock, patch, mock_open
except ImportError:
    from mock import Mock, patch, mock_open
from pyTagger.mp3_snapshot import Formatter, Mp3Snapshot


if sys.version < '3':
    coreOpenFn = '__builtin__.open'
else:
    coreOpenFn = 'builtins.open'


def buildFormula():
    greek_lower_d = u'\u03b4'
    dot_multiply = u'\u00b7'
    greater_than_or_equal = u'\u2265'
    divide = u'\u2044'
    pi = u'\u03c0'
    title = u''.join([
        greek_lower_d, 'p', dot_multiply, greek_lower_d, 'q',
        greater_than_or_equal, 'h', divide, '4', pi
    ])
    return title


class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.target = Formatter()

    def test_allFieldsGrouped(self):
        columns = self.target.orderedAllColumns()
        missing = set(self.target.columns) - set(columns)
        assert not missing

    def test_normalizeToAsciiEasy(self):
        title = u'Bj\xf6rk'
        result = self.target.normalizeToAscii(title)
        assert result == 'Bjork', result

    def test_normalizeToAsciiHard(self):
        title = buildFormula()
        result = self.target.normalizeToAscii(title)
        assert result == '?p??q?h?4?', result


class TestMp3Snapshot(unittest.TestCase):

    def setUp(self):
        self.target = Mp3Snapshot()

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_basic(self):
        formatter = Formatter(Formatter.basic)
        file = os.path.join(
            SOURCE_DIRECTORY, 'The King Of Limbs', '05 LotusFlower.MP3'
        )

        row = self.target.extractTags(file, formatter)

        assert row
        assert row['title'] == 'Lotus Flower'
        assert 'fileHash' not in row

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_full_v10(self):
        formatter = Formatter()
        file = os.path.join(SOURCE_DIRECTORY, 'Test Files', 'ID3V1.mp3')

        row = self.target.extractTags(file, formatter)

        assert row
        assert row['version'] == '1.0.0', row['version']
        assert row['title'] == 'West End Girls', row['title']
        assert row['artist'] == 'Petshop Boys', row['artist']

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_full_v22(self):
        formatter = Formatter()
        file = os.path.join(
            SOURCE_DIRECTORY, 'Test Files', 'iTunes 9 256 kbps.mp3'
        )

        row = self.target.extractTags(file, formatter)

        assert row
        assert row['version'] == '2.2.0', row['version']
        assert row['track'] == 1, row['track']
        assert row['title'] == 'Granddad\'s Opening Address', row['title']
        assert row['artist'] == 'Geggy Tah', row['artist']
        assert row['year'] == '1996', row['year']

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_full_v23(self):
        formatter = Formatter()
        file = os.path.join(SOURCE_DIRECTORY, '01 - Bust A Move.mp3')

        row = self.target.extractTags(file, formatter)

        assert row
        assert row['version'] == '2.3.0', row['version']
        assert row['track'] == 1, row['track']
        assert row['title'] == 'Bust A Move', row['title']
        assert row['artist'] == 'Young MC', row['artist']
        assert row['year'] == '1989', row['year']

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_full_v24(self):
        formatter = Formatter()
        file = os.path.join(
            SOURCE_DIRECTORY, 'The King Of Limbs', '05 LotusFlower.MP3'
        )

        row = self.target.extractTags(file, formatter)

        assert row
        assert row['version'] == '2.4.0', row['version']
        assert row['track'] == 5, row['track']
        assert row['title'] == 'Lotus Flower', row['title']
        assert row['artist'] == 'Radiohead', row['artist']
        assert row['year'] == '2011', row['year']
        assert 'fileHash' in row
        assert row['fileHash']

    def test_extract_badfile(self):
        formatter = Formatter(Formatter.basic)
        file = os.path.join(SOURCE_DIRECTORY, 'kafafasfaafaf.mp3')

        row = self.target.extractTags(file, formatter)

        assert not row

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_utf8(self):
        formatter = Formatter(Formatter.basic)
        file = os.path.join(SOURCE_DIRECTORY, '08 - Aeroplane.mp3')

        row = self.target.extractTags(file, formatter)

        assert row
        assert row['artist'] == u'Bj\xf6rk'

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_non_ascii_filename(self):
        formatter = Formatter(Formatter.basic)
        title = buildFormula()
        file = os.path.join(SOURCE_DIRECTORY, u'10 '+title+u'.mp3')

        row = self.target.extractTags(file, formatter)

        assert row
        assert row['title'] == title
        assert row['artist'] == u'T\xe9l\xe9popmusik'

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_calculate_hash(self):
        file = os.path.join(SOURCE_DIRECTORY, '10 World\'s Famous.mp3')
        track = self.target._loadID3(file)

        hash = self.target._calculateHash(track, file)

        assert hash == 'Bf4eOMgTeKkeNxKH345RQHF2GLU=', 'actual:' + hash

    @patch(coreOpenFn)
    @patch('pyTagger.mp3_snapshot.eyed3.mp3.Mp3AudioFile')
    def test_calculate_hash_badfile(self, track, mocked_open):
        mocked_open.side_effect = IOError()
        actual = self.target._calculateHash(track, 'foo.mp3')
        self.assertEqual(actual, '')

if __name__ == '__main__':
    unittest.main()
