from __future__ import print_function
from __future__ import unicode_literals
import io
import os
import pyTagger.actions.isonom as isonom
from configargparse import getArgumentParser
from pyTagger.operations.from_csv import convert
from pyTagger.operations.on_directory import buildSnapshot, prepareForLibrary
from pyTagger.operations.on_directory import renameFiles
from pyTagger.operations.on_mp3 import updateFromSnapshot
from pyTagger.operations.to_csv import writeCsv
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import loadJson, defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('prepare',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser()],
                      description='groom MP3s before adding to house library')
p.add('step', choices=[1, 2], type=int, default=1,
      help='which step to execute')
group = p.add_argument_group('Step 1')
group.add('--download-dir', default=os.path.join(os.getcwd(), 'Amazon Music'),
          help='the path where the downloaded files are located')
group.add('--prepare-snapshot',  default='prepare.json',
          help='the snapshot of the downloaded files')
group.add('--prepare-csv', default='prepare.csv',
          help='a CSV version of the snapshot of the downloaded files')
group.add('--compact', action='store_true', dest='compact',
          help='output the JSON in a compact format')
group.add('--csv-format', action='store_true', default=False,
          help='use commas not tabs')
group = p.add_argument_group('Step 2')
group.add('--update-snapshot', default='update.json',
          help='a snapshot of what the mp3s should look like')

# -----------------------------------------------------------------------------

SUCCESS = "Success"


def _step1(args):
    print('Changing tags to conform with library')
    prepared = prepareForLibrary(args.download_dir)
    print(prepared, 'files processed')

    print('Creating a snapshot of files')
    id3Proxy = ID3Proxy()
    s, f = buildSnapshot(args.download_dir, args.prepare_snapshot,
                         id3Proxy, args.compact)
    print('Extracted tags from {0} files\nFailed {1}'.format(s, f))

    print('Converting to CSV')
    snapshot = loadJson(args.prepare_snapshot)
    writeCsv(snapshot, args.prepare_csv, not args.csv_format)

    return SUCCESS


def _step2(args):
    if not os.path.exists(args.prepare_csv):
        print('Step 1 not finished')
        return "Not Ready"

    print('Converting CSV to Snapshot')
    s, f = convert(args.prepare_csv, args.update_snapshot, None,
                   not args.csv_format, args.compact)
    print('Converted {0} rows\nFailed {1}'.format(s, f))

    print('Updating files from snapshot')
    snapshot = loadJson(args.update_snapshot)
    id3Proxy = ID3Proxy()
    updated, failed = updateFromSnapshot(id3Proxy, snapshot, upgrade=True)
    print('Updated {0}\nFailed {1}'.format(updated, failed))

    print('Renaming Files')
    c = renameFiles(args.download_dir, args.download_dir, id3Proxy)
    print(c)

    return SUCCESS

# -----------------------------------------------------------------------------


def process(args):
    result = "Not Implemented"

    if args.step == 1:
        return _step1(args)

    elif args.step == 2:
        return _step2(args)

    return result
