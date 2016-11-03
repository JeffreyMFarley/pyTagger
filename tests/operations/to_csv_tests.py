from __future__ import unicode_literals
import unittest
import io
import os
import sys
import pyTagger.operations.to_csv as target
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class FakeFile(io.StringIO):
    def __exit__(self, exc_type, exc_value, traceback):
        self.seek(0)


class TestToCsv(unittest.TestCase):

    def setUp(self):
        self.snapshot = {
            'path/one': {
                'id': 'RDoCh4SQKUqntx96G42eLA==',
                'title': 'Little Lion Man',
                'albumArtist': 'Mumford & Sons',
                'artist': 'Mumford & Sons',
                'album': 'Sigh No More',
                'ufid': {
                    'DJTagger': 'RDoCh4SQKUqntx96G42eLA==',
                    'Echonest': 'qr1241aslkfjlqfafa1214'
                },
                'comments': [
                    {
                        'lang': 'eng',
                        'text': 'Amazon.com Song ID: 215022729',
                        'description': ''
                    },
                    {
                        'lang': 'eng',
                        'text': ' 00000BCE 0000370E',
                        'description': 'iTunNORM'
                    }
                ]
            },
            'path/two': {
                'lyrics': [
                    {
                        'lang': 'eng',
                        'text': 'Hey Diddle, Diddle',
                        'description': ''
                    },
                    {
                        'lang': 'fra',
                        'text': 'Oh mais oui',
                        'description': 'verse'
                    }
                ]
            }
        }

    def test_encapsulate_noaction(self):
        field = 'nospaces'
        actual = target._encapsulate(field)
        self.assertEqual(actual, field)

    def test_encapsulate_withspaces(self):
        field = 'I have some spaces'
        expected = field
        actual = target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withquotes(self):
        field = 'I have a "quote"'
        expected = '"I have a ""quote"""'
        actual = target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withcomma(self):
        field = 'We invited the strippers, JFK, and Stalin'
        expected = '"' + field + '"'
        actual = target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withnewline(self):
        for extra in ['\n', '\r', '\r\n']:
            field = extra.join(['a', 'b'])
            expected = '"' + field + '"'
            actual = target._encapsulate(field)
            self.assertEqual(actual, expected)

    def test_encapsulate_withNumeric(self):
        actual = target._encapsulate(123)
        self.assertEqual(actual, '123')

    def test_encapsulate_withUnicode(self):
        field = u'We invited the strippers, JFK, and Stalin'
        expected = u'"' + field + u'"'
        actual = target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withNone(self):
        expected = ''
        actual = target._encapsulate(None)
        self.assertEqual(actual, expected)

    def test_listFlattenedColumns(self):
        actual = target.listFlattenedColumns(self.snapshot)
        self.assertEqual(actual, [
            'title', 'artist', 'albumArtist', 'album', 'id',
            'comments\u2027eng\u2027',  'comments\u2027eng\u2027iTunNORM',
            'lyrics\u2027eng\u2027', 'lyrics\u2027fra\u2027verse',
            'ufid\u2027DJTagger', 'ufid\u2027Echonest'
        ])

    def test_writeCsv(self):
        output = FakeFile()
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = output
            target.writeCsv(self.snapshot, 'foo.txt')

        for i, r in enumerate(output):
            cells = r.split('\t')
            self.assertEqual(len(cells), 12)
            if i == 1:
                self.assertEqual(cells[5], 'Amazon.com Song ID: 215022729')
            elif i == 2:
                self.assertEqual(cells[8], 'Oh mais oui')

        output.close()

if __name__ == '__main__':
    unittest.main()
