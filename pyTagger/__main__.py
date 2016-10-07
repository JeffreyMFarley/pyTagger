import sys
from pyTagger.utils import rootParser as parser
from configargparse import getArgumentParser
from pyTagger.proxies.echonest import EchoNestProxy
from pyTagger.proxies.es import Client

actions = {
    'to-csv': 'export snapshot to CSV',
    'images': 'extract images from MP3s',
    'convert-csv': 'convert CSV to snapshot',
    'match': 'find similarily named MP3s',
    'prepare': 'groom MP3s before adding to house library',
    'rename': 'apply naming standards to MP3s',
    'scan': 'create a snapshot from directories of MP3s',
    'update': 'update ID3 fields from a snapshot',
    'upload': 'load a snapshot into Elasticsearch'
}

subs = parser.add_subparsers(help='available commands')
for k in sorted(actions):
    sub = subs.add_parser(k, help=actions[k])

modules = ['echonest', 'elasticsearch']

for m in modules:
    p = getArgumentParser(m)
    sub = subs.add_parser(m, help=p.description)
    del subs._name_parser_map[m]
    subs._name_parser_map[m] = p

if __name__ == "__main__":
    import configargparse
    if len(sys.argv) < 2:
        parser.print_help()
        exit(2)

    action = sys.argv[1].lower()
    if action in modules:
        sys.argv.pop(1)
        p = getArgumentParser(action)
        args = p.parse()
        p.print_values()

    else:
        args = parser.parse()
        parser.print_values()
