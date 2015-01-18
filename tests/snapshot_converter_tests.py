# -*- coding: utf-8 -*

import unittest
import os
import sys
import pyTagger

class TestSnapshotConverter(unittest.TestCase):

    def setUp(self):
        self.sourceDirectory = r'C:\dvp\MP3Tools\SampleData'
        self.resultDirectory = r'C:\dvp\MP3Tools\TestOutput'
        if not os.path.exists(self.resultDirectory):
            os.makedirs(self.resultDirectory)

    def tearDown(self):
        pass

    def test_encapsulate_noaction(self):
        target = pyTagger.SnapshotConverter()
        field = 'nospaces'

        actual = target._encapsulate(field)

        assert actual == field, actual

    def test_encapsulate_withspaces(self):
        target = pyTagger.SnapshotConverter()
        field = 'I have some spaces'
        expected = field

        actual = target._encapsulate(field)

        assert actual == expected, actual

    def test_encapsulate_withquotes(self):
        target = pyTagger.SnapshotConverter()
        field = 'I have a "quote"'
        expected = '"I have a ""quote"""'

        actual = target._encapsulate(field)

        assert actual == expected, actual

    def test_encapsulate_withcomma(self):
        target = pyTagger.SnapshotConverter()
        field = 'We invited the strippers, JFK, and Stalin'
        expected = '"' + field + '"'

        actual = target._encapsulate(field)

        assert actual == expected, actual

    def test_encapsulate_withnewline(self):
        target = pyTagger.SnapshotConverter()
        for extra in ['\n', '\r', '\r\n']:
            field = extra.join(['a', 'b'])
            expected = '"' + field + '"'

            actual = target._encapsulate(field)

        assert actual == expected, actual

    def test_encapsulate_withNumeric(self):
        target = pyTagger.SnapshotConverter()
        actual = target._encapsulate(123)

        assert actual == '123', actual

    def test_encapsulate_withUnicode(self):
        target = pyTagger.SnapshotConverter()
        field = u'We invited the strippers, JFK, and Stalin'
        expected = u'"' + field + u'"'

        actual = target._encapsulate(field)

        assert actual == expected, actual

    def test_encapsulate_withNone(self):
        target = pyTagger.SnapshotConverter()
        expected = ''

        actual = target._encapsulate(None)

        assert actual == expected, actual

    def test_encapsulate_withSimpleList(self):
        target = pyTagger.SnapshotConverter()
        field = ['a', 'b', 'c']
        expected = '"'+ '\n'.join(field) + '"'

        actual = target._encapsulate(field)

        assert actual == expected, repr(actual)

    def test_encapsulate_withSimpleDictionary(self):
        target = pyTagger.SnapshotConverter()
        field = {'a' : 'b', 'c': 'd'}
        expected = '"a : b, c : d"'

        actual = target._encapsulate(field)

        assert actual == expected, repr(actual)

    def test_encapsulate_withComplexList(self):
        target = pyTagger.SnapshotConverter()
        field = [{'a' : 'b', 'c' : 'd'},{'e' : 'f', 'g' : 'h'}]
        expected = '"a : b, c : d\ne : f, g : h"'

        actual = target._encapsulate(field)

        assert actual == expected, repr(actual)

if __name__ == '__main__':

    unittest.main()