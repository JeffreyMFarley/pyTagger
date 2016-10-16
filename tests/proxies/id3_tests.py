from __future__ import unicode_literals
import unittest
from tests import *
from collections import namedtuple
from pyTagger.models import Snapshot
from pyTagger.proxies.id3 import ID3Proxy
try:
    from unittest.mock import Mock, patch, mock_open
except ImportError:
    from mock import Mock, patch, mock_open

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


class TestID3Proxy(unittest.TestCase):
    def setUp(self):
        self.target = ID3Proxy()

    def test_allFieldsGrouped(self):
        columns = Snapshot.orderedAllColumns()
        missing = set(self.target.columns) - set(columns)
        assert not missing

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_basic(self):
        self.target = ID3Proxy(Snapshot.basic)
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
        assert row['artist'] == u'Bj\xf6rk'

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_extract_non_ascii_filename(self):
        title = buildFormula()
        fileName = os.path.join(SOURCE_DIRECTORY, u'10 '+title+u'.mp3')

        row = self.target.extractTags(fileName)

        assert row
        assert row['title'] == title
        assert row['artist'] == u'T\xe9l\xe9popmusik'

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_calculate_hash(self):
        fileName = os.path.join(SOURCE_DIRECTORY, '10 World\'s Famous.mp3')
        track = self.target.loadID3(fileName)
        actual = self.target._calculateHash(track, fileName)
        self.assertEqual(actual, 'Bf4eOMgTeKkeNxKH345RQHF2GLU=')

    @patch('pyTagger.proxies.id3.Normalizer')
    def test_calculate_hash_badfile(self, normalizer):
        Track = namedtuple('track', 'tag')
        track = Track(tag=None)
        normalizer.return_value.to_ascii.side_effect = lambda x: x
        self.target = ID3Proxy()

        with patch(coreOpenFn) as mocked_open:
            mocked_open.side_effect = IOError()
            actual = self.target._calculateHash(track, 'foo.mp3')
            self.assertEqual(actual, '')

if __name__ == '__main__':
    unittest.main()
