from __future__ import print_function
import logging
import os
import sys
import traceback
import pyTagger.actions.convert_csv as convert_csv
import pyTagger.actions.diff as diff
import pyTagger.actions.export as export
import pyTagger.actions.images as images
import pyTagger.actions.isonom as isonom
import pyTagger.actions.prepare as prepare
import pyTagger.actions.rename as rename
import pyTagger.actions.reripped as reripped
import pyTagger.actions.scan as scan
import pyTagger.actions.tag_album as tag_album
import pyTagger.actions.update as update
import pyTagger.actions.upload as upload
from pyTagger.utils import rootParser as parser
from configargparse import getArgumentParser

try:
    from Tkinter import Tk
except ImportError:
    from tkinter import Tk


modules = {
    'convert-csv': convert_csv.process,
    'diff': diff.process,
    'images': images.process,
    'isonom': isonom.process,
    'prepare': prepare.process,
    'rename': rename.process,
    'reripped': reripped.process,
    'scan': scan.process,
    'tag-album': tag_album.process,
    'to-csv': export.process,
    'update': update.process,
    'upload': upload.uploadToElasticsearch
}

subs = parser.add_subparsers(help='available commands')
for m in sorted(modules):
    p = getArgumentParser(m)
    sub = subs.add_parser(m, help=p.description)
    del subs._name_parser_map[m]
    subs._name_parser_map[m] = p

if __name__ == "__main__":
    Tk().withdraw()
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
        except Exception:
            for fncall in traceback.format_exception(*sys.exc_info()):
                print(fncall)

    else:
        args = parser.parse()
        parser.print_values()
