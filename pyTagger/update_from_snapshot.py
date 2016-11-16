# -*- coding: utf-8 -*

import sys
import argparse
import logging
import binascii
from hew import Normalizer
from pyTagger.models import Snapshot
from pyTagger.operations.two_tags import difference
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import loadJson

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class UpdateFromSnapshot(object):
    def __init__(self):
        self.id3Proxy = ID3Proxy()
        self.log = logging.getLogger(__name__)
        self.normalizer = Normalizer()

    def update(self, inFileName, fieldSet=None, upgrade=False):
        self.upgrade = upgrade

        snapshot = loadJson(inFileName)

        if not fieldSet:
            fieldSet = Snapshot.columnsFromSnapshot(snapshot)
        self.id3Proxy = ID3Proxy(fieldSet)

        for k, v in snapshot.items():
            k0 = self.normalizer.to_ascii(k)
            self.log.info("Updating '%s'", k0)
            try:
                self.updateOne(k, v)
            except AssertionError as assertEx:
                self.log.error("'%s' Assertion Error %s", k0, assertEx.args)
            except Exception:
                self.log.error("'%s' Error %s", k0, sys.exc_info()[0])

    def updateOne(self, fileName, updates):
        track = self.id3Proxy.loadID3(fileName)
        if not track or not track.tag:
            return

        asIs = self.id3Proxy.extractTagsFromTrack(track)
        delta = difference(updates, asIs)

        self.id3Proxy.saveID3(track, delta, self.upgrade)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Update tag values in MP3s from a snapshot'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('infile', metavar='infile', help='the snapshot to process')
    p.add_argument('-b', '--basic', action='store_true', dest='basic',
                   help='Only update: ' + ' '.join(Snapshot.basic))
    p.add_argument('-s', '--songwriting', action='store_true',
                   dest='songwriting',
                   help='Only update: ' + ' '.join(Snapshot.songwriting))
    p.add_argument('-p', '--production', action='store_true',
                   dest='production',
                   help='Only update: ' + ' '.join(Snapshot.production))
    p.add_argument('-d', '--distribution', action='store_true',
                   dest='distribution',
                   help='Only update: ' + ' '.join(Snapshot.distribution))
    p.add_argument('-l', '--library', action='store_true', dest='library',
                   help='Only update: ' + ' '.join(Snapshot.library))
    p.add_argument('-a', '--all', action='store_true', dest='all',
                   help='include all supported fields')
    p.add_argument('--upgrade', action='store_true', dest='upgrade',
                   help='Upgrade the tags to be at least 2.3')

    return p

#sys.argv = ['update_from_snapshot', '--all', '--upgrade',
#            r'c:\Users\Jeff\Music\update.json']

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()
    columns = Snapshot.columnsFromArgs(args)

    pipeline = UpdateFromSnapshot()
    pipeline.log.setLevel(logging.INFO)
    pipeline.update(args.infile, columns, args.upgrade)
