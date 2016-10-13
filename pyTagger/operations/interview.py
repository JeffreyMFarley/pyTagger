from __future__ import unicode_literals
import collections
import itertools
from pyTagger.operations.ask import askMultipleChoice
from pyTagger.utils import saveJson

basicOptions = {
    'D': 'Drop this row',
    'M': 'Manual Entry',
    'I': 'Ignore for now',
    'X': 'Save the interview and Exit',
    'Z': 'Discard the interview'
}


def _scan(rows):
    tally = collections.Counter()

    for row in rows:
        if 'status' not in row:
            raise ValueError("Missing status field.  Is this an interview?")
        tally[row['status']] += 1

    return sum([
        1
        for x in tally.keys()
        if x in ['single', 'multiple', 'nothing', 'insufficient']
    ])


def _handleSingle(context):
    context.inputToOutput('ready')


def _handleMultiple(context):
    key = context.loadCurrent()

    options = dict(basicOptions)
    del options['M']
    for i, row in enumerate(context.current):
        options[str(i + 1)] = row['oldPath']

    try:
        a = askMultipleChoice(context.step, key, options)
        try:
            context.chooseCurrent(int(a) - 1)
        except:
            if a == 'D':
                context.dropCurrent()
            elif a == 'I':
                context.currentToOutput()
            elif a == 'X':
                context.quit()
            elif a == 'Z':
                context.discard()
            else:
                raise AssertionError("askMultipleChoice failed to enforce")
    except KeyboardInterrupt:
        context.discard()


def _handleNothing(context):
    key = context.loadCurrent()
    try:
        a = askMultipleChoice(context.step, key, basicOptions)
        if a == 'M':
            context.chooseCurrent(0, 'manual')
        elif a == 'D':
            context.dropCurrent()
        elif a == 'X':
            context.quit()
        elif a == 'Z':
            context.discard()
        else:
            raise AssertionError("askMultipleChoice failed to enforce")
    except KeyboardInterrupt:
        context.discard()


def _handlePass(context):
    context.inputToOutput()


routes = {
    'single': _handleSingle,
    'multiple': _handleMultiple,
    'nothing': _handleNothing,
    'insufficient': _handleNothing,
    'ready': _handlePass,
    'manual': _handlePass
}

# -----------------------------------------------------------------------------


class Interview(object):
    def __init__(self, rows):
        self.input = rows
        self.current = []
        self.output = []
        self.unfinished = _scan(rows)
        self.userQuit = False
        self.userDiscard = False
        self.step = 0

    # -------------------------------------------------------------------------
    # Private Methods

    def _route(self):
        for self.step in itertools.count(1):  # pragma: no branch
            if self.userQuit or self.userDiscard:
                raise StopIteration

            if len(self.input) == 0:
                raise StopIteration

            peek = self.input[0]['status']
            yield routes[peek]

    # -------------------------------------------------------------------------
    # Public Methods

    def isComplete(self):
        return self.unfinished == 0

    def conduct(self):
        a = askMultipleChoice(0, 'Ready to begin the interview?', {
            'Y': 'Yes',
            'N': 'No'
        }, False)

        if a == 'N':
            return False

        for handler in self._route():
            handler(self)

        return not self.userDiscard

    def saveState(self, fileName):
        rows = list(itertools.chain(self.output, self.current, self.input))
        saveJson(fileName, rows)

    # -------------------------------------------------------------------------
    # State Events

    def loadCurrent(self):
        assert len(self.current) == 0
        key = self.input[0]['newPath']
        while len(self.input) and key == self.input[0]['newPath']:
            self.current.append(self.input.pop(0))
        return key

    def quit(self):
        self.userQuit = True

    def discard(self):
        self.userDiscard = True

    def inputToOutput(self, newStatus=None):
        row = self.input.pop(0)
        if newStatus:
            row['status'] = newStatus
        self.output.append(row)

    def chooseCurrent(self, i, newStatus='ready'):
        row = self.current[i]
        row['status'] = newStatus
        self.output.append(row)
        self.current = []

    def currentToOutput(self):
        for row in self.current:
            self.output.append(row)
        self.current = []

    def dropCurrent(self):
        self.current = []
