# -*- coding: utf-8 -*

from __future__ import print_function
import json
import os
import sys
if sys.version < '3':
    import eyed3
    from eyed3 import main, mp3, id3, core
    import codecs
import argparse
import binascii
import hashlib

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class Formatter():
    projectionEyed3 = {
        'album': lambda x: x.tag.album, 
        'albumArtist': lambda x: x.tag.album_artist, 
        'artist': lambda x: x.tag.artist,
        'bitRate': lambda x: x.info.bit_rate[1] if x.info != None else None, 
        'bpm': lambda x: x.tag.bpm,
        'comments': lambda x: [{'lang':y.lang, 'text':y.text, 'description': y.description} for y in x.tag.comments],
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
        'length' : lambda x: x.info.time_secs if x.info else '',
        'lyrics': lambda x: [{'lang':y.lang, 'text':y.text, 'description': y.description} for y in x.tag.lyrics],
        'media': lambda x: x.tag.getTextFrame('TMED'),
        'originalReleaseDate': lambda x: Formatter.extractDate(x.tag.original_release_date),
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
        'vbr': lambda x: x.info.bit_rate[0] if x.info != None else None,
        'year': lambda x: Formatter.extractDate(x.tag.getBestDate()),
    }
    columns = list(projectionEyed3.keys())

    basic = ['title', 'track', 'totalTrack', 'artist', 'albumArtist', 'album', 'length']
    songwriting = ['bpm', 'composer', 'key', 'lyrics', 'language']
    production = ['year', 'releaseDate', 'originalReleaseDate', 'recordingDate', 'conductor', 'remixer']
    distribution = ['media', 'disc', 'totalDisc']
    library = ['genre', 'id', 'ufid', 'compilation', 'comments', 'playCount', 'group', 'subtitle', 'taggingDate']
    mp3Info = ['bitRate', 'vbr', 'fileHash']

    def __init__(self, fieldSet=columns):
        self.fieldSet = fieldSet

    def format(self, obj):
        if isinstance(obj, mp3.Mp3AudioFile) and obj.tag:
            row = {}
            for k in self.fieldSet: 
                row[k] = self.projectionEyed3[k](obj)  # Python 2.7 Mac does not like dictionary comprehensions
            return row;
        return {}

    @classmethod
    def extractTaggerId(cls, track):
        ufid = ''
        for a0 in track.tag.unique_file_ids:
            if a0.owner_id == 'DJTagger' :
                ufid = binascii.b2a_base64(a0.uniq_id).strip()
        return ufid

    @classmethod
    def extractFileIds(cls, track):
        ids = {}
        for x in track.tag.unique_file_ids:
            ids[x.owner_id] = binascii.b2a_base64(x.uniq_id).strip()  # Python 2.7 Mac does not like dictionary comprehensions
        return ids

    @classmethod
    def extractDate(cls, date):
        return date.year if date else ''

class Mp3Snapshot:
    def __init__(self):
        self.currentPath = ''

    def createFromScan(self, scanPath, outFileName, fieldSet=Formatter.columns):
        formatter = Formatter(fieldSet)

        try:
            fout = codecs.open(outFileName, 'w', encoding='utf-8')
            fout.writelines('{')
            sep = ''

            for currentDir, subdirs, files in os.walk(scanPath):
                # Get the absolute path of the currentDir parameter
                currentDir = os.path.abspath(currentDir)
     
                # Traverse through all files
                for fileName in files:
                    self.currentPath = os.path.join(currentDir, fileName)
                    self.currentPath = self.currentPath.decode(sys.getfilesystemencoding())

                    # Check if the file has an extension of typical music files
                    if self.currentPath[-3:].lower() in ['mp3']:
                        try:
                            print("Processing", self.currentPath)
                        except UnicodeEncodeError:
                            print("Processing", self.currentPath.encode('ascii', errors='replace'))

                        if self.loadID3():
                            a = formatter.format(self.track)
                            if 'fileHash' in fieldSet:
                                a['fileHash'] = self.calculateHash()
                            fout.writelines([sep,'"',self.currentPath.replace('\\', '\\\\'),'":'])
                            json.dump(a, fout, indent=2)
                            sep = ','
                
        finally:
            fout.writelines('}')
            fout.close()

    def loadID3(self):
        try:
            self.track = eyed3.load(self.currentPath)
            return True
        except (IOError, ValueError):
            print('Error with ID3 Load', self.currentPath, file=sys.stderr)
            return False
        
    def calculateHash(self):
        chunk_size = 1024
        offset = self.track.tag.header.tag_size if self.track.tag and self.track.tag.header else 0
        shaAccum = hashlib.sha1()
        try:
            with open(self.currentPath, "rb") as f:
                f.seek(offset)
                byte = f.read(chunk_size)
                while byte:
                    shaAccum.update(byte)
                    byte = f.read(chunk_size)
        except IOError:
            print('Cannot Hash', self.currentPath, file=sys.stderr)
            return ''
        return binascii.b2a_base64(shaAccum.digest()).strip();

    #-------------------------------------------------------------------------------
    # I/O
    #-------------------------------------------------------------------------------

    def load(self, fileName):
        with codecs.open(fileName, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, fileName, object):
        with codecs.open(fileName, 'w', encoding='utf-8') as f:
            return json.dump(object, f, indent=2)

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def buildArgParser():
    p = argparse.ArgumentParser(description='Scan directories and build a snapshot of the MP3s')
    p.add_argument('path',  nargs='?', metavar='path',
                   default=os.getcwd(),
                   help='the path to scan')
    p.add_argument('outfile',  nargs='?', metavar='outfile',
                   default='mp3s.json',
                   help='the name of the file that will hold the results')
    p.add_argument('-b', '--basic', action='store_true', dest='basic',
                   help=' '.join(Formatter.basic))
    p.add_argument('-s', '--songwriting', action='store_true', dest='songwriting',
                   help=' '.join(Formatter.songwriting))
    p.add_argument('-p', '--production', action='store_true', dest='production',
                   help=' '.join(Formatter.production))
    p.add_argument('-d', '--distribution', action='store_true', dest='distribution',
                   help=' '.join(Formatter.distribution))
    p.add_argument('-l', '--library', action='store_true', dest='library',
                   help=' '.join(Formatter.library))
    p.add_argument('-m', '--mp3Info', action='store_true', dest='mp3Info',
                   help=' '.join(Formatter.mp3Info))
    p.add_argument('-a', '--all', action='store_true', dest='all',
                   help='include all supported fields')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    columns = []
    if args.basic:  columns = columns + Formatter.basic
    if args.songwriting:  columns = columns + Formatter.songwriting
    if args.production:  columns = columns + Formatter.production
    if args.distribution:  columns = columns + Formatter.distribution
    if args.library:  columns = columns + Formatter.library
    if args.mp3Info:  columns = columns + Formatter.mp3Info
    if args.all: columns = Formatter.columns

    if not columns:
        columns = Formatter.basic

    pipeline = Mp3Snapshot()
    pipeline.createFromScan(args.path, args.outfile, list(set(columns)))
