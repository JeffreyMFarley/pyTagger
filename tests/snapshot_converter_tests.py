# -*- coding: utf-8 -*

import unittest
import os
import sys
import pyTagger
from tests import *


class TestSnapshotConverter(unittest.TestCase):

    def setUp(self):
        self.target = pyTagger.SnapshotConverter()

    def test_encapsulate_noaction(self):
        field = 'nospaces'
        actual = self.target._encapsulate(field)
        assert actual == field, actual

    def test_encapsulate_withspaces(self):
        field = 'I have some spaces'
        expected = field
        actual = self.target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withquotes(self):
        field = 'I have a "quote"'
        expected = '"I have a ""quote"""'
        actual = self.target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withcomma(self):
        field = 'We invited the strippers, JFK, and Stalin'
        expected = '"' + field + '"'
        actual = self.target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withnewline(self):
        for extra in ['\n', '\r', '\r\n']:
            field = extra.join(['a', 'b'])
            expected = '"' + field + '"'
            actual = self.target._encapsulate(field)
            self.assertEqual(actual, expected)

    def test_encapsulate_withNumeric(self):
        actual = self.target._encapsulate(123)
        assert actual == '123', actual

    def test_encapsulate_withUnicode(self):
        field = u'We invited the strippers, JFK, and Stalin'
        expected = u'"' + field + u'"'
        actual = self.target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withNone(self):
        expected = ''
        actual = self.target._encapsulate(None)
        self.assertEqual(actual, expected)

    def test_encapsulate_withSimpleList(self):
        field = ['a', 'b', 'c']
        expected = '"[' + '\n'.join(field) + ']"'
        actual = self.target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withSimpleDictionary(self):
        field = {'a' : 'b', 'c': 'd'}
        expected = '"{a : b, c : d}"'
        actual = self.target._encapsulate(field)
        self.assertEqual(actual, expected)

    def test_encapsulate_withComplexList(self):
        field = [{'a' : 'b', 'c' : 'd'},{'e' : 'f', 'g' : 'h'}]
        expected = '"[{a : b, c : d}\n{e : f, g : h}]"'
        actual = self.target._encapsulate(field)
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
