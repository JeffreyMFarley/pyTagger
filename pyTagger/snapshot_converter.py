# -*- coding: utf-8 -*

from __future__ import print_function
import json
import os
import sys
import argparse
import unicodedata
if sys.version < '3':
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf_16_le')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: open(fileName, 'w', encoding='utf_16_le')
from pyTagger.mp3_snapshot import Formatter

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class SnapshotConverter:
    def __init__(self):
        pass

    def convert(self, inFileName, outFileName, fieldSet=[], useCsv=False):
        with _input(inFileName) as f:
            snapshot = json.load(f)

        # build the columns if they are not supplied
        if not fieldSet:
            fieldSet = self._extractColumns(snapshot)
        fieldSet.append('fullPath')

        # not using csv.DictWriter since the Python 2.x version has a hard time 
        # supporting unicode
        with _output(outFileName) as f:
            sep = ',' if useCsv else '\t'

            # write BOM
            f.write(u'\ufeff')

            # write the header row
            a = sep.join([self._encapsulate(col) for col in fieldSet])
            f.writelines([a, os.linesep])

            # write the rows                
            for k, v in snapshot.items():
                row = v
                row['fullPath'] = k
                a = sep.join([self._encapsulate(row[col])
                              if col in row else ''
                              for col in fieldSet])
                f.writelines([a, os.linesep])                

    def _extractColumns(self, data):
        header = set()

        for k, v in data.items():
            for j in v.keys():
                if j not in header:
                    header.add(j)

        # Build the ordered set with the extra columns at the end
        known = Formatter.orderedAllColumns()
        unknown = header - set(known)

        columns = [c for c in known if c in header]
        for c in unknown:
            columns.append(c)

        return columns

    def _is_sequence(self, arg):
        return isinstance(arg, (list, set, dict))

    def _encapsulate(self, field):
        try:
            if self._is_sequence(field):
                return  '"' + self._seqrepr(field) + '"'
            if not field:
                return ''
            needDoubleQuotes = [',', '"', '\r', '\n']
            addDoubleQuotes = any([x in field for x in needDoubleQuotes])
            if addDoubleQuotes:
                return '"' + field.replace('"', '""') + '"' 
            return field
        except (TypeError, AttributeError):
            return str(field)

    def _seqrepr(self, iter):
        if isinstance(iter, (list, set)):
            return '\n'.join(self._seqrepr(x) for x in iter)
        if isinstance(iter, dict):
            return ', '.join([' : '.join([self._seqrepr(k), 
                                          self._seqrepr(v)])
                                         for k,v in iter.items()])
        return iter
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Convert MP3 snapshot to a row and column format'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('infile', metavar='infile', help='the snapshot to process')
    p.add_argument('outfile',  nargs='?', metavar='outfile',
                   default='mp3s.txt',
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

    pipeline = SnapshotConverter()
    pipeline.convert(args.infile, args.outfile, columns, args.csv)
