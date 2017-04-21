from __future__ import print_function
from __future__ import unicode_literals
import io
import logging
import os
import pyTagger.actions.isonom as isonom
import pyTagger.actions.tag_album as tag_album
from configargparse import getArgumentParser
from pyTagger.operations.ask import askMultipleChoice
from pyTagger.operations.from_csv import convert
from pyTagger.operations.on_directory import extractImages, deleteFiles
from pyTagger.operations.on_directory import renameFiles, replaceFiles
from pyTagger.operations.on_directory import deleteEmptyDirectories
from pyTagger.operations.on_mp3 import updateFromSnapshot
from pyTagger.operations.to_csv import writeCsv
from pyTagger.operations.two_tags import union
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import loadJson, saveJson, generateUfid
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('reripped',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[
                          getArgumentParser('isonom'),
                      ],
                      description='process re-ripped files and merge into '
                      'house library')
p.add('step', choices=[1, 2, 3], type=int, default=1,
      help='which step to execute')
group = p.add_argument_group('tag-album')
group.add('--tag-album-file', default='albums.json',
          help='a snapshot of the mp3s to edit')
group.add('--tag-album-logging',
          choices=[logging.NOTSET, logging.INFO, logging.WARNING,
                   logging.ERROR],
          default=logging.WARNING, type=int,
          help='how verbose the process should be')
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
group = p.add_argument_group('Step 3')
group.add('--library-dir', default=os.path.join(os.getcwd(), 'Music'),
          help='the directory where the managed MP3s are located')
group.add('--intake-dir', default=os.path.join(os.getcwd(), 'Add To Library'),
          help='the directory where the incoming MP3s are located')
group.add('--cleanup', action='store_true',
          help='clean up files if successful')
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


def _tagAlbum(args):
    result = tag_album.process(args)
    if result == 'Success':
        snapshot = loadJson(args.tag_album_file)
        print('Creating ', args.goal_csv)
        writeCsv(snapshot, args.goal_csv)
    return result


def _step1(args):
    if os.path.exists(args.goal_csv):
        print('Using existing goals file')
        return SUCCESS

    if os.path.exists(args.tag_album_file):
        return _tagAlbum(args)

    result = isonom.process(args)
    if result == 'Success':
        print('Creating ', args.tag_album_file)
        merged = _mergeAll(args)
        saveJson(args.tag_album_file, merged)
        return _tagAlbum(args)

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

    l = _buildDeletes(interview, snapshot)
    _writeText(l, args.to_delete)

    # Remove the deletes from the interview
    interview = [x for x in interview if x['newPath'] not in l]

    l = _buildMoves(interview)
    _writeText(l, args.to_move)

    updates = _buildUpdates(interview)
    pairs = [a + '\t' + b for a, b in updates]
    _writeText(pairs, args.to_update)

    l = [b for _, b in updates]
    _writeText(l, args.to_extract)

    id3Proxy = ID3Proxy()
    updated, failed = updateFromSnapshot(id3Proxy, snapshot, upgrade=True)
    counter = extractImages(args.to_extract, args.images_dir, id3Proxy)

    print('Updated {0}\nFailed {1}'.format(updated, failed))
    print('Images', counter)

    return SUCCESS

# -----------------------------------------------------------------------------


def _image_ask():
    choices = {'Y': 'Yes', 'N': 'No'}
    a = askMultipleChoice(None, 'Have the images been copied?', choices, False)
    return a == 'Y'


def _deleteFiles(args):
    if not os.path.exists(args.to_delete):
        return True

    s, f = deleteFiles(args.to_delete)
    print('Deleted {0}, Errors {1}'.format(s, f))

    passed = f == 0

    if args.cleanup and passed:
        os.remove(args.to_delete)

    return passed


def _moveFiles(args):
    if not os.path.exists(args.to_move):
        return True

    reader = ID3Proxy()
    c = renameFiles(args.to_move, args.library_dir, reader)
    print('Moved', c)

    passed = c['moved'] == sum(c.values())

    if args.cleanup and passed:
        os.remove(args.to_move)

    return passed


def _replaceFiles(args):
    if not os.path.exists(args.to_update):
        return True

    c = replaceFiles(args.to_update)

    print('Replaced', c)

    passed = c['replaced'] == sum(c.values())

    if args.cleanup and passed:
        os.remove(args.to_update)

    return passed


def _step3(args):
    if not _image_ask():
        return 'Not Ready'

    p0 = _deleteFiles(args)
    p1 = _moveFiles(args)
    p2 = _replaceFiles(args)

    passed = p0 and p1 and p2

    if args.cleanup:
        d, s = deleteEmptyDirectories(args.intake_dir)
        print('Removed {0} directories, skipped {1}'.format(d, s))

        if passed:
            print('Removing goals files')
            os.remove(args.goal_csv)
            os.remove(args.goal_snapshot)
            os.remove(args.interview)

    return SUCCESS if passed else 'Not Completed'

# -----------------------------------------------------------------------------


def process(args):
    result = "Not Implemented"

    if args.step == 1:
        return _step1(args)

    elif args.step == 2:
        return _step2(args)

    elif args.step == 3:
        return _step3(args)

    return result
