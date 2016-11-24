from __future__ import unicode_literals
import unittest
import os
import shutil
import sys
import pyTagger.operations.on_mp3 as target
from pyTagger.proxies.id3 import ID3Proxy
from tests import *

IMAGES_DIRECTORY = os.path.join(RESULT_DIRECTORY, r'images')


def setUpModule():
    if sampleFilesExist and os.path.exists(IMAGES_DIRECTORY):
        shutil.rmtree(IMAGES_DIRECTORY)
    os.makedirs(IMAGES_DIRECTORY)


class TestExtractImages(unittest.TestCase):

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def setUp(self):
        self.id3Proxy = ID3Proxy()

    def test_single_extract(self):
        fileName = os.path.join(SOURCE_DIRECTORY, '01 - Bust A Move.mp3')
        expected = os.path.join(
            IMAGES_DIRECTORY, 'Young MC - single - Bust A Move.jpeg'
        )

        table = {}
        target.extractImages(self.id3Proxy, table, IMAGES_DIRECTORY, fileName)

        self.assertTrue(os.path.exists(expected), expected)
        self.assertEqual(table, {'dlKEdYk/nLyR9w47+hudLgsVfSw=': expected})

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
        target.extractImages(self.id3Proxy, table, IMAGES_DIRECTORY, file1)
        target.extractImages(self.id3Proxy, table, IMAGES_DIRECTORY, file2)

        assert os.path.exists(expected)
        assert not os.path.exists(not_expected)
        self.assertEqual(table, {'FdEykG2M5cdsTTwfeZP7JB6V8pQ=': expected})

if __name__ == '__main__':
    unittest.main()
