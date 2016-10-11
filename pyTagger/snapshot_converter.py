# -*- coding: utf-8 -*

from __future__ import print_function
import json
import os
import sys
import argparse
if sys.version < '3':  # pragma: no cover
    import codecs
    _input_json = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _input_table = lambda fileName: codecs.open(fileName, 'r',
                                                encoding='utf_16_le')
    _output_json = lambda fileName: codecs.open(fileName, 'w',
                                                encoding='utf-8')
    _output_table = lambda fileName: codecs.open(fileName, 'w',
                                                 encoding='utf_16_le')
    _unicode = unicode
else:  # pragma: no cover
    _input_json = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _input_table = lambda fileName: open(fileName, 'r', encoding='utf_16_le')
    _output_json = lambda fileName: open(fileName, 'w', encoding='utf-8')
    _output_table = lambda fileName: open(fileName, 'w', encoding='utf_16_le')
    _unicode = lambda x: x
from pyTagger.mp3_snapshot import Formatter

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

    def parse(self, inFile, useCsv=False):
        self._reset()
        self._separator = ',' if useCsv else '\t'
        with _input_table(inFile) as f:
            f.seek(2)  # skip BOM
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
# Classes
# -----------------------------------------------------------------------------


class SnapshotConverter(object):
    def __init__(self):
        pass

    def convert(self, inFileName, outFileName, fieldSet=None, useCsv=False):
        with _input_json(inFileName) as f:
            snapshot = json.load(f)

        # build the columns if they are not supplied
        if not fieldSet:
            fieldSet = self._extractColumns(snapshot)
        fieldSet.append('fullPath')

        # not using csv.DictWriter since the Python 2.x version has a hard time
        # supporting unicode
        with _output_table(outFileName) as f:
            sep = ',' if useCsv else '\t'

            # write BOM
            f.write(u'\ufeff')

            # write the header row
            a = sep.join([self._encapsulate(col) for col in fieldSet])
            f.writelines([a, '\n'])

            # write the rows
            for k in sorted(snapshot):
                row = snapshot[k]
                row['fullPath'] = k
                a = sep.join([self._encapsulate(row[col])
                              if col in row else ''
                              for col in fieldSet])
                f.writelines([a, '\n'])

    def _extractColumns(self, data):
        header = set()

        for _, v in data.items():
            for j in v.keys():
                if j not in header:
                    header.add(j)

        # Build the ordered set with the extra columns at the end
        known = Formatter.orderedAllColumns()
        unknown = header - set(known)

        columns = [c for c in known if c in header]
        for c in sorted(unknown):
            columns.append(c)

        return columns

    def _is_sequence(self, arg):
        return isinstance(arg, (list, set, dict))

    def _encapsulate(self, field):
        try:
            if self._is_sequence(field):
                return '"' + self._seqrepr(field).replace('"', '""') + '"'
            if not field:
                return ''
            needDoubleQuotes = [',', '"', '\r', '\n']
            addDoubleQuotes = any([x in field for x in needDoubleQuotes])
            if addDoubleQuotes:
                return '"' + field.replace('"', '""') + '"'
            return field
        except (TypeError, AttributeError):
            return str(field)

    def _seqrepr(self, iterable):
        if isinstance(iterable, (list, set)):
            return '[' + '\n'.join(self._seqrepr(x) for x in iterable) + ']'
        if isinstance(iterable, dict):
            return '{' + ', '.join([' : '.join([self._seqrepr(k),
                                                self._seqrepr(v)])
                                    for k, v in sorted(iterable.items())
                                    ]) + '}'
        return iterable


class ConvertBack(object):
    _collectionTags = ['comments', 'lyrics', 'ufid']
    _numberTags = ['bitRate', 'bpm', 'disc', 'length', 'totalDisc',
                   'totalTrack', 'track']
    _booleanTags = ['vbr']

    def convert(self, inFileName, outFileName, useCsv=False):
        context = Context()
        rowgen = context.parse(inFileName, useCsv)
        columns = next(rowgen)

        # Make the set output columns
        #fieldSet
        outputColumns = set(columns) - {
            'comments', 'lyrics', 'ufid', 'fullPath'
        }

        result = {}
        for row in rowgen:
            value = {columns[i]: self._transform(x, columns[i])
                     for (i, x) in enumerate(row)
                     if columns[i] in outputColumns}
            result[row[-1]] = value

        with _output_json(outFileName) as f:
            json.dump(result, f)

    def _transform(self, s, column):
        if column in self._numberTags and s:
            return int(s)
        elif column in self._booleanTags:
            return s == 'True'
        return s

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Convert between MP3 snapshot format and a row/column format'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('infile', metavar='infile', help='the snapshot to process')
    p.add_argument('outfile', nargs='?', metavar='outfile',
                   help='the name of the file that will hold the results')
    p.add_argument('-b', '--basic', action='store_true', dest='basic',
                   help=' '.join(Formatter.basic))
    p.add_argument('-s', '--songwriting', action='store_true',
                   dest='songwriting', help=' '.join(Formatter.songwriting))
    p.add_argument('-p', '--production', action='store_true',
                   dest='production', help=' '.join(Formatter.production))
    p.add_argument('-d', '--distribution', action='store_true',
                   dest='distribution', help=' '.join(Formatter.distribution))
    p.add_argument('-l', '--library', action='store_true', dest='library',
                   help=' '.join(Formatter.library))
    p.add_argument('-m', '--mp3Info', action='store_true', dest='mp3Info',
                   help=' '.join(Formatter.mp3Info))
    p.add_argument('-a', '--all', action='store_true', dest='all',
                   help='include all supported fields')
    p.add_argument('--csv', action='store_true', dest='csv',
                   help='CSV as the output format (default = tab-delimited)')
    p.add_argument('--convert-back', action='store_true', dest='reverse',
                   help='Convert CSV to JSON')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    columns = []
    if args.basic:
        columns = columns + Formatter.basic
    if args.songwriting:
        columns = columns + Formatter.songwriting
    if args.production:
        columns = columns + Formatter.production
    if args.distribution:
        columns = columns + Formatter.distribution
    if args.library:
        columns = columns + Formatter.library
    if args.mp3Info:
        columns = columns + Formatter.mp3Info
    if args.all:
        columns = Formatter.orderedAllColumns()

    if not args.outfile:
        root, ext = os.path.splitext(args.infile)
        newext = '.csv' if args.csv else '.txt'
        if args.reverse:
            newext = '.json'
        args.outfile = root + newext

    if not args.reverse:
        pipeline = SnapshotConverter()
        pipeline.convert(args.infile, args.outfile, columns, args.csv)
    else:
        pipeline = ConvertBack()
        pipeline.convert(args.infile, args.outfile, args.csv)
