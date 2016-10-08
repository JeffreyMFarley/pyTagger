from configargparse import getArgumentParser
from pyTagger.proxies.es import Client
from pyTagger.utils import loadJson
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('upload',
                      default_config_files=defaultConfigFiles,
                      parents=[getArgumentParser('elasticsearch')],
                      description='load a snapshot into Elasticsearch')
group = p.add_argument_group('Files')
group.add('--library-snapshot', default='mp3s.json',
          help='the file to upload')
group = p.add_argument_group('Other Options')
group.add('--append', action='store_true', help='append records to the index')
group.add('--reload', action='store_true',
          help='clear the index and repopulate')

# -----------------------------------------------------------------------------


def uploadToElasticsearch(args):
    snapshot = loadJson(args.library_snapshot)

    cli = Client()
    exists = cli.exists()

    if exists and args.reload:
        cli.delete()

    elif exists and not args.append:
        raise ValueError('Upload already exists!  You can correct this by:\n\n'
                         '--append    Append the records to the index\n'
                         '--reload    Clear the index and repopulate\n'
                         '--es-index  Specify a different index')

    l, f = cli.load(snapshot)
    return 'Loaded {0} records\nFailed {1}'.format(l, f)
