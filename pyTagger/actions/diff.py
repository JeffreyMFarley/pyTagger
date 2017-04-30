from __future__ import unicode_literals
from configargparse import getArgumentParser
from pyTagger.models import Snapshot
from pyTagger.operations.two_tags import difference
from pyTagger.utils import defaultConfigFiles, loadJson
from pyTagger.utils import saveJsonIncrementalDict

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('diff',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser()],
                      description='find the differences between two snapshots')
group = p.add_argument_group('Files')
group.add('left', help='the first snapshot to compare')
group.add('right', help='the second snapshot to compare')
group.add('outfile', help='the snapshot that will hold the results')
group = p.add_argument_group('Options')
group.add('--compact', action='store_true', dest='compact',
          help='output the JSON in a compact format')
group.add('--include-nulls', action='store_true',
          help='include nulls in the difference')
group.add('--match-on', choices=['id', 'path'], default='path',
          help='select which field should be used for comparison')
group.add('--write-empty', action='store_true',
          help='output empty differences')


# type: same, left-only, right-only, diff-left, diff-right

# -----------------------------------------------------------------------------

def _filter(tags):
    for k in Snapshot.mp3Info:
        if k in tags:
            del tags[k]
    if 'length' in tags:
        del tags['length']
    return tags


def _removeNulls(tags):
    keys = list(tags.keys())
    for k in keys:
        if not tags[k]:
            del tags[k]
    return tags


def _keyOnId(tags):
    t = {}
    for k, v in tags.items():
        if 'id' in v:
            v['path'] = k
            t[v['id']] = v
    return t


def process(args):
    a = loadJson(args.left)
    b = loadJson(args.right)

    # Scope the work
    if args.match_on == 'id':
        a = _keyOnId(a)
        b = _keyOnId(b)

    ka = set(a.keys())
    kb = set(b.keys())
    kboth = ka & kb

    output = saveJsonIncrementalDict(args.outfile, args.compact)

    extracted = next(output)

    for k in sorted(kboth):
        tags = difference(_filter(a[k]), _filter(b[k]))
        if not args.include_nulls:
            tags = _removeNulls(tags)

        if tags or args.write_empty:
            pair = (k.replace('\\', '\\\\'), tags)
            extracted = output.send(pair)

    output.close()

    return '{} tags processed'.format(extracted)
