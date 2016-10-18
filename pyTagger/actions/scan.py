import os
from configargparse import getArgumentParser
from pyTagger.models import Snapshot
from pyTagger.operations.on_directory import buildSnapshot
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('scan',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser('snapshot')],
                      description='create a snapshot from directories of MP3s')
group = p.add_argument_group('Files')
group.add('path',  nargs='?', default=os.getcwd(),
          help='the path to scan')
group.add('outfile',  nargs='?', default='mp3s.json',
          help='the name of the file that will hold the results')
group.add('--compact', action='store_true', dest='compact',
          help='output the JSON in a compact format')

# -----------------------------------------------------------------------------


def process(args):
    columns = Snapshot.columnsFromArgs(args)
    id3Proxy = ID3Proxy(columns)
    s, f = buildSnapshot(args.path, args.outfile, id3Proxy, args.compact)
    return 'Extracted tags from {0} files\nFailed {1}'.format(s, f)
