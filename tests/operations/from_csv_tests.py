from __future__ import unicode_literals
import unittest
import io
import pyTagger.operations.from_csv as sut
from nose_parameterized import parameterized
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestParseStateMachine(unittest.TestCase):
    def setUp(self):
        self.target = sut.Context()

    @parameterized.expand([
        ('nospaces', 'nospaces'),
        ('I have some spaces', 'I have some spaces'),
        ('"I have a ""quote"""', 'I have a "quote"'),
        ('"""I"" have a quote"', '"I" have a quote'),
        ('"We invited the strippers, JFK, and Stalin"',
            'We invited the strippers, JFK, and Stalin'),
        ('"a\nb"', 'a\nb'),
        ('"a\rb"', 'a\rb'),
        ('"a\r\nb"', 'a\r\nb'),
        ('"""\n"""', '"\n"')
    ])
    def test_parse_cell(self, s, expected):
        instream = io.StringIO('\ufeff' + s + '\n')
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = instream
            actual = list(self.target.parse('foo'))
        self.assertEqual(actual, [[expected]])

    @parameterized.expand([
        ('a\tb', True, ['a', 'b']),
        ('a,b', False, ['a', 'b']),
        ('a,b', True, ['a,b']),
        ('a\tb', False, ['a\tb']),
        ('"a,b,c"\td', True, ['a,b,c', 'd']),
        ('"a,b,c",d', False, ['a,b,c', 'd']),
        ('"a,""b"",c"\td', True, ['a,"b",c', 'd']),
        ('"a,""b"",c",d', False, ['a,"b",c', 'd'])
    ])
    def test_parse_row(self, s, excelFormat, expected):
        instream = io.StringIO('\ufeff' + s + '\n')
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = instream
            actual = list(self.target.parse('foo', excelFormat))
        self.assertEqual(actual, [expected])

    @parameterized.expand([
        ('\r\n\r\n', [[''], [''], ['']])
    ])
    def test_parse_whole(self, s, expected):
        instream = io.StringIO('\ufeff' + s + '\n')
        with patch.object(io, 'open') as fmocked:
            fmocked.return_value = instream
            actual = list(self.target.parse('foo'))
        self.assertEqual(actual, expected)


