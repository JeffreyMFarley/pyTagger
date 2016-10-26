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

p = getArgumentParser('isonom',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser('elasticsearch')],
                      description='find mp3s with similar names')
group = p.add_argument_group('Isonom Files')
group.add('--library-snapshot', default='library.json',
          help='a snapshot of the current library')
group.add('--intake-snapshot', default='mp3s.json',
          help='a snapshot of files to check')
group.add('--interview', default='interview.json',
          help='communcation with the user about the match results')

# -----------------------------------------------------------------------------

_success = "Success"
_notFinished = "Interview Not Complete"


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
        if interview.conduct():
            interview.saveState(args.interview)
            return _success if not interview.userQuit else _notFinished
        else:
            return _notFinished

    return _success
