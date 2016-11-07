from __future__ import unicode_literals
import os
from configargparse import getArgumentParser
from pyTagger.operations.to_csv import writeCsv
from pyTagger.utils import loadJson, defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('to-csv',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser()],
                      description='export snapshot to CSV')
group = p.add_argument_group('Files')
group.add('infile', help='the snapshot to process')
group.add('outfile', nargs='?', help='the CSV file that will hold the results')
group.add('--csv-format', action='store_true', default=False,
          help='use commas not tabs')

# -----------------------------------------------------------------------------


def _getOutputName(args):
    if args.outfile:
        return args.outfile

    root, _ = os.path.splitext(args.infile)
    if args.csv_format:
        return root + '.csv'
    else:
        return root + '.txt'


def process(args):
    outfile = _getOutputName(args)
    snapshot = loadJson(args.infile)
    writeCsv(snapshot, outfile, not args.csv_format)
    return "Exported to " + outfile
