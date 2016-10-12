from __future__ import print_function
from __future__ import unicode_literals
import os
from configargparse import getArgumentParser
from pyTagger.actions.upload import uploadToElasticsearch
from pyTagger.operations.find_duplicates import findIsonoms
from pyTagger.operations.interview import Interview
from pyTagger.proxies.es import Client
from pyTagger.utils import loadJson, saveJsonIncrementalArray
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('reripped',
                      default_config_files=defaultConfigFiles,
                      parents=[getArgumentParser('elasticsearch')],
                      description='process re-ripped files and merge into '
                      'house library')
p.add('step', choices=[1, 2, 3], type=int, default=1,
      help='which step to execute')
group = p.add_argument_group('Files')
group.add('--library-snapshot', default='library.json',
          help='a snapshot of the current library')
group.add('--intake-snapshot', default='mp3s.json',
          help='the newly ripped files')
group.add('--interview', default='interview.json',
          help='communcation with the user about the match results')

# -----------------------------------------------------------------------------


def _buildIndex(args):
    uploadToElasticsearch(args)


def _findIsonoms(args, client):
    snapshot = loadJson(args.intake_snapshot)

    output = saveJsonIncrementalArray(args.interview)
    rows = next(output)

    for row in findIsonoms(client, snapshot):
        rows = output.send(row._asdict())

    output.close()

    return "{1} track(s) produced {0} rows".format(rows, len(snapshot))


def process(args):
    if args.step == 1:
        cli = Client()

        if not cli.exists():
            print('Building Index')
            _buildIndex(args)
        else:
            print('Index Already Built')

        if not os.path.exists(args.interview):
            print('Finding Isonoms')
            print(_findIsonoms(args, cli))
        else:
            print('Using existing isonoms file')

        rows = loadJson(args.interview)
        interview = Interview(rows)

        if not interview.isComplete():
            interview.conduct()
            interview.saveState(args.interview)
        else:
            raise AssertionError

        return "Success"

    return "Not Implemented"
