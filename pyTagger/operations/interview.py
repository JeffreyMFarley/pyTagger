from __future__ import unicode_literals
import collections
import itertools
from pyTagger.operations.ask import askMultipleChoice
from pyTagger.utils import saveJson, fmap

basicOptions = {
    'B': 'Browse for Match',
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


def _enforceMultiple(rows):
    # Build a dictionary of all old paths
    olds = collections.defaultdict(list)
    for row in rows:
        if row['oldPath']:
            olds[row['oldPath']].append(row)

    # If an old row entry has multiple matches, all the rows should have
    # 'multiple' as the status
    for v in olds.values():
        if len(v) > 1:
            for row in v:
                row['status'] = 'multiple'

    return rows


def _verifyTrackNumbersMatch(rows):
    for row in rows:
        if row['oldTags']:
            if row['newTags']['track'] != row['oldTags']['track']:
                row['status'] = 'multiple'
    return rows


def _handleSingle(context):
    context.inputToOutput('ready')


def _handleMultiple(context):
    key = context.loadCurrent()

    options = dict(basicOptions)
    for i, row in enumerate(context.current):
        options[str(i + 1)] = row['oldPath']

    try:
        a = askMultipleChoice(context.step, key, options)
        try:
            context.chooseCurrent(int(a) - 1)
        except ValueError:
            if a == 'B':
                if not context.browseForCurrent():
                    context.currentToOutput()
            elif a == 'D':
                context.dropCurrent()
            elif a == 'I':
                context.currentToOutput()
            elif a == 'M':
                context.chooseCurrentAsManual()
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
        if a == 'B':
            if not context.browseForCurrent():
                context.currentToOutput()
        elif a == 'D':
            context.dropCurrent()
        elif a == 'I':
            context.currentToOutput()
        elif a == 'M':
            context.chooseCurrentAsManual()
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
        self.userQuit = False
        self.userDiscard = False
        self.step = 0

    # -------------------------------------------------------------------------
    # Private Methods

    def _preprocess(self):
        fns = [_enforceMultiple, _verifyTrackNumbersMatch]
        self.input = fmap(fns, self.input)

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
        rows = list(itertools.chain(self.output, self.current, self.input))
        return _scan(rows) == 0

    def conduct(self):
        self._preprocess()

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

    def chooseCurrentAsManual(self):
        row = self.current[0]
        row['status'] = 'manual'
        row['oldPath'] = None
        row['oldTags'] = None
        self.output.append(row)
        self.current = []

    def browseForCurrent(self):
        from pyTagger.proxies.id3 import ID3Proxy
        try:
            from tkFileDialog import askopenfilename
        except ImportError:
            from filedialog import askopenfilename

        filename = askopenfilename()
        if not filename:
            return False

        try:
            id3Proxy = ID3Proxy()
            row = self.current[0]
            row['status'] = 'ready'
            row['oldPath'] = filename
            row['oldTags'] = id3Proxy.extractTags(filename)
            self.output.append(row)
            self.current = []
            return True
        except Exception:
            return False

    def currentToOutput(self):
        for row in self.current:
            self.output.append(row)
        self.current = []

    def dropCurrent(self):
        self.current = []
