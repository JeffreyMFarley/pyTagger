# -*- coding: utf-8 -*

from __future__ import print_function
import os
import sys
import argparse
import logging
import binascii
import hashlib
if sys.version < '3':
    import eyed3
    from eyed3 import main, mp3, id3, core
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
from pyTagger.mp3_snapshot import Formatter

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class ExtractImages():
    def __init__(self, outputDir):
        self.outputDir = outputDir if outputDir else os.getcwd()
        self.captured = {}
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

    def _hash(self, image):
        shaAccum = hashlib.sha1()
        shaAccum.update(image.image_data)
        return binascii.b2a_base64(shaAccum.digest()).strip()

    def _writeImage(self, track, image):
        extension = image.mime_type.split("/")[1]
        fileName = u'{0} - {1}.{2}'.format(track.tag.album, 
                                           track.tag.title, 
                                           extension)
        fullPath = os.path.join(self.outputDir, fileName)

        with open(fullPath, mode="wb") as f:
            f.write(image.image_data)

        return fullPath

    def _extract(self, mp3FileName):
        track = None
        try:
            track = eyed3.load(mp3FileName)
        except (IOError, ValueError):
            print('Error with ID3 Load', mp3FileName, file=sys.stderr)
            return

        if not track.tag or not track.tag.images:
            return

        for image in track.tag.images:
            k = self._hash(image)
            if k not in self.captured:
                v = self._writeImage(track, image)
                self.captured[k] = v

    def extractAll(self, directory):
        formatter = Formatter([])
        log = logging.getLogger('eyed3')
        log.setLevel(logging.ERROR)

        for currentDir, subdirs, files in os.walk(unicode(directory)):
            # Get the absolute path of the currentDir parameter
            currentDir = os.path.abspath(currentDir)

            # Traverse through all files
            for fileName in files:
                fullPath = os.path.join(currentDir, fileName)

                # Check if the file has an extension of typical music files
                if fullPath[-3:].lower() in ['mp3']:
                    print("Extracting", formatter.normalizeToAscii(fullPath))
                    self._extract(fullPath)

    def extractFrom(self, fileList):
        formatter = Formatter([])
        log = logging.getLogger('eyed3')
        log.setLevel(logging.ERROR)

        if not os.path.exists(fileList):
            print(fileList, 'does not exist.  Exiting.')
            return

        with _input(fileList) as f:
            for l in f:
                fullPath = l.strip()

                # Check if the file has an extension of typical music files
                if fullPath[-3:].lower() in ['mp3']:
                    print("Extracting", formatter.normalizeToAscii(fullPath))
                    self._extract(fullPath)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Extract image from MP3 files'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('path',  nargs='?', metavar='path',
                   default=os.getcwd(),
                   help='the path to scan')
    p.add_argument('outputDir',  nargs='?', metavar='outputDir',
                   default=os.path.join(os.getcwd(), 'images'),
                   help='the directory where the extracted images are stored')
    p.add_argument('-f', '--use-file', dest='useFile',
                   metavar='filename',
                   help='a text file with the list of files to extract')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    pipeline = ExtractImages(args.outputDir)
    if args.useFile:
        pipeline.extractFrom(args.useFile)
    else:
        pipeline.extractAll(args.path)
