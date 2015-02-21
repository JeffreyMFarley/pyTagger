import sys

__all__ = ['mp3_snapshot', 'snapshot_converter', 'path_segmentation', 'update_from_snapshot', 'console_progress_bar']

from pyTagger.mp3_snapshot import Mp3Snapshot
from pyTagger.path_segmentation import *
from pyTagger.snapshot_converter import *
from pyTagger.update_from_snapshot import *
from pyTagger.console_progress_bar import *

if sys.version > '3':
    __all__.append('iTunes')
    from pyTagger.iTunes import *
