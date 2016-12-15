from __future__ import unicode_literals
from configargparse import getArgumentParser
from pyTagger.operations.on_directory import renameFiles
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('rename',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser()],
                      description='apply naming standards to MP3s')
group = p.add_argument_group('Files')
group.add('path',
          help='the path to scan')
group.add('destDir',
          help='the directory where the files should be moved')

# -----------------------------------------------------------------------------


def process(args):
    return renameFiles(args.path, args.destDir, ID3Proxy())
