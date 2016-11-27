from __future__ import unicode_literals
import os
from configargparse import getArgumentParser
from pyTagger.operations.on_directory import extractImages, extractImagesFrom
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('images',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser()],
                      description='extract images from MP3s')
group = p.add_argument_group('Files')
group.add('path',
          help='the path to scan or file to use')
group.add('outputDir',
          help='the directory where the extracted images are stored')

# -----------------------------------------------------------------------------


def process(args):
    if os.path.isfile(args.path):
        return extractImagesFrom(args.path, args.outputDir, ID3Proxy())
    elif os.path.isdir(args.path):
        return extractImages(args.path, args.outputDir, ID3Proxy())
    else:
        raise ValueError(args.path + ' is not a file or directory')
