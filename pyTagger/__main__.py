from __future__ import print_function
import logging
import os
import sys
import pyTagger.actions.convert_csv as convert_csv
import pyTagger.actions.export as export
import pyTagger.actions.images as images
import pyTagger.actions.isonom as isonom
import pyTagger.actions.rename as rename
import pyTagger.actions.reripped as reripped
import pyTagger.actions.scan as scan
import pyTagger.actions.update as update
import pyTagger.actions.upload as upload
from pyTagger.utils import rootParser as parser
from configargparse import getArgumentParser

actions = {
    'prepare': 'groom MP3s before adding to house library',
}

subs = parser.add_subparsers(help='available commands')
for k in sorted(actions):
    sub = subs.add_parser(k, help=actions[k])

modules = {
    'convert-csv': convert_csv.process,
    'images': images.process,
    'isonom': isonom.process,
    'rename': rename.process,
    'reripped': reripped.process,
    'scan': scan.process,
    'to-csv': export.process,
    'update': update.process,
    'upload': upload.uploadToElasticsearch
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
