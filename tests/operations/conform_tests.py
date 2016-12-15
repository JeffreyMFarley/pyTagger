import unittest
import os
import shutil
import datetime
from nose_parameterized import parameterized
from tests import *
from pyTagger.operations.conform import LibraryStandard
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestConform(unittest.TestCase):
    def setUp(self):
        self.target = LibraryStandard()
        self.tags = {}

    @patch('pyTagger.operations.conform.generateUfid')
    def test_assignID_no_id(self, generateUfid):
        generateUfid.return_value = 'foo'
        actual = self.target.assignID(self.tags)
        self.assertEqual(actual, {'ufid': {'DJTagger': 'foo'}})
        self.assertEqual(actual, self.tags)

    @patch('pyTagger.operations.conform.generateUfid')
    def test_assignID_id_exists(self, generateUfid):
        generateUfid.return_value = 'foo'
        self.tags['ufid'] = {'bar': 'baz'}
        actual = self.target.assignID(self.tags)
        self.assertEqual(actual, {'ufid': {
            'DJTagger': 'foo',
            'bar': 'baz'
        }})
        self.assertEqual(actual, self.tags)

    def test_clearComments(self):
        actual = self.target.clearComments(self.tags)
        self.assertEqual(actual, {'comments': [
            {'lang': 'eng', 'text': '', 'description': ''},
            {'lang': '', 'text': '', 'description': ''}
        ]})
        self.assertEqual(actual, self.tags)

    def test_clearMedia(self):
        actual = self.target.clearMedia(self.tags)
        self.assertEqual(actual, {'media': ''})
        self.assertEqual(actual, self.tags)

    def test_clearRating(self):
        actual = self.target.clearRating(self.tags)
        self.assertEqual(actual, {'group': ''})
        self.assertEqual(actual, self.tags)

    def test_digitalMedia(self):
        actual = self.target.digitalMedia(self.tags)
        self.assertEqual(actual, {'media': 'DIG'})
        self.assertEqual(actual, self.tags)

    @parameterized.expand([
        (
            'The Sideshow (feat. Ernie Fresh)', 'DJ Shadow',
            'The Sideshow', 'DJ Shadow/Ernie Fresh'
        ),
        (
            'Shake Ya Tail Feather', 'Nelly',
            'Shake Ya Tail Feather', 'Nelly'
        ),
        (
            'All We Need Is Love (Christmas in the Yard) (feat. Shaggy)',
            'The Big Yard Family',
            'All We Need Is Love (Christmas in the Yard)',
            'The Big Yard Family/Shaggy',
        ),
        (
            'Pitter Patter (feat. G Jones & Bleep Bloop)', 'DJ Shadow',
            'Pitter Patter', 'DJ Shadow/G Jones/Bleep Bloop',
        ),
        (
            "Ghosts 'n' Stuff (Feat. Rob Swire)", 'deadmau5',
            "Ghosts 'n' Stuff", 'deadmau5/Rob Swire',
        ),
        (
            'Pursuit Of Happiness [Explicit] (Steve Aoki Remix Feat. MGMT)',
            'Kid Cudi',
            'Pursuit Of Happiness [Explicit] (Steve Aoki Remix Feat. MGMT)',
            'Kid Cudi'
        ),
        (
            'Sleeping With Byron (Hotbox remix featuring Byron Stingily)',
            'Lo Fidelity Allstars',
            'Sleeping With Byron (Hotbox remix featuring Byron Stingily)',
            'Lo Fidelity Allstars'
        ),
        (
            "There's A Truth Feat Stee Downes", "Motor City Drum Ensemble",
            "There's A Truth Feat Stee Downes", "Motor City Drum Ensemble"
        ),
        (
            "Omen [feat. Sam Smith]", "Disclosure",
            "Omen", "Disclosure/Sam Smith"
        ),
        (
            'Where Are U Now (with Justin Bieber)', 'Skrillex & Diplo',
            'Where Are U Now', 'Skrillex & Diplo/Justin Bieber',
        ),
        (None, None, None, None)
    ])
    def test_extractArtist(self, t0, a0, t1, a1):
        self.tags['title'] = t0
        self.tags['artist'] = a0
        expected = {'title': t1, 'artist': a1}
        actual = self.target.extractArtist(self.tags)
        self.assertEqual(actual, expected)
        self.assertEqual(actual, self.tags)

    @parameterized.expand([
        (None, None),
        ('Nothing is Wrong', 'Nothing is Wrong'),
        (
            'Everything Counts [In Larger Amounts]',
            'Everything Counts [In Larger Amounts]'
        ),
        ('Dreams [Explicit]', 'Dreams'),
        ('Foo (Explicit Version)', 'Foo'),
        ('Foo (Explicit)', 'Foo'),
        ('Foo [Explicit Content]', 'Foo'),
        ('Foo (US Version)', 'Foo'),
        ('Foo [US Release]', 'Foo'),
        ('Foo (Album Version)', 'Foo'),
        ('Foo (LP Version)', 'Foo'),
        ('Foo (Deluxe)', 'Foo'),
        ('Foo [Deluxe Edition]', 'Foo'),
        ('Foo (Deluxe Version)', 'Foo'),
        ('Foo [Amazon MP3 Exclusive Version]', 'Foo'),
        ('Foo (Amazon MP3 Exclusive - Deluxe Version)', 'Foo'),
        ('Foo (Original Motion Picture Soundtrack)', 'Foo'),
        ('Foo (Special Edition)', 'Foo'),
        ('Foo (Remastered)', 'Foo')
    ])
    def test_removeAnnotations(self, before, after):
        self.tags['title'] = before
        expected = {'title': after}
        actual = self.target.removeAnnotations(self.tags)
        self.assertEqual(actual, expected)
        self.assertEqual(actual, self.tags)

    def test_timestamp(self):
        expected = datetime.date.today().isoformat()
        actual = self.target.timestamp(self.tags)
        self.assertEqual(actual, {'subtitle': expected})
        self.assertEqual(actual, self.tags)

    @patch('pyTagger.operations.conform.updateOne')
    @patch('pyTagger.operations.conform.fmap')
    def test_processFile(self, fmap, updateOne):
        self.target.reader = Mock(spec=['extractTags'])
        self.target.reader.extractTags.return_value = {}
        expected = [
            self.target.extractArtist,
            self.target.removeAnnotations,
            self.target.timestamp,
            self.target.assignID,
            self.target.digitalMedia,
            self.target.clearComments,
            self.target.clearRating
        ]

        self.target.processFile('/path/to/yasss')

        fmap.assert_called_with(expected, {})
        self.assertEqual(updateOne.call_count, 1)

if __name__ == '__main__':
    unittest.main()
