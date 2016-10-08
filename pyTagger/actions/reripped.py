from __future__ import unicode_literals
from configargparse import getArgumentParser
from pyTagger.actions.upload import uploadToElasticsearch
from pyTagger.operations.find_duplicates import findIsonoms
from pyTagger.proxies.es import Client
from pyTagger.utils import loadJson
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
group.add('--reripped-snapshot', default='mp3s.json',
          help='the newly ripped files')
group.add('--step1-output', default='isonoms.json',
          help='the output from step one')

# -----------------------------------------------------------------------------


def _step0(args):
    uploadToElasticsearch(args)


def _step1(args, client):
    import io
    import json

    snapshot = loadJson(args.reripped_snapshot)
    sep = '\n'
    rows = 0

    # TODO: http://www.scipy-lectures.org/advanced/advanced_python/
    # bidirectional-communication
    with io.open(args.step1_output, 'w', encoding='utf-8') as f:
        f.write('[')
        for row in findIsonoms(client, snapshot):
            rows += 1
            f.write(sep)
            f.write(unicode(json.dumps(row.__dict__, ensure_ascii=False)))
            sep = ',\n'
        f.write('\n]')

    return "Step 1: {1} tracks produced {0} rows".format(rows, len(snapshot))


def process(args):
    if args.step == 1:
        cli = Client()

        if not cli.exists():
            _step0(args)

        return _step1(args, cli)

    return "Not Implemented"
