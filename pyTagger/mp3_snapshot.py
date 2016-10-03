# -*- coding: utf-8 -*

import json
import os
import sys
import argparse
import binascii
import hashlib
import logging
if sys.version < '3':  # pragma: no cover
    import codecs
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf-8')
else:  # pragma: no cover
    _output = lambda fileName: open(fileName, 'w', encoding='utf-8')
from pyTagger.io import walk

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class Formatter(object):
    _projectionEyed3 = {
        'album': lambda x: x.tag.album,
        'albumArtist': lambda x: x.tag.album_artist,
        'artist': lambda x: x.tag.artist,
        'bitRate':
        lambda x: x.info.bit_rate[1] if x.info is not None else None,
        'bpm': lambda x: x.tag.bpm,
        'comments': lambda x: [{'lang': y.lang,
                                'text': y.text,
                                'description': y.description}
                               for y in x.tag.comments],
        'compilation': lambda x: x.tag.getTextFrame('TCMP'),
        'composer': lambda x: x.tag.getTextFrame('TCOM'),
        'conductor': lambda x: x.tag.getTextFrame('TPE3'),
        'disc': lambda x: x.tag.disc_num[0],
        'encodingDate': lambda x: Formatter.extractDate(x.tag.encoding_date),
        'fileHash': lambda x: '',
        'genre': lambda x: x.tag.genre.name if x.tag.genre else '',
        'group': lambda x: x.tag.getTextFrame('TIT1'),
        'id': lambda x: Formatter.extractTaggerId(x),
        'key': lambda x: x.tag.getTextFrame('TKEY'),
        'language': lambda x: x.tag.getTextFrame('TLAN'),
        'length': lambda x: x.info.time_secs if x.info else '',
        'lyrics': lambda x: [{'lang': y.lang,
                              'text': y.text,
                              'description': y.description}
                             for y in x.tag.lyrics],
        'media': lambda x: x.tag.getTextFrame('TMED'),
        'originalReleaseDate':
        lambda x: Formatter.extractDate(x.tag.original_release_date),
        'playCount': lambda x: x.tag.play_count,
        'publisher': lambda x: x.tag.publisher,
        'recordingDate': lambda x: Formatter.extractDate(x.tag.recording_date),
        'releaseDate': lambda x: Formatter.extractDate(x.tag.release_date),
        'remixer': lambda x: x.tag.getTextFrame('TPE4'),
        'subtitle': lambda x: x.tag.getTextFrame('TIT3'),
        'taggingDate': lambda x: Formatter.extractDate(x.tag.tagging_date),
        'title': lambda x: x.tag.title,
        'totalDisc': lambda x: x.tag.disc_num[1],
        'totalTrack': lambda x: x.tag.track_num[1],
        'track': lambda x: x.tag.track_num[0],
        'ufid': lambda x: Formatter.extractFileIds(x),
        'vbr': lambda x: x.info.bit_rate[0] if x.info is not None else None,
        'version': lambda x: '.'.join([str(y) for y in x.tag.version]),
        'year': lambda x: Formatter.extractDate(x.tag.getBestDate()),
    }
    columns = list(_projectionEyed3.keys())

    basic = ['title', 'track', 'totalTrack', 'artist',
             'albumArtist', 'album', 'length']
    songwriting = ['bpm', 'composer', 'key', 'lyrics', 'language']
    production = ['year', 'releaseDate', 'originalReleaseDate',
                  'recordingDate', 'conductor', 'remixer', 'publisher']
    distribution = ['media', 'disc', 'totalDisc']
    library = ['genre', 'id', 'ufid', 'compilation', 'comments', 'playCount',
               'group', 'subtitle', 'encodingDate', 'taggingDate']
    mp3Info = ['bitRate', 'vbr', 'fileHash', 'version']

    def __init__(self, fieldSet=None):
        self.fieldSet = self.columns if fieldSet is None else fieldSet
        self.normalizer = None

    def format(self, obj):
        from eyed3 import mp3
        if isinstance(obj, mp3.Mp3AudioFile) and obj.tag:
            # Python 2.6 does not like dictionary comprehensions
            row = {}
            for k in self.fieldSet:
                row[k] = self._projectionEyed3[k](obj)
            return row
        return {}

    def normalizeToAscii(self, text):
        from hew import Normalizer
        if not self.normalizer:
            self.normalizer = Normalizer()
        return self.normalizer.to_ascii(text)

    @classmethod
    def extractTaggerId(cls, track):
        ufid = ''
        for a0 in track.tag.unique_file_ids:
            if a0.owner_id == 'DJTagger':
                ufid = binascii.b2a_base64(a0.uniq_id).strip()
        return ufid

    @classmethod
    def extractFileIds(cls, track):
        # Python 2.6 does not like dictionary comprehensions
        ids = {}
        for x in track.tag.unique_file_ids:
            ids[x.owner_id] = binascii.b2a_base64(x.uniq_id).strip()
        return ids

    @classmethod
    def extractDate(cls, date):
        return str(date) if date else ''

    @classmethod
    def orderedAllColumns(cls):
        # preserve order
        columns = (Formatter.basic +
                   Formatter.songwriting +
                   Formatter.production +
                   Formatter.distribution +
                   Formatter.library +
                   Formatter.mp3Info)

        return columns


