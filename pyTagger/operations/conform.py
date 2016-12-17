import re
import datetime
from pyTagger.operations.on_mp3 import updateOne
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import generateUfid, fmap


def _expel(phrases, x):
    if not x:
        return x

    if '(' not in x and '[' not in x:
        return x

    for phrase in phrases:
        if phrase in x:
            x = x.replace(phrase, '')

    return x


class LibraryStandard(object):
    def __init__(self):
        self.annotatedFields = {'title', 'album'}
        self.featuring = {'artist'}
        self.addTags = {'media', 'ufid', 'comments', 'group', 'subtitle'}

        self.reader = ID3Proxy(
            self.annotatedFields.union(self.featuring).union(self.addTags)
        )

        # https://regex101.com/
        self.regexFeature = re.compile(
            '(?i)(.*?)\W[\(\[](feat|featuring|with)\W+(.*)[\)\]]'
        )

        self.annotations = [
            'Album Version', 'Amazon MP3 Exclusive - Deluxe Version',
            'Amazon MP3 Exclusive Version', 'Deluxe Edition', 'Deluxe Version',
            'Deluxe', 'Explicit Content', 'Explicit Version', 'Explicit',
            'LP Version', 'Original Motion Picture Soundtrack', 'Remastered',
            'Special Edition', 'US Release', 'US Version', '+digital booklet'
        ]

        # Build up the expel table
        self.expel = [' (' + x + ')' for x in self.annotations]
        self.expel.extend([' [' + x + ']' for x in self.annotations])

    # -------------------------------------------------------------------------
    # Operations
    # -------------------------------------------------------------------------

    def assignID(self, tags):
        ufid = generateUfid()
        if 'ufid' in tags:
            tags['ufid'].update({'DJTagger': ufid})
        else:
            tags['ufid'] = {'DJTagger': ufid}
        return tags

    def clearComments(self, tags):
        tags['comments'] = [
            {'lang': 'eng', 'text': '', 'description': ''},
            {'lang': '', 'text': '', 'description': ''}
        ]
        return tags

    def clearMedia(self, tags):
        tags['media'] = ''
        return tags

    def clearRating(self, tags):
        tags['group'] = ''
        return tags

    def digitalMedia(self, tags):
        tags['media'] = 'DIG'
        return tags

    def extractArtist(self, tags):
        if 'title' not in tags or not tags['title']:
            return tags

        m = self.regexFeature.match(tags['title'])
        if m:
            tags['title'] = m.group(1)
            artists = [tags['artist']]
            artists.extend([x.strip() for x in m.group(3).split('&')])
            tags['artist'] = '/'.join(artists)
        return tags

    def removeAnnotations(self, tags):
        for k in self.annotatedFields:
            if k in tags:
                tags[k] = _expel(self.expel, tags[k])
        return tags

    def timestamp(self, tags):
        stamp = datetime.date.today()
        tags['subtitle'] = stamp.isoformat()
        return tags

    # -------------------------------------------------------------------------
    # Process
    # -------------------------------------------------------------------------

    def processFile(self, fullPath):
        tags = self.reader.extractTags(fullPath)

        pipeline = [
            self.extractArtist, self.removeAnnotations, self.timestamp,
            self.assignID, self.digitalMedia, self.clearComments,
            self.clearRating
        ]
        tags = fmap(pipeline, tags)

        updateOne(self.reader, fullPath, tags, True)
