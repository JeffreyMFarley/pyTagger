from __future__ import unicode_literals
from pyTagger.operations.two_tags import difference


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
