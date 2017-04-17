from __future__ import unicode_literals
import unittest
import collections
import os
import shutil
import sys
import pyTagger.operations.on_mp3 as target
from pyTagger.proxies.id3 import ID3Proxy
from tests import *
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

IMAGES_DIRECTORY = os.path.join(RESULT_DIRECTORY, r'images')


@unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
def setUpModule():
    if sampleFilesExist and os.path.exists(IMAGES_DIRECTORY):
        shutil.rmtree(IMAGES_DIRECTORY)
    os.makedirs(IMAGES_DIRECTORY)


class TestOnMp3s(unittest.TestCase):

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def setUp(self):
        self.id3Proxy = ID3Proxy()

    def test_single_extract(self):
        fileName = os.path.join(SOURCE_DIRECTORY, '01 - Bust A Move.mp3')
        expected = os.path.join(
            IMAGES_DIRECTORY, 'Young MC - single - Bust A Move.jpeg'
        )

        table = {}
        processed = target.extractImages(
            self.id3Proxy, table, IMAGES_DIRECTORY, fileName
        )

        self.assertTrue(os.path.exists(expected), expected)
        self.assertEqual(table, {'dlKEdYk/nLyR9w47+hudLgsVfSw=': expected})
        self.assertEqual(processed['extracted'], 1)
        self.assertEqual(processed['skipped'], 0)
        self.assertEqual(processed['errors'], 0)

    def test_multiple_on_same_album_extract(self):
        file1 = os.path.join(
            SOURCE_DIRECTORY, 'The King Of Limbs', '01 Bloom.MP3'
        )
        file2 = os.path.join(
            SOURCE_DIRECTORY, 'The King Of Limbs', '02 MorningMrMagpie.MP3'
        )
        expected = os.path.join(
            IMAGES_DIRECTORY, 'Radiohead - The King Of Limbs - Bloom.jpeg'
        )
        not_expected = os.path.join(
            IMAGES_DIRECTORY, 'Radiohead - The King Of Limbs - ' +
            'Morning Mr Magpie.jpeg'
        )

        table = {}
        processed = target.extractImages(
            self.id3Proxy, table, IMAGES_DIRECTORY, file1
        )
        processed += target.extractImages(
            self.id3Proxy, table, IMAGES_DIRECTORY, file2
        )

        assert os.path.exists(expected)
        assert not os.path.exists(not_expected)
        self.assertEqual(table, {'FdEykG2M5cdsTTwfeZP7JB6V8pQ=': expected})
        self.assertEqual(processed['extracted'], 1)
        self.assertEqual(processed['skipped'], 1)
        self.assertEqual(processed['errors'], 0)

    @patch('pyTagger.proxies.id3.ID3Proxy')
    def test_updateOne_fails(self, proxy):
        Track = collections.namedtuple('Track', 'tag')
        track = Track({'album': 'foo'})

        instance = proxy.return_value
        instance.loadID3.return_value = track
        instance.extractTagsFromTrack.side_effect = IOError

        actual = target.updateOne(instance, 'foo.mp3', {})
        self.assertEqual(actual, 0)

if __name__ == '__main__':
    unittest.main()