class TestFromCsv(unittest.TestCase):
    def setUp(self):
        self.csv = [
            ['id', 'title', 'track', 'vbr',
             'comments\u2027eng\u2027', 'comments\u2027eng\u2027iTunNORM',
             'lyrics\u2027eng\u2027', 'lyrics\u2027fra\u2027verse',
             'ufid\u2027DJTagger', 'ufid\u2027Echonest', 'fullPath'],
            ['12234', 'foo', '2', 'False', 'Backcatalog', '000 111 AAA',
             '', '', 'RDoCh4SQKUqntx96G42eLA==', '', 'path/one'],
            ['34567', 'bar', '99', 'True', '', '', 'Tra\nLa\nLa',
             'Ooo\nLa\nLa', '', 'qr1241aslkfjlqfafa1214', 'path/two']
        ]

    @parameterized.expand([
        ('foo', 'title', 'foo'),
        ('foo', 'bar', 'foo'),
        ('128', 'bitRate', 128),
        ('128', 'bpm', 128),
        ('1', 'disc', 1),
        ('01', 'disc', 1),
        ('345', 'length', 345),
        ('2', 'totalDisc', 2),
        ('100', 'totalTrack', 100),
        ('98', 'track', 98),
        ('False', 'vbr', False),
        ('True', 'vbr', True)
    ])
    def test_transform(self, s, column, expected):
        actual = sut._transform(s, column)
        self.assertEqual(actual, expected)

    @parameterized.expand([
        ('title', 'A little night music', ('title', 'A little night music')),
        ('foo', 'bar', ('foo', 'bar')),
        ('comments\u2027eng\u2027', 'Backcatalog', (
            'comments', {
                'lang': 'eng',
                'text': 'Backcatalog',
                'description': ''
            }
        )),
        ('comments\u2027eng\u2027iTunNORM', '0000 1111 AAAA 2222', (
            'comments', {
                'lang': 'eng',
                'text': '0000 1111 AAAA 2222',
                'description': 'iTunNORM'
            }
        )),
        ('lyrics\u2027eng\u2027', 'Tra\nla\nla', (
            'lyrics', {
                'lang': 'eng',
                'text': 'Tra\nla\nla',
                'description': ''
            }
        )),
        ('lyrics\u2027fra\u2027verse', 'Ooo\nla\nla', (
            'lyrics', {
                'lang': 'fra',
                'text': 'Ooo\nla\nla',
                'description': 'verse'
            }
        )),
        ('ufid\u2027DJTagger', 'RDoCh4SQKUqntx96G42eLA==', (
            'ufid', {
                'DJTagger': 'RDoCh4SQKUqntx96G42eLA=='
            }
        )),
        ('an\u2027unknown\u2027split', 'foo', (None, None)),
        ('fullPath', '/path/to/bar', (None, None)),
        ('comments\u2027eng\u2027', '', (None, None)),
        ('lyrics\u2027eng\u2027', '', (None, None)),
        ('ufid\u2027DJTagger', '', (None, None)),
    ])
    def test_expand(self, column, cell, expected):
        actual = sut._expand(cell, column)
        self.assertEqual(actual, expected)

    def test_handleRow_0(self):
        k, v = sut._handleRow(self.csv[1], self.csv[0])
        self.assertEqual(k, 'path/one')
        self.assertEqual(v['id'], '12234')
        self.assertEqual(v['track'], 2)
        self.assertEqual(v['vbr'], False)
        self.assertEqual(len(v['comments']), 2)
        self.assertEqual(v['comments'][0]['text'], 'Backcatalog')
        self.assertEqual(v['comments'][1]['text'], '000 111 AAA')
        self.assertEqual(len(v['lyrics']), 0)
        self.assertEqual(len(v['ufid']), 1)
        self.assertEqual(v['ufid']['DJTagger'], 'RDoCh4SQKUqntx96G42eLA==')

    def test_handleRow_1(self):
        k, v = sut._handleRow(self.csv[2], self.csv[0])
        self.assertEqual(k, 'path/two')
        self.assertEqual(v['id'], '34567')
        self.assertEqual(v['track'], 99)
        self.assertEqual(v['vbr'], True)
        self.assertEqual(len(v['comments']), 0)
        self.assertEqual(len(v['lyrics']), 2)
        self.assertEqual(v['lyrics'][0]['text'], 'Tra\nLa\nLa')
        self.assertEqual(v['lyrics'][1]['text'], 'Ooo\nLa\nLa')
        self.assertEqual(len(v['ufid']), 1)
        self.assertEqual(v['ufid']['Echonest'], 'qr1241aslkfjlqfafa1214')

    @parameterized.expand([
        (None, {'a': 'b', 'c': 'd'}),
        ([], {'a': 'b', 'c': 'd'}),
        (['a'], {'a': 'b'}),
        (['b'], {}),
        (['a', 'b'], {'a': 'b'}),
        (['c'], {'c': 'd'}),
        (['a', 'b', 'c'], {'a': 'b', 'c': 'd'})
    ])
    def test_projection(self, columns, expected):
        fields = {'a': 'b', 'c': 'd'}
        actual = sut._projection(fields, columns)
        self.assertEqual(actual, expected)

    @patch('pyTagger.operations.from_csv.saveJsonIncrementalDict')
    @patch('pyTagger.operations.from_csv.Context')
    def test_convert(self, context, saveJson):
        def mock_parse(inFileName, excelFormat):
            self.assertEqual(inFileName, 'foo')
            self.assertEqual(excelFormat, True)
            for r in self.csv:
                yield r
        context_instance = Mock()
        context_instance.parse.side_effect = mock_parse
        context.return_value = context_instance

        def noop_coroutine(outfile, compact):
            self.assertEqual(outfile, 'bar')
            self.assertEqual(compact, True)
            for i in [0, 1, 2, 3, 4]:
                k, v = yield i
                if i == 0:
                    self.assertEqual(k, 'path/one')
                    self.assertEqual(v['id'], '12234')
                    self.assertNotIn('title', v)
                elif i == 1:
                    self.assertEqual(k, 'path/two')
                    self.assertEqual(v['id'], '34567')
                    self.assertNotIn('title', v)
        saveJson.side_effect = noop_coroutine

        actual = sut.convert('foo', 'bar', ['id'])
        self.assertEqual(actual, (2, 0))

if __name__ == '__main__':
    unittest.main()
