# -*- coding: utf-8 -*

from __future__ import print_function
import json
import os
import sys
import argparse
import logging
import datetime
import binascii
if sys.version < '3':
    import eyed3
    from eyed3 import main, mp3, id3, core
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
import pyTagger
from pyTagger.mp3_snapshot import Formatter

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class UpdateFromSnapshot:
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
        self.reader = pyTagger.Mp3Snapshot()

    def update(self, inFileName, fieldSet=[], upgrade=False, supressWarnings=True):
        if supressWarnings:
            log = logging.getLogger('eyed3')
            log.setLevel(logging.ERROR)
        self.upgrade = upgrade

        with _input(inFileName) as f:
            snapshot = json.load(f)

        if not fieldSet:
            friend = pyTagger.SnapshotConverter()
            fieldSet = friend._extractColumns(snapshot)
        self.formatter = pyTagger.mp3_snapshot.Formatter(fieldSet)

        for k,v in snapshot.items():
            print("Updating", self.formatter.normalizeToAscii(k))
            try:
                self._updateOne(k,v)
            except:
                print('Error with', self.formatter.normalizeToAscii(k))

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

        if version[1] == 3:
            hasMood = track.tag.getTextFrame('TMOO')
            if hasMood:
                track.tag.setTextFrame('TMOO', None)

        return version

    def _loadID3(self, fileName):
        try:
            return eyed3.load(fileName)
        except (IOError, ValueError):
            print('Error with ID3 Load', fileName, file=sys.stderr)
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

        return result;

    def _findDeltaDLT(self, a, b):
        ''' Compares collections of Description, Language, Text tuples
        '''
        result = []

        for a0 in a:
            toTest = list(filter(lambda x: x['lang'] == a0['lang'] and x['description'] == a0['description'], b))
            if not toTest and a0['text']:
                result.append(a0)
            else:
                for b0 in toTest:
                    if a0['text'] != b0['text']:
                        result.append(a0)
                        break

        return result

    def _writeSimple(self, track, tags):
        for k,v in tags.items():
            if k in self._collectionTags:
                continue

            assert not isinstance(v, (list, set, dict))
            text = unicode(v) if v else None

            # pick setting the value based on a strategy
            if k in self._useSetAttr:
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
        for k,v in tags.items():
            if k == 'comments':
                for v0 in v:
                    l = unicode(v0['lang'])
                    d = unicode(v0['description'])
                    if not v0['text']:
                        track.tag.comments.remove(d, l)
                    else:
                        track.tag.comments.set(unicode(v0['text']), d, l)
            elif k == 'lyrics':
                for v0 in v:
                    l = unicode(v0['lang'])
                    d = unicode(v0['description'])
                    if not v0['text']:
                        track.tag.lyrics.remove(d, l)
                    else:
                        track.tag.lyrics.set(unicode(v0['text']), d, l)
            elif k == 'ufid':
                for id, value in v.items():
                    if not value:
                        track.tag.unique_file_ids.remove(id)
                    else:
                        toBytes = binascii.a2b_base64(value)
                        # str(id) is so Python doesn't try to do ASCII conversion on the whole string
                        track.tag.unique_file_ids.set(toBytes, str(id))

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Update tag values in MP3s from a snapshot'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('infile', metavar='infile', help='the snapshot to process')
    p.add_argument('-b', '--basic', action='store_true', dest='basic',
                   help='Only update: ' + ' '.join(Formatter.basic))
    p.add_argument('-s', '--songwriting', action='store_true',
                   dest='songwriting',
                   help='Only update: ' + ' '.join(Formatter.songwriting))
    p.add_argument('-p', '--production', action='store_true',
                   dest='production',
                   help='Only update: ' + ' '.join(Formatter.production))
    p.add_argument('-d', '--distribution', action='store_true',
                   dest='distribution',
                   help='Only update: ' + ' '.join(Formatter.distribution))
    p.add_argument('-l', '--library', action='store_true', dest='library',
                   help='Only update: ' + ' '.join(Formatter.library))
    p.add_argument('-a', '--all', action='store_true', dest='all',
                   help='include all supported fields')
    p.add_argument('--upgrade', action='store_true', dest='upgrade',
                   help='Upgrade the tags to be at least 2.3')
    p.add_argument('--suppress', action='store_true', dest='supressWarnings',
                   help='supress eyed3 warnings')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    columns = []
    if args.basic:
        columns = columns + Formatter.basic
    if args.songwriting:
        columns = columns + Formatter.songwriting
    if args.production:
        columns = columns + Formatter.production
    if args.distribution:
        columns = columns + Formatter.distribution
    if args.library:
        columns = columns + Formatter.library
    if args.all:
        columns = Formatter.columns - Formatter.mp3Info

    if not columns:
        columns = Formatter.basic

    pipeline = UpdateFromSnapshot()
    pipeline.update(args.infile, columns, args.upgrade, args.supressWarnings);
