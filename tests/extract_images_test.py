import unittest
import os
import sys
import pyTagger
from tests import *

IMAGES_DIRECTORY = os.path.join(RESULT_DIRECTORY, r'images')


class TestExtractImages(unittest.TestCase):

    def setUp(self):
        assert sys.version < '3', 'This test must be run in Python 2.x'
        self.target = pyTagger.ExtractImages(IMAGES_DIRECTORY)

    def test_single_extract(self):
        file = os.path.join(SOURCE_DIRECTORY, '08 - Aeroplane.mp3')
        expected = os.path.join(IMAGES_DIRECTORY, 'Debut - Aeroplane.jpeg')
        
        self.target._extract(file)
        
        assert os.path.exists(expected)

    def test_multiple_on_same_album_extract(self):
        file1 = os.path.join(SOURCE_DIRECTORY, 'The King Of Limbs', '01 Bloom.mp3')
        file2 = os.path.join(SOURCE_DIRECTORY, 'The King Of Limbs', '02 MorningMrMagpie.mp3')
        expected = os.path.join(IMAGES_DIRECTORY, 'The King Of Limbs - Bloom.jpeg')
        not_expected = os.path.join(IMAGES_DIRECTORY, 'The King Of Limbs - Morning Mr Magpie.jpeg')
        
        self.target._extract(file1)
        self.target._extract(file2)
        
        assert os.path.exists(expected)
        assert not os.path.exists(not_expected)

if __name__ == '__main__':

    unittest.main()