# -*- coding: utf-8 -*

from __future__ import print_function
import json
import os
import sys
import argparse
import logging
import datetime
if sys.version < '3':
    import eyed3
    from eyed3 import main, mp3, id3, core
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
import pyTagger

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class UpdateFromSnapshot:
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
        pass

    def update(self, inFileName, fieldSet=[], force=False):
        with _input(inFileName) as f:
            snapshot = json.load(f)

        formatter = pyTagger.mp3_snapshot.Formatter(fieldSet)
        if not fieldSet:
            fieldSet = formatter.columns

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
        
    def _writeSimple(self, track, tags):
        for k,v in tags.items():
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
    p.add_argument('--force', action='store_true', dest='force',
                   help='always overwrite tags')

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
    pipeline.update(args.infile, columns, args.force);
