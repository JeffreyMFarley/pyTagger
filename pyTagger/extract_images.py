# -*- coding: utf-8 -*

import os
import sys
import argparse
import logging
import binascii
import hashlib
if sys.version < '3':  # pragma: no cover
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
else:  # pragma: no cover
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
from hew import Normalizer
from pyTagger.utils import walk

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class ExtractImages(object):
    def __init__(self, outputDir):
        self.log = logging.getLogger(__name__)
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
        import eyed3
        track = None
        try:
            track = eyed3.load(mp3FileName)
        except (IOError, ValueError):
            self.log.error("Cannot load MP3 '%s'", mp3FileName)
            return

        if not track.tag or not track.tag.images:
            return

        for image in track.tag.images:
            k = self._hash(image)
            if k not in self.captured:
                v = self._writeImage(track, image)
                self.captured[k] = v

    def extractAll(self, directory):
        normalizer = Normalizer()
        log = logging.getLogger('eyed3')
        log.setLevel(logging.ERROR)
        for fullPath in walk(directory):
            asciified = normalizer.to_ascii(fullPath)
            self.log.info("Extracting '%s'", asciified)
            self._extract(fullPath)

    def extractFrom(self, fileList):
        normalizer = Normalizer()
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
                    asciified = normalizer.to_ascii(fullPath)
                    self.log.info("Extracting '%s'", asciified)
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
    pipeline.log.setLevel(logging.INFO)
    if args.useFile:
        pipeline.extractFrom(args.useFile)
    else:
        pipeline.extractAll(args.path)
