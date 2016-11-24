# -*- coding: utf-8 -*

import os
import sys
import argparse
import logging
if sys.version < '3':  # pragma: no cover
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
else:  # pragma: no cover
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
from hew import Normalizer
from pyTagger.operations.hash import hashBuffer
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import walk

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class ExtractImages(object):
    def __init__(self, outputDir):
        self.log = logging.getLogger(__name__)
        self.outputDir = outputDir if outputDir else os.getcwd()
        self.captured = {}
        self.id3Proxy = ID3Proxy()
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

    def _writeImage(self, track, image_data, mime_type):
        fileName = u'{0} - {1}.{2}'.format(track.tag.album,
                                           track.tag.title,
                                           mime_type)
        fullPath = os.path.join(self.outputDir, fileName)

        with open(fullPath, mode="wb") as f:
            f.write(image_data)

        return fullPath

    def _extract(self, id3Proxy, mp3FileName):
        track = id3Proxy.loadID3(mp3FileName)
        for image_data, mime_type in id3Proxy.extractImages(track):
            k = hashBuffer(image_data)
            if k not in self.captured:
                v = self._writeImage(track, image_data, mime_type)
                self.captured[k] = v

    def extractAll(self, directory):
        normalizer = Normalizer()
        log = logging.getLogger('eyed3')
        log.setLevel(logging.ERROR)
        for fullPath in walk(directory):
            asciified = normalizer.to_ascii(fullPath)
            self.log.info("Extracting '%s'", asciified)
            self._extract(self.id3Proxy, fullPath)

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
                    self._extract(self.id3Proxy, fullPath)

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
