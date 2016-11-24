import unittest
import os
import sys
from pyTagger.extract_images import ExtractImages
from tests import *

IMAGES_DIRECTORY = os.path.join(RESULT_DIRECTORY, r'images')


class TestExtractImages(unittest.TestCase):

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def setUp(self):
        self.target = ExtractImages(IMAGES_DIRECTORY)

    def test_single_extract(self):
        file = os.path.join(SOURCE_DIRECTORY, '08 - Aeroplane.mp3')
        expected = os.path.join(IMAGES_DIRECTORY, 'Debut - Aeroplane.jpeg')

        self.target._extract(self.target.id3Proxy, file)

        assert os.path.exists(expected)

    def test_multiple_on_same_album_extract(self):
        file1 = os.path.join(
            SOURCE_DIRECTORY, 'The King Of Limbs', '01 Bloom.MP3'
        )
        file2 = os.path.join(
            SOURCE_DIRECTORY, 'The King Of Limbs', '02 MorningMrMagpie.MP3'
        )
        expected = os.path.join(
            IMAGES_DIRECTORY, 'The King Of Limbs - Bloom.jpeg'
        )
        not_expected = os.path.join(
            IMAGES_DIRECTORY, 'The King Of Limbs - Morning Mr Magpie.jpeg'
        )

        self.target._extract(self.target.id3Proxy, file1)
        self.target._extract(self.target.id3Proxy, file2)

        assert os.path.exists(expected)
        assert not os.path.exists(not_expected)

if __name__ == '__main__':
    unittest.main()
