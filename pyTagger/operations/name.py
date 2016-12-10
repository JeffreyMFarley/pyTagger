from __future__ import unicode_literals

winFileReserved = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '.']
winFileTable = {ord(c): '_' for c in winFileReserved}

# -----------------------------------------------------------------------------
# Helpers


def _safeGet(tags, field, default=None):
    return tags[field] if field in tags else default


def _albumArtistTitle(tags):
    album = _safeGet(tags, 'album')
    if not album:
        raise ValueError('Album Name must be provided')

    if _safeGet(tags, 'compilation'):
        artist = 'Compilations'
    else:
        artist = _safeGet(tags, 'albumArtist') or _safeGet(tags, 'artist')
        if not artist:
            raise ValueError('Artist must be provided')

    title = _safeGet(tags, 'title')
    if not title:
        raise ValueError('Title must be provided')

    return album, artist, title


def _removeBadFileNameChars(s):
    return s.translate(winFileTable).strip('_ ')


def _limit(s, maxChars):
    return s[:maxChars].strip()

# -----------------------------------------------------------------------------
# Public Methods


def buildPath(tags, ext='mp3'):
    pipeline = lambda x, n: _limit(_removeBadFileNameChars(x), n)

    album, artist, title = _albumArtistTitle(tags)

    jointedPath = [pipeline(artist, 40), pipeline(album, 40)]

    totalDisc = _safeGet(tags, 'totalDisc', 1)
    if totalDisc > 1:
        fileName = '{0:02d}-'.format(_safeGet(tags, 'disc', 0))
    else:
        fileName = ''

    fileName += '{0:02d} {1}'.format(_safeGet(tags, 'track', 0),
                                     pipeline(title, 99))
    fileName = '{0}.{1}'.format(_limit(fileName, 36), ext)

    jointedPath.append(fileName)
    return jointedPath


def imageFileName(tags, mime_type):
    album, artist, title = _albumArtistTitle(tags)
    fileTitle = '{0} - {1} - {2}'.format(artist, album, title)

    return _removeBadFileNameChars(fileTitle) + '.' + mime_type
