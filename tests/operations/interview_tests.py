from __future__ import unicode_literals
import copy
import io
import sys
import unittest
import pyTagger.operations.interview as sut
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock


data = [
    {'status': 'single', 'newPath': 'alpha', 'oldPath': 'foo'},
    {'status': 'multiple', 'newPath': 'beta', 'oldPath': 'bar'},
    {'status': 'multiple', 'newPath': 'beta', 'oldPath': 'baz'}
]


class TestInterviewFunctions(unittest.TestCase):
    def setUp(self):
        self.context = Mock(spec=sut.Interview)
        self.context.loadCurrent.return_value = 'foo'
        self.context.current = data
        self.context.step = 99

    def test_scan_bad_interview(self):
        with self.assertRaises(ValueError):
            sut._scan([{}])

    def test_scan_has_unfinished(self):
        rows = [{'status': x} for x in [
            'single', 'multiple', 'nothing', 'insufficient', 'foo'
        ]]
        actual = sut._scan(rows)
        self.assertEqual(actual, 4)

    def test_scan_no_unfinished(self):
        rows = [{'status': x} for x in [
            'ready', 'manual', 'foo'
        ]]
        actual = sut._scan(rows)
        self.assertEqual(actual, 0)

    # --- preprocess function  -------------------------------------------------

    def test_enforceMultiple(self):
        fixture = [
          {
            'newPath': '06 Meat Beat Manifesto - Kick That Man.mp3',
            'oldPath': '06 Kneel & Buzz.mp3',
            'status': 'multiple'
          },
          {
            'newPath': '06 Meat Beat Manifesto - Kick That Man.mp3',
            'oldPath': '07 Kick That Man.mp3',
            'status': 'multiple'
          },
          {
            'newPath': '07 Meat Beat Manifesto - Kneel & Buzz.mp3',
            'oldPath': '06 Kneel & Buzz.mp3',
            'status': 'single'
          },
          {
            'newPath': '08 Meat Beat Manifesto - Fear Version.mp3',
            'oldPath': '08 Fear Version.mp3',
            'status': 'single'
          },
          {
            'newPath': '99 foo.mp3',
            'oldPath': None,
            'status': 'nothing'
          }
        ]
        actual = sut._enforceMultiple(fixture)
        self.assertEqual(actual[0]['status'], 'multiple')
        self.assertEqual(actual[1]['status'], 'multiple')
        self.assertEqual(actual[2]['status'], 'multiple')
        self.assertEqual(actual[3]['status'], 'single')
        self.assertEqual(actual[4]['status'], 'nothing')


    def test__verifyTrackNumbersMatch(self):
        fixture = [
          {
            'newPath': '02 Kinky - Mas.mp3',
            'newTags': {
              'track': 2,
            },
            'oldPath': '01 Mas.mp3',
            'oldTags': {
              'track': 1,
            },
            'status': 'single'
          },
          {
            'newPath': '08 Leftfield - A Final Hit.mp3',
            'newTags': {
              'track': 8,
            },
            'oldPath': '08 A Final Hit.mp3',
            'oldTags': {
              'track': 8,
            },
            'status': 'single'
          },
          {
            'newPath': '03 foo.mp3',
            'newTags': {
              'track': 3,
            },
            'oldPath': None,
            'oldTags': None,
            'status': 'nothing'
          }
        ]
        actual = sut._verifyTrackNumbersMatch(fixture)
        self.assertEqual(actual[0]['status'], 'multiple')
        self.assertEqual(actual[1]['status'], 'single')
        self.assertEqual(actual[2]['status'], 'nothing')

    # --- handleX ------------------------------------------------------

    def test_handleSingle(self):
        sut._handleSingle(self.context)
        self.context.inputToOutput.assert_called_with('ready')

    def test_handlePass(self):
        sut._handlePass(self.context)
        self.assertTrue(self.context.inputToOutput.called)

    # --- handleMultiple ------------------------------------------------------

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_validate_ask(self, ask):
        expected = dict(sut.basicOptions)
        expected.update({
            '1': 'foo',
            '2': 'bar',
            '3': 'baz'
        })
        ask.return_value = '1'

        sut._handleMultiple(self.context)
        ask.assert_called_with(99, 'foo', expected)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_first(self, ask):
        ask.return_value = '1'
        sut._handleMultiple(self.context)
        self.context.chooseCurrent.assert_called_with(0)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_second(self, ask):
        ask.return_value = '2'
        sut._handleMultiple(self.context)
        self.context.chooseCurrent.assert_called_with(1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_browse_successful(self, ask):
        ask.return_value = 'B'
        self.context.browseForCurrent.return_value = True
        sut._handleMultiple(self.context)
        self.assertEqual(self.context.currentToOutput.call_count, 0)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_browse_cancel(self, ask):
        ask.return_value = 'B'
        self.context.browseForCurrent.return_value = False
        sut._handleMultiple(self.context)
        self.assertEqual(self.context.currentToOutput.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_drop(self, ask):
        ask.return_value = 'D'
        sut._handleMultiple(self.context)
        self.assertEqual(self.context.dropCurrent.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_manual(self, ask):
        ask.return_value = 'M'
        sut._handleMultiple(self.context)
        self.assertEqual(self.context.chooseCurrentAsManual.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_ignore(self, ask):
        ask.return_value = 'I'
        sut._handleMultiple(self.context)
        self.assertEqual(self.context.currentToOutput.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_exit(self, ask):
        ask.return_value = 'X'
        sut._handleMultiple(self.context)
        self.assertEqual(self.context.quit.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_leave_interview(self, ask):
        ask.return_value = 'Z'
        sut._handleMultiple(self.context)
        self.assertEqual(self.context.discard.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_control_c(self, ask):
        ask.side_effect = KeyboardInterrupt
        sut._handleMultiple(self.context)
        self.assertEqual(self.context.discard.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleMultiple_choose_illegal(self, ask):
        ask.return_value = '@'
        with self.assertRaises(AssertionError):
            sut._handleMultiple(self.context)

    # --- handleNothing -------------------------------------------------------

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_validate_ask(self, ask):
        expected = dict(sut.basicOptions)
        ask.return_value = 'M'
        sut._handleNothing(self.context)
        ask.assert_called_with(99, 'foo', expected)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_choose_browse_successful(self, ask):
        ask.return_value = 'B'
        self.context.browseForCurrent.return_value = True
        sut._handleNothing(self.context)
        self.assertEqual(self.context.currentToOutput.call_count, 0)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_choose_browse_cancel(self, ask):
        ask.return_value = 'B'
        self.context.browseForCurrent.return_value = False
        sut._handleNothing(self.context)
        self.assertEqual(self.context.currentToOutput.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_choose_ignore(self, ask):
        ask.return_value = 'I'
        sut._handleNothing(self.context)
        self.assertEqual(self.context.currentToOutput.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_choose_manual(self, ask):
        ask.return_value = 'M'
        sut._handleNothing(self.context)
        self.assertEqual(self.context.chooseCurrentAsManual.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_choose_drop(self, ask):
        ask.return_value = 'D'
        sut._handleNothing(self.context)
        self.assertEqual(self.context.dropCurrent.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_choose_exit(self, ask):
        ask.return_value = 'X'
        sut._handleNothing(self.context)
        self.assertEqual(self.context.quit.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_choose_leave_interview(self, ask):
        ask.return_value = 'Z'
        sut._handleNothing(self.context)
        self.assertEqual(self.context.discard.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_control_c(self, ask):
        ask.side_effect = KeyboardInterrupt
        sut._handleNothing(self.context)
        self.assertEqual(self.context.discard.call_count, 1)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_handleNothing_choose_illegal(self, ask):
        ask.return_value = '@'
        with self.assertRaises(AssertionError):
            sut._handleNothing(self.context)


class TestInterviewClass(unittest.TestCase):
    def setUp(self):
        self.target = sut.Interview(copy.deepcopy(data))

    @patch('pyTagger.operations.interview.fmap')
    def test_preprocess(self, fmap):
        self.target._preprocess()
        fmap.assert_called_with(
            [sut._enforceMultiple, sut._verifyTrackNumbersMatch], data
        )

    def test_route(self):
        actual = next(self.target._route())
        self.assertEqual(actual, sut._handleSingle)

        _ = self.target.input.pop(0)
        actual = next(self.target._route())
        self.assertEqual(actual, sut._handleMultiple)

    def test_routeUserDiscard(self):
        self.target.userDiscard = True
        with self.assertRaises(StopIteration):
            actual = next(self.target._route())

    def test_routeUserQuit(self):
        self.target.userQuit = True
        with self.assertRaises(StopIteration):
            actual = next(self.target._route())

    def test_routeEmptyInput(self):
        self.target.input = []
        with self.assertRaises(StopIteration):
            actual = next(self.target._route())

    def test_isComplete(self):
        actual = self.target.isComplete()
        self.assertFalse(actual)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_conduct_yes(self, ask):
        def callback(x):
            self.assertEqual(x, self.target)

        ask.return_value = 'Y'
        self.target._route = Mock(return_value=[callback])
        self.target._preprocess = Mock()
        actual = self.target.conduct()
        self.assertTrue(actual)

    @patch('pyTagger.operations.interview.askMultipleChoice')
    def test_conduct_no(self, ask):
        ask.return_value = 'N'
        self.target._preprocess = Mock()
        actual = self.target.conduct()
        self.assertFalse(actual)

    @patch('pyTagger.operations.interview.saveJson')
    def test_saveState(self, saveJson):
        self.target.input = ['1', '2']
        self.target.current = ['3', '4']
        self.target.output = ['5', '6']
        self.target.saveState('foo.json')
        saveJson.assert_called_with('foo.json', ['5', '6', '3', '4', '1', '2'])

    def test_loadCurrent(self):
        self.target.loadCurrent()
        self.assertEqual(self.target.input, data[1:])
        self.assertEqual(self.target.current, [data[0]])

    def test_quit(self):
        self.target.quit()
        self.assertTrue(self.target.userQuit)

    def test_discard(self):
        self.target.discard()
        self.assertTrue(self.target.userDiscard)

    def test_inputToOutput(self):
        self.target.inputToOutput()
        self.assertEqual(self.target.input, data[1:])
        self.assertEqual(self.target.output, [data[0]])

    def test_inputToOutput_withStatus(self):
        self.target.inputToOutput('foo')
        self.assertEqual(self.target.input, data[1:])
        for row in self.target.output:
            self.assertEqual(row['status'], 'foo')

    def test_chooseCurrent(self):
        self.target.current = copy.deepcopy(data)
        self.target.chooseCurrent(0, 'bar')
        self.assertEqual(self.target.current, [])
        self.assertEqual(len(self.target.output), 1)
        self.assertEqual(self.target.output[0]['status'], 'bar')

    def test_chooseCurrentAsManual(self):
        self.target.current = copy.deepcopy(data)
        self.target.chooseCurrentAsManual()
        self.assertEqual(self.target.current, [])
        self.assertEqual(len(self.target.output), 1)
        self.assertEqual(self.target.output[0]['status'], 'manual')
        self.assertEqual(self.target.output[0]['newPath'], 'alpha')
        self.assertEqual(self.target.output[0]['oldPath'], None)
        self.assertEqual(self.target.output[0]['oldTags'], None)

    @unittest.skipIf(sys.version >= '3', 'tkFileDialog is in PY 2.X')
    @patch('tkFileDialog.askopenfilename')
    def test_browseForCurrent_noFile(self, askOpen):
        askOpen.return_value = ''
        actual = self.target.browseForCurrent()
        self.assertEqual(actual, False)

    @unittest.skipIf(sys.version >= '3', 'tkFileDialog is in PY 2.X')
    @patch('pyTagger.proxies.id3.ID3Proxy')
    @patch('tkFileDialog.askopenfilename')
    def test_browseForCurrent_badFile(self, askOpen, proxy):
        askOpen.return_value = 'foo.mp3'
        proxy.side_effect = IOError
        actual = self.target.browseForCurrent()
        self.assertEqual(actual, False)

    @unittest.skipIf(sys.version >= '3', 'tkFileDialog is in PY 2.X')
    @patch('pyTagger.proxies.id3.ID3Proxy')
    @patch('tkFileDialog.askopenfilename')
    def test_browseForCurrent_goodFile(self, askOpen, proxy):
        self.target.current = copy.deepcopy(data)

        askOpen.return_value = 'foo.mp3'
        instance = proxy.return_value
        instance.extractTags.return_value = 'foo'

        actual = self.target.browseForCurrent()

        self.assertEqual(actual, True)
        self.assertEqual(self.target.output[0]['status'], 'ready')
        self.assertEqual(self.target.output[0]['oldPath'], 'foo.mp3')
        self.assertEqual(self.target.output[0]['oldTags'], 'foo')
        self.assertEqual(self.target.current, [])

    def test_currentToOutput(self):
        self.target.current = copy.deepcopy(data)
        self.target.currentToOutput()
        self.assertEqual(self.target.current, [])
        self.assertEqual(self.target.output, data)

    def test_dropCurrent(self):
        self.target.current = copy.deepcopy(data)
        self.target.dropCurrent()
        self.assertEqual(self.target.current, [])
        self.assertEqual(self.target.output, [])

if __name__ == '__main__':
    unittest.main()
