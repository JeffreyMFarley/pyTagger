from __future__ import unicode_literals
import io
from pyTagger.operations.to_csv import SUBFIELD_SEP
from pyTagger.utils import saveJsonIncrementalDict

import sys
if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x

# -----------------------------------------------------------------------------
# State Machine
# -----------------------------------------------------------------------------


class Context(object):
    def __init__(self):
        self._reset()

    def _reset(self):
        self._buffer = []
        self._state = State.Initial

    def push(self, c):
        self._buffer.append(c)

    @property
    def separator(self):
        return self._separator

    def parse(self, inFile, excelFormat=True):
        self._reset()
        self._separator = '\t' if excelFormat else ','

        with io.open(inFile, 'r', encoding='utf_16_le') as f:
            c = f.read(1)  # skip BOM
            c = f.read(1)
            while c:
                self._state = self._state.onCharacter(self, c)
                self._state.run(self, c)
                if self._state.isEndOfRecord:
                    row = _unicode(''.join(self._buffer))
                    yield row.split('\x1f')
                    self._reset()
                c = f.read(1)


class State(object):
    def run(self, context, c):
        raise NotImplementedError

    def onCharacter(self, context, c):
        if c == context.separator:
            return State.EndOfField
        elif c == '"':
            return State.DoubleQuote
        elif c == '\n':
            return State.NewLine
        else:
            return State.Raw

    @property
    def isEndOfRecord(self):
        return False


class InitialState(State):
    pass


class RawState(State):
    def run(self, context, c):
        if c != '\r':
            context.push(c)


class EndOfFieldState(State):
    def run(self, context, c):
        context.push('\x1f')


class DoubleQuoteState(State):
    def run(self, context, c):
        if c != '"':
            context.push(c)

    def onCharacter(self, context, c):
        if c == '"':
            return State.EscapingDoubleQuote
        else:
            return self


class EscapingDoubleQuoteState(State):
    def run(self, context, c):
        pass

    def onCharacter(self, context, c):
        if c == context.separator:
            return State.EndOfField
        elif c == '"':
            context.push('"')
            return State.DoubleQuote
        elif c == '\n':
            return State.NewLine
        else:
            return State.Raw


class NewLineState(State):
    def run(self, context, c):
        pass

    def onCharacter(self, context, c):
        return self

    def isEndOfRecord(self):
        return True


State.Initial = InitialState()
State.Raw = RawState()
State.EndOfField = EndOfFieldState()
State.DoubleQuote = DoubleQuoteState()
State.EscapingDoubleQuote = EscapingDoubleQuoteState()
State.NewLine = NewLineState()

# -----------------------------------------------------------------------------

_collectionTags = ['comments', 'lyrics']
_numberTags = ['bitRate', 'bpm', 'disc', 'length', 'totalDisc',
               'totalTrack', 'track']
_booleanTags = ['vbr']


def _transform(s, column):
    if column in _numberTags and s:
        return int(s)
    elif column in _booleanTags:
        return s == 'True'
    return s


def _expand(cell, column):
    if column == 'fullPath':
        return (None, None)

    parts = column.split(SUBFIELD_SEP)
    if len(parts) == 1:
        return (column, cell)

    # Do not add a collection element if the text is null
    if not cell:
        return (None, None)

    elif parts[0] in ['comments', 'lyrics']:
        return (parts[0], {
            'lang': parts[1],
            'text': cell,
            'description': parts[2]
        })

    elif parts[0] == 'ufid':
        return (parts[0], {
            parts[1]: cell
        })

    # Unrecognized split
    return (None, None)


def _handleRow(row, columns):
    fullPath = row[-1]
    result = {k: [] for k in _collectionTags}
    result['ufid'] = {}

    for i, x in enumerate(row):
        cell = _transform(x, columns[i])
        k, v = _expand(cell, columns[i])

        if k is None:
            pass
        elif k in _collectionTags:
            result[k].append(v)
        elif k == 'ufid':
            id0, value0 = v.popitem()
            result[k][id0] = value0
        else:
            result[k] = v

    return (fullPath, result)


def _projection(fields, columns):
    if not columns:
        return fields
    return {k: fields[k] for k in columns if k in fields}


def convert(inFileName, outFileName, outputColumns=None, excelFormat=True,
            compact=True):
    context = Context()
    rowgen = context.parse(inFileName, excelFormat)
    columns = next(rowgen)

    output = saveJsonIncrementalDict(outFileName, compact)

    extracted = next(output)
    failed = 0

    for row in rowgen:
        k, v = _handleRow(row, columns)
        v = _projection(v, outputColumns)
        extracted = output.send((k, v))

    output.close()

    return extracted, failed
