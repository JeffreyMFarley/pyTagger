from __future__ import unicode_literals
import logging
import os
from collections import Counter
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
    c = Counter()

    track = id3Proxy.loadID3(fileName)
    for image_data, mime_type in id3Proxy.extractImages(track):
        k = hashBuffer(image_data)
        if k not in hashTable:
            tags = id3Proxy.extractTagsFromTrack(track)
            try:
                v = _writeImage(outputDir, tags, image_data, mime_type)
                hashTable[k] = v
                c['extracted'] += 1
            except ValueError as ve:
                log = logging.getLogger(__name__)
                s = 'Extract Images failed on %s - %s'
                log.error(s, fileName, ve)
                c['errors'] += 1
        else:
            c['skipped'] += 1
    return c


def updateOne(id3Proxy, fileName, updates, upgrade=False):
    track = id3Proxy.loadID3(fileName)
    if not track or not track.tag:
        return 0

    asIs = id3Proxy.extractTagsFromTrack(track)
    delta = difference(updates, asIs)

    id3Proxy.saveID3(track, delta, upgrade)
    return 1


def updateFromSnapshot(id3Proxy, snapshot, upgrade=False):
    updated, failed = 0, 0

    for k, v in sorted(snapshot.items()):
        if updateOne(id3Proxy, k, v, upgrade):
            updated += 1
        else:
            failed += 1

    return updated, failed
