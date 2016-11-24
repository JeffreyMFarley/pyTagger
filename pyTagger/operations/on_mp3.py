from __future__ import unicode_literals
import logging
import os
from pyTagger.operations.hash import hashBuffer
from pyTagger.operations.name import imageFileName
from pyTagger.operations.two_tags import difference


def _writeImage(outputDir, tags, image_data, mime_type):
    fileName = imageFileName(tags, mime_type)
    fullPath = os.path.join(outputDir, fileName)

    with open(fullPath, mode="wb") as f:
        f.write(image_data)

    return fullPath


def extractImages(id3Proxy, hashTable, outputDir, fileName):
    track = id3Proxy.loadID3(fileName)
    for image_data, mime_type in id3Proxy.extractImages(track):
        k = hashBuffer(image_data)
        if k not in hashTable:
            tags = id3Proxy.extractTagsFromTrack(track)
            try:
                v = _writeImage(outputDir, tags, image_data, mime_type)
                hashTable[k] = v
            except ValueError as ve:
                log = logging.getLogger(__name__)
                s = 'Extract Images failed on {0} - {1}'
                log.error(s.format(fileName, ve))


def updateOne(id3Proxy, fileName, updates, upgrade=False):
    track = id3Proxy.loadID3(fileName)
    if not track or not track.tag:
        return

    asIs = id3Proxy.extractTagsFromTrack(track)
    delta = difference(updates, asIs)

    id3Proxy.saveID3(track, delta, upgrade)


def updateFromSnapshot(id3Proxy, snapshot, upgrade=False):
    for k, v in snapshot.items():
        updateOne(id3Proxy, k, v, upgrade)