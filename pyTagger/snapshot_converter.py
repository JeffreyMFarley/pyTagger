# -*- coding: utf-8 -*

from __future__ import print_function
import csv
import json
import os
import sys
import argparse
if sys.version < '3':
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: open(fileName, 'w', encoding='utf-8')

if __package__ is None:
    from mp3_snapshot import Formatter
else:
    from .mp3_snapshot import Formatter

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class SnapshotConverter:
    def __init__(self):
        pass

    def convert(self, inFileName, outFileName, fieldSet=[], useCsv=False):
        with _input(inFileName) as f:
            snapshot = json.load(f)

        # build the columns if they are not supplied 
        if not fieldSet:
            fieldSet = self.extractColumns(snapshot)
        fieldSet.append('fullPath')
        
        with _output(outFileName) as f:
            writer = csv.DictWriter(f, fieldSet, dialect=csv.excel if useCsv else csv.excel_tab, extrasaction='ignore')
            writer.writeheader()
            for k,v in snapshot.items():
                row = v
                row['fullPath'] = k
                try:        
                    writer.writerow(row)
                except UnicodeError:
                    for field in fieldSet:
                        if isinstance(row[field], basestring):
                            row[field] = row[field].encode('ascii', 'replace')
                    writer.writerow(row)

    def extractColumns(self, data):
        header = set()

        for k, v in data.items():
            for j in v.keys():
                if j not in header:
                    header.add(j)

        # Build the ordered set with the extra columns at the end
        known = orderedAllColumns()
        unknown = header - set(known)

        columns = [c for c in known if c in header]
        for c in unknown:
            columns.append(c)

        return columns

#-------------------------------------------------------------------------------
# Helper function
#-------------------------------------------------------------------------------

def orderedAllColumns():
    # preserve order
    columns = Formatter.basic + \
              Formatter.songwriting + \
              Formatter.production + \
              Formatter.distribution + \
              Formatter.library + \
              Formatter.mp3Info
        
    # for testing that all fields are grouped
    missing = set(Formatter.columns) - set(columns)
    assert(not missing)
    return columns

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

sys.argv = [sys.argv[0], r'C:\dvp\Mp3Reduce\data\mp3s_enh.json', 
                         r'C:\Users\Jeff\Documents\East Wind\snapshot.txt']

def buildArgParser():
    p = argparse.ArgumentParser(description='Convert MP3 snapshot to a row and column format')
    p.add_argument('infile', metavar='infile', help='the snapshot to process')
    p.add_argument('outfile',  nargs='?', metavar='outfile',
                   default='mp3s.txt',
                   help='the name of the file that will hold the results')
    p.add_argument('-b', '--basic', action='store_true', dest='basic',
                   help=' '.join(Formatter.basic))
    p.add_argument('-s', '--songwriting', action='store_true', dest='songwriting',
                   help=' '.join(Formatter.songwriting))
    p.add_argument('-p', '--production', action='store_true', dest='production',
                   help=' '.join(Formatter.production))
    p.add_argument('-d', '--distribution', action='store_true', dest='distribution',
                   help=' '.join(Formatter.distribution))
    p.add_argument('-l', '--library', action='store_true', dest='library',
                   help=' '.join(Formatter.library))
    p.add_argument('-m', '--mp3Info', action='store_true', dest='mp3Info',
                   help=' '.join(Formatter.mp3Info))
    p.add_argument('-a', '--all', action='store_true', dest='all',
                   help='include all supported fields')
    p.add_argument('--csv', action='store_true', dest='csv',
                   help='use CSV as the output format (tab-delimited is the default)')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    columns = []
    if args.basic:  columns = columns + Formatter.basic
    if args.songwriting:  columns = columns + Formatter.songwriting
    if args.production:  columns = columns + Formatter.production
    if args.distribution:  columns = columns + Formatter.distribution
    if args.library:  columns = columns + Formatter.library
    if args.mp3Info:  columns = columns + Formatter.mp3Info
    if args.all:    columns = orderedAllColumns() 
    
    pipeline = SnapshotConverter()
    pipeline.convert(args.infile, args.outfile, columns, args.csv)