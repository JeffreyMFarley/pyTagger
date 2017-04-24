from __future__ import unicode_literals
import io
import unittest
import pyTagger.operations.ask as target
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


class TestAsk(unittest.TestCase):
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_wrapped_out(self, stdout):
        target.wrapped_out(1, u'f\u00f2\u00f3 b\u00e3r b\u00e5z q\u00e2z')
        self.assertEqual(stdout.getvalue(), '1. foo bar baaz qaz\n')

    @patch('pyTagger.operations.ask.get_input')
    def test_askMultipleChoice(self, userInput):
        userInput.return_value = '1'
        options = {
            '1': 'One'
        }

        with patch('sys.stdout', new_callable=io.StringIO) as stdout:
            target.askMultipleChoice('A', 'title', options, True)
            self.assertEqual(stdout.getvalue(), 'A. title\n\n\n1. One\n\n\n')

        with patch('sys.stdout', new_callable=io.StringIO) as stdout:
            target.askMultipleChoice('A', 'title', options, False)
            self.assertEqual(stdout.getvalue(), 'A. title\n\n\n1. One\n\n\n')

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('pyTagger.operations.ask.get_input')
    def test_askOrEnterMultipleChoice_enter(self, userInput, stdout):
        userInput.return_value = 'Echo'
        options = {'A': 'Alpha'}
        actual = target.askOrEnterMultipleChoice('1', 'title', options)
        self.assertEqual(actual, 'Echo')

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('pyTagger.operations.ask.get_input')
    def test_askOrEnterMultipleChoice_choose(self, userInput, stdout):
        userInput.return_value = 'a'
        options = {'A': 'Alpha'}
        actual = target.askOrEnterMultipleChoice('1', 'title', options, False)
        self.assertEqual(actual, 'A')

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('pyTagger.operations.ask.get_input')
    def test_askOrEnterMultipleChoice_enterSingle(self, userInput, stdout):
        userInput.return_value = 'm'
        options = {'A': 'Alpha'}
        actual = target.askOrEnterMultipleChoice('1', 'title', options)
        self.assertEqual(actual, 'm')

if __name__ == '__main__':
    unittest.main()
