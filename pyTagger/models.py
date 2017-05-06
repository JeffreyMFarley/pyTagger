from configargparse import getArgumentParser
from collections import namedtuple
from pyTagger.utils import defaultConfigFiles


def makeEnum(name, *sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type(name, (), enums)


COMPARISON = makeEnum(
    'Comparison', 'EQUAL', 'NOT', 'GT', 'GTE', 'LT', 'LTE', 'LIKE'
)


FilterCondition = namedtuple('FilterCondition', [
    'field', 'comparison', 'value'
])


TrackMatch = namedtuple('TrackMatch', [
    'status', 'newPath', 'oldPath', 'score', 'newTags', 'oldTags'
])


#------ Snapshot --------------------------------------------------------------

class Snapshot(object):
    basic = ['title', 'track', 'totalTrack', 'artist',
             'albumArtist', 'album', 'length']
    songwriting = ['bpm', 'composer', 'key', 'lyrics', 'language']
    production = ['year', 'releaseDate', 'originalReleaseDate',
                  'recordingDate', 'conductor', 'remixer', 'publisher']
    distribution = ['barcode', 'media', 'disc', 'totalDisc']
    library = ['genre', 'id', 'ufid', 'compilation', 'comments', 'playCount',
               'group', 'subtitle', 'encodingDate', 'taggingDate']
    mp3Info = ['bitRate', 'vbr', 'fileHash', 'version']

    dltTags = ['comments', 'lyrics']
    complexTags = ['comments', 'lyrics', 'ufid']

    integerTags = [
        'track', 'totalTrack', 'length',
        'disc', 'totalDisc',
        'compilation', 'playCount',
        'bitRate'
    ]

    @staticmethod
    def orderedAllColumns():
        # preserve order
        columns = (Snapshot.basic +
                   Snapshot.songwriting +
                   Snapshot.production +
                   Snapshot.distribution +
                   Snapshot.library +
                   Snapshot.mp3Info)

        return columns

    @staticmethod
    def columnsFromSnapshot(data):
        header = set()

        for v in data.values():
            for j in v.keys():
                if j not in header:
                    header.add(j)

        # Build the ordered set with the extra columns at the end
        known = Snapshot.orderedAllColumns()
        unknown = header - set(known)

        columns = [c for c in known if c in header]
        for c in sorted(unknown):
            columns.append(c)

        return columns

    @staticmethod
    def columnsFromArgs(args):
        columns = []
        if args.basic:
            columns = columns + Snapshot.basic
        if args.songwriting:
            columns = columns + Snapshot.songwriting
        if args.production:
            columns = columns + Snapshot.production
        if args.distribution:
            columns = columns + Snapshot.distribution
        if args.library:
            columns = columns + Snapshot.library
        if args.mp3Info:
            columns = columns + Snapshot.mp3Info
        if args.all:
            columns = Snapshot.orderedAllColumns()

        if not columns:
            columns = Snapshot.basic

        return columns


p = getArgumentParser('snapshot',
                      default_config_files=defaultConfigFiles,
                      parents=[getArgumentParser()],
                      description='control which columns are included in the'
                      'snapshot')
group = p.add_argument_group('Columns')
group.add_argument('--basic', action='store_true', dest='basic',
                   help=' '.join(Snapshot.basic))
group.add_argument('--songwriting', action='store_true',
                   dest='songwriting', help=' '.join(Snapshot.songwriting))
group.add_argument('--production', action='store_true',
                   dest='production', help=' '.join(Snapshot.production))
group.add_argument('--distribution', action='store_true',
                   dest='distribution', help=' '.join(Snapshot.distribution))
group.add_argument('--library', action='store_true', dest='library',
                   help=' '.join(Snapshot.library))
group.add_argument('--mp3Info', action='store_true', dest='mp3Info',
                   help=' '.join(Snapshot.mp3Info))
group.add_argument('--all', action='store_true', dest='all',
                   help='include all supported fields')
