from __future__ import print_function
import logging
import os
import sys
from pyTagger.actions.reripped import process as rerippedProcess
from pyTagger.actions.upload import uploadToElasticsearch
from pyTagger.utils import rootParser as parser
from configargparse import getArgumentParser

actions = {
    'to-csv': 'export snapshot to CSV',
    'images': 'extract images from MP3s',
    'convert-csv': 'convert CSV to snapshot',
    'match': 'find similarily named MP3s',
    'prepare': 'groom MP3s before adding to house library',
    'rename': 'apply naming standards to MP3s',
    'scan': 'create a snapshot from directories of MP3s',
    'update': 'update ID3 fields from a snapshot'
}

subs = parser.add_subparsers(help='available commands')
for k in sorted(actions):
    sub = subs.add_parser(k, help=actions[k])

modules = {
    'reripped': rerippedProcess,
    'upload': uploadToElasticsearch
}

for m in sorted(modules):
    p = getArgumentParser(m)
    sub = subs.add_parser(m, help=p.description)
    del subs._name_parser_map[m]
    subs._name_parser_map[m] = p

if __name__ == "__main__":
    logging.basicConfig()
    os.system('cls' if os.name == 'nt' else 'clear')

    if len(sys.argv) < 2:
        parser.print_help()
        exit(2)

    action = sys.argv[1].lower()
    if action in modules:
        sys.argv.pop(1)
        p = getArgumentParser(action)
        args = p.parse()
        print('=' * 31, ' Configuration ', '=' * 32)
        p.print_values()
        print('=' * 80)
        try:
            print(modules[action](args))
        except ValueError as ve:
            print(ve)
        except IOError as ioe:
            print(ioe)

    elif action in actions:
        print(action, 'is not yet implemented')

    else:
        args = parser.parse()
        parser.print_values()