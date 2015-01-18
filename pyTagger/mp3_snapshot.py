# -*- coding: utf-8 -*

from __future__ import print_function
import json
import os
import sys
import argparse
import binascii
import hashlib
if sys.version < '3':
    import eyed3
    from eyed3 import main, mp3, id3, core
    import codecs
    import unicodedata
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: open(fileName, 'w', encoding='utf-8')

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class Formatter():
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
    mp3Info = ['bitRate', 'vbr', 'fileHash']

    def __init__(self, fieldSet=columns):
        self.fieldSet = fieldSet
        self.translateTable = []

    def format(self, obj):
        if isinstance(obj, mp3.Mp3AudioFile) and obj.tag:
            # Python 2.6 does not like dictionary comprehensions
            row = {}
            for k in self.fieldSet:
                row[k] = self._projectionEyed3[k](obj)
            return row
        return {}

    def normalizeToAscii(self, text):
        if not self.translateTable:
            self.translateTable = self.buildTranslateTable()
        b = unicodedata.normalize('NFKD', text)
        return b.translate(self.translateTable).encode('ascii', 'replace')

    @classmethod
    def buildTranslateTable(cls):
        if sys.version >= '3':
            return dict.fromkeys(c for c in range(sys.maxunicode)
                                 if unicodedata.combining(chr(c)))
        else:
            return dict.fromkeys(c for c in range(sys.maxunicode)
                                 if unicodedata.combining(unichr(c)))

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
        return date.year if date else ''

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

class Mp3Snapshot:
    def __init__(self, compact=True):
        self.compact = compact

    def createFromScan(self, scanPath, outFileName,
                       fieldSet=Formatter.columns):
        formatter = Formatter(fieldSet)

        try:
            fout = _output(outFileName)
            fout.writelines('{')
            sep = ''

            # make sure the scan path is unicode and the results will be returned in unicode
            for currentDir, subdirs, files in os.walk(unicode(scanPath)):
                # Get the absolute path of the currentDir parameter
                currentDir = os.path.abspath(currentDir)

                # Traverse through all files
                for fileName in files:
                    fullPath = os.path.join(currentDir, fileName)

                    # Check if the file has an extension of typical music files
                    if fullPath[-3:].lower() in ['mp3']:
                        print("Processing", formatter.normalizeToAscii(fullPath))
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
        try:
            return eyed3.load(mp3FileName)
        except (IOError, ValueError):
            print('Error with ID3 Load', mp3FileName, file=sys.stderr)
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
            print('Cannot Hash', mp3FileName, file=sys.stderr)
            return ''
        return binascii.b2a_base64(shaAccum.digest()).strip()

    # -------------------------------------------------------------------------
    # I/O
    # -------------------------------------------------------------------------

    def load(self, fileName):
        with _input(fileName) as f:
            return json.load(f)

    def save(self, fileName, object):
        with _output(fileName) as f:
            return json.dump(object, f, indent=None if self.compact else 2)

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
    pipeline.createFromScan(args.path, args.outfile, list(set(columns)))
