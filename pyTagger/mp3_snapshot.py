# -*- coding: utf-8 -*

from __future__ import print_function
import json
import os
import sys
if sys.version < '3':
    import eyed3
    from eyed3 import main, mp3, id3, core
    import codecs
import binascii
import hashlib

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class Formatter():
    projectionEyed3 = {
        'id': lambda x: Formatter.extractTaggerId(x),
        'track': lambda x: x.tag.track_num[0], 
        'totalTrack': lambda x: x.tag.track_num[1],
        'title': lambda x: x.tag.title,
        'album': lambda x: x.tag.album, 
        'artist': lambda x: x.tag.artist,
        'albumArtist': lambda x: x.tag.album_artist, 
        'genre': lambda x: x.tag.genre.name if x.tag.genre else '', 
        'group': lambda x: x.tag.getTextFrame('TIT1'),
        'subtitle': lambda x: x.tag.getTextFrame('TIT3'),
        'disc': lambda x: x.tag.disc_num[0],
        'totalDisc': lambda x: x.tag.disc_num[1],
        'publisher': lambda x: x.tag.publisher,
        'bpm': lambda x: x.tag.bpm,
        'key': lambda x: x.tag.getTextFrame('TKEY'),
        'playCount': lambda x: x.tag.play_count,
        'ufid': lambda x: {y.owner_id: binascii.b2a_base64(y.uniq_id).strip() for y in x.tag.unique_file_ids},
        'comments': lambda x: [{'lang':y.lang, 'text':y.text, 'description': y.description} for y in x.tag.comments],
        'bitRate': lambda x: x.info.bit_rate[1] if x.info != None else None, 
        'vbr': lambda x: x.info.bit_rate[0] if x.info != None else None,
        'fileHash': lambda x: ''
    }
    columns = list(projectionEyed3.keys())

    def __init__(self, fieldSet=columns):
        self.fieldSet = fieldSet

    def format(self, obj):
         if isinstance(obj, mp3.Mp3AudioFile) and obj.tag:
             return { k: self.projectionEyed3[k](obj) for k in self.fieldSet } 
         # Let the base class default method raise the TypeError
         return {}

    @classmethod
    def extractTaggerId(cls, track):
        ufid = ''
        for a0 in track.tag.unique_file_ids:
            if a0.owner_id == 'DJTagger' :
                ufid = binascii.b2a_base64(a0.uniq_id).strip()
        return ufid

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
                        print("Processing", self.currentPath)
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


# debugging
#sys.argv = [sys.argv[0], r'C:\dvp\MP3Tools\SampleData', r'..\data\snapshot.json']

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    path = os.getcwd()
    outFileName = 'mp3s.json'
    
    argc = len(sys.argv)
    if argc > 2:
        outFileName = sys.argv[2]
    if argc > 1:
        path = sys.argv[1]

    pipeline = Mp3Snapshot()
    pipeline.createFromScan(path, outFileName)
