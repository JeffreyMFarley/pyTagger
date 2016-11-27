from __future__ import print_function
from __future__ import unicode_literals
import os
import pyTagger.actions.isonom as isonom
from configargparse import getArgumentParser
from pyTagger.operations.to_csv import writeCsv
from pyTagger.operations.two_tags import union
from pyTagger.utils import loadJson, saveJsonIncrementalDict, generateUfid
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
group.add('--goal-snapshot', default='goal.json',
          help='a snapshot of what the mp3s should look like')
group.add('--goal-csv', default='goal.csv',
          help='a CSV version of the goal snapshot')
group = p.add_argument_group('Step 3')
group.add('--images-dir', default=os.getcwd() + '/images',
          help='the directory where images should be extracted')

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


def process(args):
    result = "Not Implemented"

    if args.step == 1:
        return _step1(args)

    return result
