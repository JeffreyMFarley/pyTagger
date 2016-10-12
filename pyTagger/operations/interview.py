from __future__ import print_function
import collections
import itertools
from pyTagger.operations.ask import askMultipleChoice
from pyTagger.utils import saveJsonIncrementalArray

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

    return tally, sum([
        1
        for x in tally.keys()
        if x in ['single', 'multiple', 'nothing', 'insufficient']
    ])


def _handleSingle(context):
    context.inputToOutput('ready')


def _handleMultiple(context):
    key = context.fillAccum()

    options = dict(basicOptions)
    del options['M']
    for i, row in enumerate(context.accum):
        options[str(i + 1)] = row['oldPath']

    try:
        a = askMultipleChoice(context.step, key, options)
        try:
            context.choose(int(a))
        except:
            if a == 'D':
                context.dropAccum()
            elif a == 'I':
                context.accumToOutput()
            elif a == 'X':
                context.quit()
            elif a == 'Z':
                context.discard()
    except KeyboardInterrupt:
        context.discard()


def _handleNothing(context):
    key = context.fillAccum()
    try:
        a = askMultipleChoice(context.step, key, basicOptions)
        if a == 'M':
            context.choose(0, 'manual')
        elif a == 'D':
            context.dropAccum()
        elif a == 'X':
            context.quit()
        elif a == 'Z':
            context.discard()
    except KeyboardInterrupt:
        context.discard()

# -----------------------------------------------------------------------------


class Interview(object):
    def __init__(self, rows):
        self.input = rows
        self.accum = []
        self.output = []
        self.tally, self.unfinished = _scan(rows)
        self.userQuit = False
        self.userDiscard = False
        self.step = 0

        self.routes = {
            'single': _handleSingle,
            'multiple': _handleMultiple,
            'nothing': _handleNothing,
            'insufficient': _handleNothing,
            'ready': self.inputToOutput,
            'manual': self.inputToOutput
        }

    # -------------------------------------------------------------------------
    # Private Methods

    def _route(self):
        for self.step in itertools.count():
            if self.userQuit or self.userDiscard:
                raise StopIteration

            if len(self.input) == 0:
                raise StopIteration

            peek = self.input[0]['status']
            yield self.routes[peek]

    # -------------------------------------------------------------------------
    # Public Methods

    def isComplete(self):
        return self.unfinished == 0

    def conduct(self):
        for handler in self._route():
            handler(self)

    def saveState(self, fileName):
        if self.userDiscard:
            return

        for r in itertools.chain(self.output, self.accum, self.input):
            path = r['newPath']
            info = ('..' + path[-60:]) if len(path) > 60 else data
            print(r['status'], info)

    # -------------------------------------------------------------------------
    # State Events

    def quit(self):
        self.userQuit = True

    def discard(self):
        self.userDiscard = True

    def inputToOutput(self, newStatus=None):
        row = self.input.pop(0)
        if newStatus:
            row['status'] = newStatus
        self.output.append(row)

    def fillAccum(self):
        assert len(self.accum) == 0
        key = self.input[0]['newPath']
        while len(self.input) and key == self.input[0]['newPath']:
            self.accum.append(self.input.pop(0))
        return key

    def choose(self, i, newStatus='ready'):
        row = self.accum[i]
        row['status'] = newStatus
        self.output.append(row)
        self.accum = []

    def accumToOutput(self):
        for row in self.accum:
            self.output.append(row)
        self.accum = []

    def dropAccum(self):
        self.accum = []
