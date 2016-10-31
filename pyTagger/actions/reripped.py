from __future__ import print_function
from __future__ import unicode_literals
import copy
import os
from configargparse import getArgumentParser
import pyTagger.actions.isonom as isonom
from pyTagger.models import Snapshot
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


def _mergeOne(newer, older):
    c = {}
    if not older:
        c = copy.deepcopy(newer)
        for k in Snapshot.mp3Info:
            if k in c:
                del c[k]

    else:
        keys = set(newer.keys()) | set(older.keys())
        keys = keys - set(Snapshot.mp3Info)
        for k in keys:
            if k in older and k in newer:
                if older[k]:
                    c[k] = older[k]
                else:
                    c[k] = newer[k]
            elif k in older:
                c[k] = older[k]
            else:
                c[k] = newer[k]

    if 'id' not in c:
        ufid = generateUfid()
        c['id'] = ufid
        c['ufid'] = {'DJTagger': ufid}

    return c


def _mergeAll(args):
    rows = loadJson(args.interview)

    output = saveJsonIncrementalDict(args.goal_snapshot, False)
    extracted = next(output)

    for row in rows:
        c = _mergeOne(row['newTags'], row['oldTags'])
        pair = (row['newPath'], c)
        extracted = output.send(pair)

    output.close()

    return extracted


def process(args):
    if args.step == 1:
        match_result = isonom.process(args)
        if match_result == 'Success':
            _mergeAll(args)

        return match_result

    return "Not Implemented"
