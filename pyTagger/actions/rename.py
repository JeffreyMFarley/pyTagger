from __future__ import unicode_literals
# import os
import argparse
# import itertools
# import logging
# from pyTagger.models import Snapshot
# from pyTagger.operations.on_directory import renameFiles
# from pyTagger.proxies.id3 import ID3Proxy

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


# class Rename(object):
#     def __init__(self, destDir):
#         self.destDir = destDir if destDir else os.getcwd()

#     def _buildReader(self):
#         fields = list(itertools.chain(Snapshot.basic, Snapshot.distribution))
#         fields.append('compilation')
#         return ID3Proxy(fields)

#     # -----------------------------------------------------------------------
#     # Main Methods
#     # -----------------------------------------------------------------------

#     def run(self, directory):
#         reader = self._buildReader()
#         _ = renameFiles(directory, self.destDir, reader)

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

# if __name__ == '__main__':
#     parser = buildArgParser()
#     args = parser.parse_args()

#     pipeline = Rename(args.destDir)
#     pipeline.log.setLevel(logging.INFO)
#     pipeline.run(args.sourceDir)
