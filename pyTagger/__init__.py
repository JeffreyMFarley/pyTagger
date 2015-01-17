import sys

__all__ = ['mp3_snapshot', 'snapshot_converter', 'path_segmentation']

from pyTagger.mp3_snapshot import Mp3Snapshot
from pyTagger.path_segmentation import *
from pyTagger.snapshot_converter import *

if sys.version > '3':
    __all__.append('iTunes')
    from pyTagger.iTunes import *
