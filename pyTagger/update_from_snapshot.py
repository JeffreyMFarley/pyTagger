# -*- coding: utf-8 -*

import sys
import argparse
import logging
import binascii
if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x
from hew import Normalizer
from pyTagger.models import Snapshot
from pyTagger.utils import loadJson
from pyTagger.snapshot_converter import SnapshotConverter
from pyTagger.mp3_snapshot import Formatter, Mp3Snapshot

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class UpdateFromSnapshot(object):
    _collectionTags = ['comments', 'lyrics', 'ufid']

    _useSetAttr = {
        'bpm': 'bpm',
        'playCount': 'play_count',
    }

    _useSetAttrDate = {
        'encodingDate': 'encoding_date',
        'originalReleaseDate': 'original_release_date',
        'recordingDate': 'recording_date',
        'releaseDate': 'release_date',
        'taggingDate': 'tagging_date'
    }

    _useSetAttrString = {
        'album': 'album',
        'albumArtist': 'album_artist',
        'artist': 'artist',
        'publisher': 'publisher',
        'title': 'title'
    }

    _useSetTextFrame = {
        'compilation': 'TCMP',
        'composer': 'TCOM',
        'conductor': 'TPE3',
        'genre': 'TCON',
        'group': 'TIT1',
        'key': 'TKEY',
        'language': 'TLAN',
        'media': 'TMED',
        'remixer': 'TPE4',
        'subtitle': 'TIT3'
    }

    def __init__(self):
        self.reader = Mp3Snapshot()
        self.log = logging.getLogger(__name__)
        self.normalizer = Normalizer()

    def update(self, inFileName, fieldSet=None, upgrade=False,
               supressWarnings=True):
        if supressWarnings:
            log = logging.getLogger('eyed3')
            log.setLevel(logging.ERROR)
        self.upgrade = upgrade

        snapshot = loadJson(inFileName)

        if not fieldSet:
            fieldSet = Snapshot.extractColumns(snapshot)
        self.formatter = Formatter(fieldSet)

        for k, v in snapshot.items():
            k0 = self.normalizer.to_ascii(k)
            self.log.info("Updating '%s'", k0)
            try:
                self._updateOne(k, v)
            except AssertionError as assertEx:
                self.log.error("'%s' Assertion Error %s", k0, assertEx.args)
            except Exception:
                self.log.error("'%s' Error %s", k0, sys.exc_info()[0])

    def _updateOne(self, fileName, updates):
        track = self._loadID3(fileName)
        if not track or not track.tag:
            return

        version = self._compliance(track)
        asIs = self.reader._extractTags(track, self.formatter)
        delta = self._findDelta(updates, asIs)
        self._writeSimple(track, delta)
        self._writeCollection(track, delta)
        self._saveID3(track, version)

    def _compliance(self, track):
        version = track.tag.version
        if version[1] == 2:
            version = (2, 3, 0)

        if self.upgrade and version[1] < 3:
            version = (2, 3, 0)

        # MJMD tag was in some Jen files
        if 'MJMD' in track.tag.frame_set:
            del track.tag.frame_set['MJMD']

        if version[1] == 3:
            hasMood = track.tag.getTextFrame('TMOO')
            if hasMood:
                track.tag.setTextFrame('TMOO', None)

        return version

    def _loadID3(self, fileName):
        import eyed3
        try:
            return eyed3.load(fileName)
        except (IOError, ValueError):
            self.log.error("Could not load '%s'", fileName)
            return None

    def _saveID3(self, track, version=None):
        if not version:
            track.tag.save()
        else:
            track.tag.save(version=version)

    def _findDelta(self, a, b):
        '''Compare two file snapshots and return the difference
        ''a'' should be considered the source, like the JSON snapshot.
        ''b'' should be considered the destination, like the file
        '''
        result = {}

        # Scope the work
        ka = set(a.keys())
        kb = set(b.keys())
        notb = ka - kb
        kboth = ka & kb

        # copy over the new keys
        for k in notb:
            result[k] = a[k]

        # look for the smaller differences
        for k in kboth:
            if k not in self._collectionTags:
                if a[k] != b[k]:
                    result[k] = a[k] if a[k] else None
            elif k in ['comments', 'lyrics']:
                result[k] = self._findDeltaDLT(a[k], b[k])
            elif k == 'ufid':
                result[k] = self._findDelta(a[k], b[k])

            # if there are no members of a collection, remove the collection
            if k in self._collectionTags:
                if not result[k]:
                    del result[k]

        return result

    def _findDeltaDLT(self, a, b):
        ''' Compares collections of Description, Language, Text tuples
        '''
        result = []

        for a0 in a:
            toTest = list(
                filter(
                    lambda x, y=a0: x['lang'] == y['lang']
                    and x['description'] == y['description'], b
                )
            )
            if not toTest and a0['text']:
                result.append(a0)
            else:
                for b0 in toTest:
                    if a0['text'] != b0['text']:
                        result.append(a0)
                        break

        return result

    def _writeSimple(self, track, tags):
        import eyed3

        for k, v in tags.items():
            if k in self._collectionTags:
                continue

            assert not isinstance(v, (list, set, dict))
            text = _unicode(v) if v else None

            # pick setting the value based on a strategy
            if k in self._useSetAttr and v:
                setattr(track.tag, self._useSetAttr[k], v)
            elif k in self._useSetAttrString:
                setattr(track.tag, self._useSetAttrString[k], text)
            elif k in self._useSetAttrDate:
                date = eyed3.core.Date.parse(v) if v else None
                setattr(track.tag, self._useSetAttrDate[k], date)
            elif k in self._useSetTextFrame:
                track.tag.setTextFrame(self._useSetTextFrame[k], text),
            elif k == 'year':
                for dateAttr in self._useSetAttrDate.values():
                    setattr(track.tag, dateAttr, None)
                date = eyed3.core.Date.parse(v) if v else None
                track.tag.recording_date = date
            elif k == 'disc':
                track.tag.disc_num = (v, track.tag.disc_num[1])
            elif k == 'totalDisc':
                track.tag.disc_num = (track.tag.disc_num[0], v)
            elif k == 'totalTrack':
                track.tag.track_num = (track.tag.track_num[0], v)
            elif k == 'track':
                track.tag.track_num = (v, track.tag.track_num[1])

    def _writeCollection(self, track, tags):
        for k, v in tags.items():
            if k == 'comments':
                for v0 in v:
                    l = _unicode(v0['lang'])
                    d = _unicode(v0['description'])
                    if not v0['text']:
                        track.tag.comments.remove(d, l)
                    else:
                        track.tag.comments.set(_unicode(v0['text']), d, l)
            elif k == 'lyrics':
                for v0 in v:
                    l = _unicode(v0['lang'])
                    d = _unicode(v0['description'])
                    if not v0['text']:
                        track.tag.lyrics.remove(d, l)
                    else:
                        track.tag.lyrics.set(_unicode(v0['text']), d, l)
            elif k == 'ufid':
                for ufid, value in v.items():
                    if not value:
                        track.tag.unique_file_ids.remove(ufid)
                    else:
                        toBytes = binascii.a2b_base64(value)
                        # str(ufid) is so Python doesn't try to do ASCII
                        # conversion on the whole string
                        track.tag.unique_file_ids.set(toBytes, str(ufid))

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
    p.add_argument('--suppress', action='store_true', dest='supressWarnings',
                   help='supress eyed3 warnings')

    return p

#sys.argv = ['update_from_snapshot', '--all', '--upgrade',
#            r'c:\Users\Jeff\Music\update.json']

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    columns = []
    if args.basic:
        columns = columns + Snapshot.basic
    if args.songwriting:
        columns = columns + Snapshot.songwriting
    if args.production:
        columns = columns + Snapshot.production
    if args.distribution:
        columns = columns + Snapshot.distribution
    if args.library:
        columns = columns + Snapshot.library
    if args.all:
        columns = Snapshot.orderedAllColumns()
        for x in Snapshot.mp3Info:
            columns.remove(x)

    if not columns:
        columns = Snapshot.basic

    pipeline = UpdateFromSnapshot()
    pipeline.log.setLevel(logging.INFO)
    pipeline.update(args.infile, columns, args.upgrade, args.supressWarnings)
