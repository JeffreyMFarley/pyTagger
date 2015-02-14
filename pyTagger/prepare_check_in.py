import os
import json
import sys
import argparse
import logging
import unicodedata
import datetime
import uuid
import binascii
if sys.version < '3':
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: open(fileName, 'w', encoding='utf-8')
import pyTagger

class prepare_check_in():
    """description of class"""

    def __init__(self):
        self.updater = pyTagger.UpdateFromSnapshot()
        self.updater.formatter = pyTagger.mp3_snapshot.Formatter({'media', 'ufid', 'comments', 'group', 'subtitle'})

    def _walk(self, path):
        for currentDir, subdirs, files in os.walk(unicode(path)):
            # Get the absolute path of the currentDir parameter
            currentDir = os.path.abspath(currentDir)

            # Traverse through all files
            for fileName in files:
                fullPath = os.path.join(currentDir, fileName)
                yield fullPath

    def run(self, path, supressWarnings=True):
        if supressWarnings:
            log = logging.getLogger('eyed3')
            log.setLevel(logging.ERROR)

        stamp = datetime.date.today()
        for fullPath in self._walk(unicode(path)):
            id = uuid.uuid4()
            asString = binascii.b2a_base64(id.bytes).strip()
            preparationTags = {
                'media' : 'DIG',
                'ufid' : {'DJTagger': asString},
                'comments' : [{'lang': 'eng', 'text': '', 'description': ''},
                              {'lang': '', 'text': '', 'description': ''}
                              ],
                'group' : '',
                'subtitle' : stamp.isoformat()
                }
            self.updater._updateOne(fullPath, preparationTags)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

# debugging
#sys.argv = [sys.argv[0], r'C:\Users\Jeff\Music\Amazon MP3']

def buildArgParser():
    description = 'Update basic fields in a directory'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('path', metavar='path', help='the directory to process')
    p.add_argument('--suppress', action='store_true', dest='supressWarnings',
                   help='supress eyed3 warnings')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    pipeline = prepare_check_in()
    pipeline.run(args.path, args.supressWarnings);
