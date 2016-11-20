import os
from configargparse import getArgumentParser
from pyTagger.models import Snapshot
from pyTagger.operations.on_mp3 import updateFromSnapshot
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import loadJson, defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('update',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser('snapshot')],
                      description='update ID3 fields from a snapshot')
group = p.add_argument_group('Files')
group.add('infile', help='the snapshot to process')
group = p.add_argument_group('Options')
group.add('--upgrade', action='store_true', dest='upgrade',
          help='Upgrade the tags to be at least 2.3')

# -----------------------------------------------------------------------------


def process(args):
    columns = Snapshot.columnsFromArgs(args)
    id3Proxy = ID3Proxy(columns)
    snapshot = loadJson(args.infile)
    return updateFromSnapshot(id3Proxy, snapshot, args.upgrade)
