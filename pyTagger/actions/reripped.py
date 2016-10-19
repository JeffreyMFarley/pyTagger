from __future__ import print_function
from __future__ import unicode_literals
import os
from configargparse import getArgumentParser
import pyTagger.actions.isonom as isonom
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

# -----------------------------------------------------------------------------


def process(args):
    if args.step == 1:
        match_result = isonom.process(args)
        if match_result == 'Success':
            raise AssertionError("To Be Implemted")

        return match_result

    return "Not Implemented"
