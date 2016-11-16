from __future__ import unicode_literals
import unittest
import uuid
import pyTagger.operations.two_tags as target


class TestDifference(unittest.TestCase):
    def test_a_greaterThan_b(self):
        a = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {'album': 'ghi'}
        expected = {'title': 'abc',  'artist': 'def'}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lessThan_b(self):
        a = {'album': 'ghi'}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_isNull(self):
        a = {}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_isNull(self):
        a = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {}
        expected = a

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleEqual_b(self):
        a = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleNotEqual_b(self):
        a = {'title': 'cde',  'artist': 'def', 'album': 'ghi'}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {'title': 'cde'}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_simpleIsNull(self):
        a = {'title': '',  'artist': 'def', 'album': 'ghi'}
        b = {'title': 'abc',  'artist': 'def', 'album': 'ghi'}
        expected = {'title': None}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_simpleIsNull(self):
        a = {'title': 'cde',  'artist': 'def', 'album': 'ghi'}
        b = {'title': '',  'artist': 'def', 'album': 'ghi'}
        expected = {'title': 'cde'}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentsGreaterThan_b(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        expected = {'comments': [
            {'lang': 'esp', 'text': 'hola', 'description': ''},
            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
        ]}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_commentsGreaterThan_a(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentEqual_b(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentNotEqual_b(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bon', 'description': ''}
                          ]}
        expected = {'comments': [{
            'lang': 'fra', 'text': 'bonjour', 'description': ''
        }]}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_commentIsNull(self):
        a = {'comments': []}
        b = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bon', 'description': ''}
                          ]}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_commentIsNull(self):
        a = {'comments': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                          {'lang': 'esp', 'text': 'hola', 'description': ''},
                          {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                          ]}
        b = {'comments': []}
        expected = a

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricsGreaterThan_b(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        expected = {'lyrics': [
            {'lang': 'esp', 'text': 'hola', 'description': ''},
            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
        ]}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_lyricsGreaterThan_a(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''}]}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricEqual_b(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricNotEqual_b(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bon', 'description': ''}
                        ]}
        expected = {'lyrics': [
            {'lang': 'fra', 'text': 'bonjour', 'description': ''}
        ]}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_lyricIsNull(self):
        a = {'lyrics': []}
        b = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bon', 'description': ''}
                        ]}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_lyricIsNull(self):
        a = {'lyrics': [{'lang': 'eng', 'text': 'hello', 'description': ''},
                        {'lang': 'esp', 'text': 'hola', 'description': ''},
                        {'lang': 'fra', 'text': 'bonjour', 'description': ''}
                        ]}
        b = {'lyrics': []}
        expected = a

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idsGreaterThan_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = {'ufid': {'def': id2.bytes}}
        expected = {'ufid': {'abc': id1.bytes, 'ghi': id3.bytes}}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_idsGreaterThan_a(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {'def': id2.bytes}}
        b = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idEqual_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idNotEqual_b(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        id4 = uuid.uuid1()
        a = {'ufid': {'abc': id4.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {'ufid': {'abc': id4.bytes}}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_a_idIsNull(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {}}
        b = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        expected = {}

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_b_idIsNull(self):
        id1 = uuid.uuid1()
        id2 = uuid.uuid1()
        id3 = uuid.uuid1()
        a = {'ufid': {'abc': id1.bytes, 'def': id2.bytes, 'ghi': id3.bytes}}
        b = {'ufid': {}}
        expected = a

        actual = target.difference(a, b)

        self.assertDictEqual(expected, actual, repr(actual))

    def test_empty_comments_not_added(self):
        a = [{'lang': 'eng', 'text': '', 'description': ''},
             {'lang': 'esp', 'text': '', 'description': ''},
             {'lang': 'fra', 'text': '', 'description': ''}]
        b = [{'lang': 'deu', 'text': 'guten tag', 'description': ''}]
        expected = []

        actual = target._differenceDLT(a, b)

        self.assertListEqual(expected, actual, repr(actual))


class TestTwoTags(unittest.TestCase):
    def setUp(self):
        self.snapshot = {'foo': 'bar'}
        self.keys = ['title', 'album', 'artist', 'track', 'id']
        self.mp3Info = ['bitRate', 'vbr', 'fileHash', 'version']

    def test_union_notOlder_clones(self):
        a = {'title': 'hey'}

        actual = target.union(a, {})

        self.assertEqual(actual['title'], a['title'])
        a['title'] = 'bar'
        self.assertNotEqual(actual['title'], a['title'])

    def test_union_notOlder_hasMp3Info(self):
        a = {k: 'foo' for k in ['title'] + self.mp3Info}

        actual = target.union(a, {})

        for k in ['title']:
            self.assertTrue(k in actual)
        for k in self.mp3Info:
            self.assertFalse(k in actual)

    def test_union_allCommonKeys(self):
        a = {k: 'bar' for k in self.keys}
        b = {k: 'foo' for k in self.keys}

        actual = target.union(a, b)

        self.assertEqual(len(actual), len(self.keys))
        for k in self.keys:
            self.assertEqual(actual[k], b[k])

    def test_union_allCommonKeys_olderIsNull(self):
        a = {k: 'bar' for k in self.keys}
        b = {k: '' for k in self.keys}

        actual = target.union(a, b)

        self.assertEqual(len(actual), len(self.keys))
        for k in self.keys:
            self.assertEqual(actual[k], a[k])

    def test_union_noCommonKeys(self):
        a = {k: 'baz' for k in ['title', 'album', 'artist']}
        b = {k: 'baz' for k in ['track', 'id']}

        actual = target.union(a, b)

        self.assertEqual(len(actual), len(self.keys))
        for k in self.keys:
            self.assertEqual(actual[k], 'baz')

    def test_union_clones(self):
        a = {k: 'bar' for k in self.keys}
        b = {k: 'foo' for k in self.keys}

        actual = target.union(a, b)

        for k in self.keys:
            a[k] = 'qaz'
            b[k] = 'baz'
            self.assertEqual(actual[k], 'foo')

    def test_union_hasMp3Info(self):
        a = {k: 'bar' for k in self.keys}
        b = {k: 'foo' for k in self.mp3Info}

        actual = target.union(a, b)

        self.assertEqual(len(actual), len(self.keys))
        for k in self.mp3Info:
            self.assertFalse(k in actual)

if __name__ == '__main__':
    unittest.main()
