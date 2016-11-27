from __future__ import print_function
from __future__ import unicode_literals
import io
import os
import pyTagger.actions.isonom as isonom
from configargparse import getArgumentParser
from pyTagger.operations.from_csv import convert
from pyTagger.operations.on_directory import extractImagesFrom
from pyTagger.operations.on_mp3 import updateFromSnapshot
from pyTagger.operations.to_csv import writeCsv
from pyTagger.operations.two_tags import union
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import loadJson, generateUfid
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('reripped',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser('isonom')],
                      description='process re-ripped files and merge into '
                      'house library')
p.add('step', choices=[1, 2, 3], type=int, default=1,
      help='which step to execute')
group = p.add_argument_group('Step 1')
group.add('--goal-csv', default='goal.csv',
          help='a CSV version of the goal snapshot')
group = p.add_argument_group('Step 2')
group.add('--goal-snapshot', default='goal.json',
          help='a snapshot of what the mp3s should look like')
group.add('--images-dir', default=os.path.join(os.getcwd(), 'images'),
          help='the directory where images should be extracted')
group.add('--to-delete', default='to-delete.txt',
          help='the file that lists the MP3s to be deleted')
group.add('--to-extract', default='to-extract.txt',
          help='the file that lists the MP3s to extract images from')
group.add('--to-move', default='to-move.txt',
          help='the file that lists the MP3s to be moved')
group.add('--to-update', default='to-update.txt',
          help='the file that lists the MP3s to be overwritten')

# -----------------------------------------------------------------------------

SUCCESS = "Success"


def _mergeAll(args):
    rows = loadJson(args.interview)
    merged = {}

    for row in rows:
        c = union(row['newTags'], row['oldTags'])

        if row['status'] == 'manual':
            ufid = generateUfid()
            c['id'] = ufid
            c['ufid'] = {'DJTagger': ufid}

        merged[row['newPath']] = c

    return merged


def _step1(args):
    if os.path.exists(args.goal_csv):
        print('Using existing goals file')
        return SUCCESS

    result = isonom.process(args)
    if result == 'Success':
        print('Creating ', args.goal_csv)
        merged = _mergeAll(args)
        writeCsv(merged, args.goal_csv)

    return result

# -----------------------------------------------------------------------------


def _writeText(lines, fileName):
    with io.open(fileName, 'w', encoding='utf-8') as f:
        for i, l in enumerate(lines):
            if i > 0:
                f.write('\n')
            f.write(l)


def _buildDeletes(interview, snapshot):
    return [x['newPath'] for x in interview if x['newPath'] not in snapshot]


def _buildMoves(interview):
    return [x['newPath'] for x in interview if x['status'] == 'manual']


def _buildUpdates(interview):
    return [
        (x['newPath'], x['oldPath'])
        for x in interview
        if x['status'] == 'ready'
    ]


def _step2(args):
    if not os.path.exists(args.goal_csv):
        print('Step 1 not finished')
        return "Not Ready"

    if not os.path.exists(args.goal_snapshot):
        convert(args.goal_csv, args.goal_snapshot)
    else:
        print('Using existing goals file')

    interview = loadJson(args.interview)
    snapshot = loadJson(args.goal_snapshot)

    deletes = _buildDeletes(interview, snapshot)
    _writeText(deletes, args.to_delete)

    # Remove the deletes from the interview
    interview = [x for x in interview if x['newPath'] not in deletes]

    moves = _buildMoves(interview)
    _writeText(moves, args.to_move)

    updates = _buildUpdates(interview)
    pairs = [a + ', ' + b for a, b in updates]
    _writeText(pairs, args.to_update)

    images = [b for _, b in updates]
    _writeText(images, args.to_extract)

    id3Proxy = ID3Proxy()
    updated, failed = updateFromSnapshot(id3Proxy, snapshot, upgrade=True)
    counter = extractImagesFrom(args.to_extract, args.images_dir, id3Proxy)

    print('Updated {0}\nFailed {1}'.format(updated, failed))
    print('Images', counter)

    return SUCCESS

# -----------------------------------------------------------------------------


def process(args):
    result = "Not Implemented"

    if args.step == 1:
        return _step1(args)

    elif args.step == 2:
        return _step2(args)

    return result
