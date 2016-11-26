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
          help='the path to scan')
group.add('outputDir',
          help='the directory where the extracted images are stored')
group.add('--use-file',
          help='a text file with the list of files to extract')

# -----------------------------------------------------------------------------


def process(args):
    if args.use_file:
        return extractImagesFrom(args.use_file, args.outputDir, ID3Proxy())
    else:
        return extractImages(args.path, args.outputDir, ID3Proxy())
