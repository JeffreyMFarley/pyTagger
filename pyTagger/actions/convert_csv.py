from __future__ import unicode_literals
import os
from configargparse import getArgumentParser
from pyTagger.models import Snapshot
from pyTagger.operations.from_csv import convert
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('convert-csv',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser('snapshot')],
                      description='convert CSV to snapshot')
group = p.add_argument_group('Files')
group.add('infile', help='the CSV to process')
group.add('outfile', nargs='?', help='the snapshot that will hold the results')
group.add('--csv-format', action='store_true', default=False,
          help='use commas not tabs')
group.add('--compact', action='store_true', dest='compact',
          help='output the JSON in a compact format')

# -----------------------------------------------------------------------------


def _getOutputName(args):
    if args.outfile:
        return args.outfile

    root, _ = os.path.splitext(args.infile)
    return root + '.json'


def process(args):
    outfile = _getOutputName(args)
    columns = Snapshot.columnsFromArgs(args)
    print('Exporting to ' + outfile)
    s, f = convert(args.infile, outfile, columns, not args.csv_format,
                   args.compact)
    return '{0} rows\n{1} fail(s)'.format(s, f)
