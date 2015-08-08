import re
import os
import sys
import argparse
import logging
import datetime
import uuid
import unicodedata
import binascii

if sys.version < '3':
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: open(fileName, 'w', encoding='utf-8')
from pyTagger import UpdateFromSnapshot, Mp3Snapshot
from pyTagger.mp3_snapshot import Formatter

def curryStrip(phrase):
    def strip(x):
        if phrase in x:
            return x.replace(phrase, '')
        return x
    return strip

class PrepareCheckIn():
    """description of class"""

    def __init__(self):
        self.stripFields = {'title', 'album'}
        self.featuring = {'artist'}
        self.addTags = {'media', 'ufid', 'comments', 'group', 'subtitle'}

        self.reader = Mp3Snapshot()
        self.readerFormatter = Formatter(self.stripFields
                                         .union(self.featuring))

        self.updater = UpdateFromSnapshot()
        self.updater.formatter = Formatter(self.stripFields
                                           .union(self.featuring)
                                           .union(self.addTags))
        self.updater.upgrade = True

        self.regexBracket = re.compile('^(.*)(\[.*\])+(.*)$')
        self.regexFeature = re.compile('\((feat|feat\.|featuring|with) (.*)\)')

        self.textMonoids = [
                            self.stripBracketedText, 
                            curryStrip(' (Explicit Version)'),
                            curryStrip(' (Explicit)'),
                            curryStrip(' (Explicit Content)'),
                            curryStrip(' (US Version)'),
                            curryStrip(' (US Release)'),
                            curryStrip(' (Album Version)'),
                            curryStrip(' (LP Version)'),
                            curryStrip(' (Deluxe)'),
                            curryStrip(' (Deluxe Edition)'),
                            curryStrip(' (Deluxe Version)'),
                            curryStrip(' (Amazon MP3 Exclusive Version)'),
                            curryStrip(' (Amazon MP3 Exclusive - Deluxe Version)'),
                            curryStrip(' (Original Motion Picture Soundtrack)'),
                            curryStrip(' (Special Edition)')
                            ]

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def stripBracketedText(self, s):
        if '[' in s:
            while '[' in s:
                m = self.regexBracket.match(s)
                if not m:  # no closing bracket, strip to end
                    openBracket = s.index('[')
                    s = s[:openBracket]
                else:
                    s = m.group(1).strip() + m.group(3).strip()
        return s

    def prepareText(self, s):
        for fn in self.textMonoids:
            s = fn(s)
        return s

    def extractArtist(self, s):
        m = self.regexFeature.match(s)
        if m:
            replace = ' ({0} {1})'.replace(m.group(1), m.group(2))
            s = s.replace(replace, '')
            return s, m.group(2)
        else:
            return s, None
        
    def getTags(self, fullPath):
        return self.reader.extractTags(fullPath, self.readerFormatter)

    # -------------------------------------------------------------------------
    # Process
    # -------------------------------------------------------------------------

    def _walk(self, path):
        for currentDir, subdirs, files in os.walk(unicode(path)):
            # Get the absolute path of the currentDir parameter
            currentDir = os.path.abspath(currentDir)

            # Traverse through all files
            for fileName in files:
                fullPath = os.path.join(currentDir, fileName)
                yield fullPath

    def _process(self, fullPath):
        tags = self.getTags(fullPath)
        for k in self.stripFields:
            tags[k] = self.prepareText(tags[k])

        stamp = datetime.date.today()
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
        tags.update(preparationTags)
        self.updater._updateOne(fullPath, tags)

    def run(self, path, supressWarnings=True):
        if supressWarnings:
            log = logging.getLogger('eyed3')
            log.setLevel(logging.ERROR)

        for fullPath in self._walk(unicode(path)):
            if fullPath[-3:].lower() in ['mp3']:
                self._process(fullPath)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

# debugging
#sys.argv = [sys.argv[0], r'C:\Users\Jeff\Music\Amazon MP3']

def buildArgParser():
    description = 'Update basic fields in a directory'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('path',  nargs='?', metavar='path',
                   default=os.getcwd(),
                   help='the directory to process')
    p.add_argument('--suppress', action='store_true', dest='supressWarnings',
                   help='supress eyed3 warnings')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    pipeline = PrepareCheckIn()
    pipeline.run(args.path, args.supressWarnings);



 