class Mp3Snapshot(object):
    def __init__(self, compact=True):
        self.compact = compact
        self.log = logging.getLogger(__name__)

    def createFromScan(self, scanPath, outFileName,
                       fieldSet=None, supressWarnings=True):
        formatter = Formatter(fieldSet)

        if supressWarnings:
            log = logging.getLogger('eyed3')
            log.setLevel(logging.ERROR)

        try:
            fout = _output(outFileName)
            fout.writelines('{')
            sep = ''

            for fullPath in walk(scanPath):
                self.log.info(
                    "Scanning %s", formatter.normalizeToAscii(fullPath)
                )
                row = self.extractTags(fullPath, formatter)
                if row:
                    fout.writelines([sep, '"',
                                     fullPath.replace('\\', '\\\\'),
                                     '":'])
                    json.dump(row, fout,
                              indent=None if self.compact else 2)
                    sep = ','

        finally:
            fout.writelines('}')
            fout.close()

    def extractTags(self, mp3FileName, formatter):
        track = self._loadID3(mp3FileName)
        if not track:
            return None
        a = self._extractTags(track, formatter)
        if 'fileHash' in formatter.fieldSet:
            a['fileHash'] = self._calculateHash(track, mp3FileName)
        return a

    def _extractTags(self, track, formatter):
        return formatter.format(track)

    def _loadID3(self, mp3FileName):
        import eyed3
        try:
            return eyed3.load(mp3FileName)
        except (IOError, ValueError):
            self.log.error("Cannot load ID3 '%s'", mp3FileName)
            return None

    def _calculateHash(self, track, mp3FileName):
        chunk_size = 1024
        offset = (track.tag.header.tag_size
                  if track.tag and track.tag.header
                  else 0)
        shaAccum = hashlib.sha1()
        try:
            with open(mp3FileName, "rb") as f:
                f.seek(offset)
                byte = f.read(chunk_size)
                while byte:
                    shaAccum.update(byte)
                    byte = f.read(chunk_size)
        except IOError:
            self.log.error("Cannot Hash '%s'", mp3FileName)
            return ''
        return binascii.b2a_base64(shaAccum.digest()).strip()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Scan directories and build a snapshot of the MP3s'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('path',  nargs='?', metavar='path',
                   default=os.getcwd(),
                   help='the path to scan')
    p.add_argument('outfile',  nargs='?', metavar='outfile',
                   default='mp3s.json',
                   help='the name of the file that will hold the results')
    p.add_argument('-b', '--basic', action='store_true', dest='basic',
                   help=' '.join(Formatter.basic))
    p.add_argument('-s', '--songwriting', action='store_true',
                   dest='songwriting', help=' '.join(Formatter.songwriting))
    p.add_argument('-p', '--production', action='store_true',
                   dest='production', help=' '.join(Formatter.production))
    p.add_argument('-d', '--distribution', action='store_true',
                   dest='distribution', help=' '.join(Formatter.distribution))
    p.add_argument('-l', '--library', action='store_true', dest='library',
                   help=' '.join(Formatter.library))
    p.add_argument('-m', '--mp3Info', action='store_true', dest='mp3Info',
                   help=' '.join(Formatter.mp3Info))
    p.add_argument('-a', '--all', action='store_true', dest='all',
                   help='include all supported fields')
    p.add_argument('--compact', action='store_true', dest='compact',
                   help='output the JSON in a compact format')

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
    if args.mp3Info:
        columns = columns + Formatter.mp3Info
    if args.all:
        columns = Formatter.columns

    if not columns:
        columns = Formatter.basic

    pipeline = Mp3Snapshot(args.compact)
    pipeline.log.setLevel(logging.INFO)
    pipeline.createFromScan(args.path, args.outfile, list(set(columns)))
