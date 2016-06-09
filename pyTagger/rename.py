
from __future__ import print_function
import os
import sys
import argparse
import itertools
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
from pyTagger.mp3_snapshot import Formatter, Mp3Snapshot

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class Rename():
    def __init__(self, destDir):
        self.destDir = destDir if destDir else os.getcwd()
        if not os.path.exists(self.destDir):
            os.makedirs(self.destDir)

    def _buildFormatter(self):
        fields = list(itertools.chain(Formatter.basic, Formatter.distribution))
        fields.append('compilation')
        return Formatter(fields)

    def buildPath(self, tags, extension=None):
        return [None, None, None]

    def run(self, directory):
        log = logging.getLogger('eyed3')
        log.setLevel(logging.ERROR)

        reader = Mp3Snapshot()
        formatter = self._buildFormatter()

        for currentDir, subdirs, files in os.walk(unicode(directory)):
            # Get the absolute path of the currentDir parameter
            currentDir = os.path.abspath(currentDir)

            # Traverse through all files
            for fileName in files:
                fullPath = os.path.join(currentDir, fileName)

                # Check if the file has an extension of typical music files
                if fullPath[-3:].lower() in ['mp3']:
                    print("Extracting", formatter.normalizeToAscii(fullPath))
                    tags = reader.extractTags(fullPath, formatter)
                    relativePath = self.buildPath(tags, fullPath[-3:])

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Rename MP3 files'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('sourceDir',  nargs='?', metavar='sourceDir',
                   default=os.getcwd(),
                   help='the path to scan')
    p.add_argument('destDir',  nargs='?', metavar='destDir',
                   default=None,
                   help='the directory where the files will be moved to')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    pipeline = Rename(args.destDir)
    pipeline.run(args.sourceDir)
