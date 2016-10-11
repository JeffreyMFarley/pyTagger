from __future__ import unicode_literals
from configargparse import getArgumentParser
from pyTagger.actions.upload import uploadToElasticsearch
from pyTagger.operations.find_duplicates import findIsonoms
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
group.add('--step1-output', default='isonoms.json',
          help='the output from step one')

# -----------------------------------------------------------------------------


def _step0(args):
    uploadToElasticsearch(args)


def _step1(args, client):
    snapshot = loadJson(args.intake_snapshot)

    output = saveJsonIncrementalArray(args.step1_output)
    rows = output.next()

    for row in findIsonoms(client, snapshot):
        rows = output.send(row.__dict__)

    output.close()

    return "Step 1: {1} track(s) produced {0} rows".format(rows, len(snapshot))


def process(args):
    if args.step == 1:
        cli = Client()

        if not cli.exists():
            _step0(args)

        return _step1(args, cli)

    return "Not Implemented"
