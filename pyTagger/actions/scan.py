import datetime
import eyed3
import os
import platform
from configargparse import getArgumentParser
from pyTagger.models import Snapshot
from pyTagger.operations.on_directory import buildSnapshot
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import defaultConfigFiles

# -----------------------------------------------------------------------------
# Configuration

MIN_DATE = datetime.datetime(1970, 1, 1).isoformat()
MAX_DATE = datetime.datetime(2200, 1, 1).isoformat()

p = getArgumentParser('scan',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser('snapshot')],
                      description='create a snapshot from directories of MP3s')
group = p.add_argument_group('Files')
group.add('path',  nargs='?', default=os.getcwd(),
          help='the path to scan')
group.add('outfile',  nargs='?', default='mp3s.json',
          help='the name of the file that will hold the results')
group.add('--compact', action='store_true', dest='compact',
          help='output the JSON in a compact format')
group = p.add_argument_group('Filters')
group.add('--created-min', default=MIN_DATE,
          help='only include files that have been created since')
group.add('--created-max', default=MAX_DATE,
          help='only include files that have been created before')
group.add('--modified-min', default=MIN_DATE,
          help='only include files that have been modified since')
group.add('--modified-max', default=MAX_DATE,
          help='only include files that have been modified before')


# -----------------------------------------------------------------------------

# https://en.wikipedia.org/wiki/Robustness_principle
def postel_date(s):
    d0 = eyed3.core.Date.parse(s)
    d1 = datetime.datetime(
        d0.year,
        d0.month or 1,
        d0.day or 1,
        d0.hour or 0,
        d0.minute or 0,
        d0.second or 0
    )
    return d1


def creationDate(path):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/questions/237079/
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def buildFilter(args):
    minModTime = postel_date(args.modified_min)
    maxModTime = postel_date(args.modified_max)
    minCreateTime = postel_date(args.created_min)
    maxCreateTime = postel_date(args.created_max)

    def innerFilter(path):
        if path[-3:].lower() not in ['mp3']:
            return False

        stats = os.stat(path)
        modTime = datetime.datetime.fromtimestamp(stats.st_mtime)
        createTime = datetime.datetime.fromtimestamp(creationDate(path))

        createOk = minCreateTime <= createTime <= maxCreateTime
        modOk = minModTime <= modTime <= maxModTime
        if createOk and modOk:
            print(path)
            return True

        return False
    return innerFilter


def process(args):
    filterFn = None
    if (
        args.modified_min != MIN_DATE or args.modified_max != MAX_DATE or
        args.created_min != MIN_DATE or args.created_max != MAX_DATE
    ):
        filterFn = buildFilter(args)

    columns = Snapshot.columnsFromArgs(args)
    id3Proxy = ID3Proxy(columns)
    s, f = buildSnapshot(
        args.path, args.outfile, id3Proxy, args.compact, filterFn
    )
    return 'Extracted tags from {0} files\nFailed {1}'.format(s, f)
