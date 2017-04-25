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

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_wrapped_out_null(self, stdout):
        target.wrapped_out(1, None)
        self.assertEqual(stdout.getvalue(), '1. (blank)\n')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_wrapped_out_number(self, stdout):
        target.wrapped_out(1, 33)
        self.assertEqual(stdout.getvalue(), '1. 33\n')

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

    @patch('pyTagger.operations.ask.askMultipleChoice')
    def test_editSet_cancel(self, step1):
        step1.return_value = 'X'
        actual = target.editSet(0, 'foo', ['one', 'two', 'three'])
        self.assertEqual(actual, (-1, None))

    @patch('pyTagger.operations.ask.askOrEnterMultipleChoice')
    @patch('pyTagger.operations.ask.askMultipleChoice')
    def test_editSet_choose(self, step1, step2):
        step1.return_value = '2'
        step2.return_value = '1'
        actual = target.editSet(0, 'foo', ['one', 'two', 'three'])
        self.assertEqual(actual, (1, 0))

    @patch('pyTagger.operations.ask.askOrEnterMultipleChoice')
    @patch('pyTagger.operations.ask.askMultipleChoice')
    def test_editSet_enter(self, step1, step2):
        step1.return_value = '2'
        step2.return_value = 'bar'
        actual = target.editSet(0, 'foo', ['one', 'two', 'three'])
        self.assertEqual(actual, (1, 'bar'))

    @patch('pyTagger.operations.ask.askOrEnterMultipleChoice')
    @patch('pyTagger.operations.ask.askMultipleChoice')
    def test_editSet_choose_or_cancel(self, step1, step2):
        step1.return_value = '2'
        step2.return_value = 'X'
        actual = target.editSet(0, 'foo', ['one', 'two', 'three'])
        self.assertEqual(actual, (-1, None))


if __name__ == '__main__':
    unittest.main()
