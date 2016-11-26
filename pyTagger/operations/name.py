from __future__ import unicode_literals

BAD_WIN_FILE_CHARS = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '.']


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


def imageFileName(tags, mime_type):
    album, artist, title = _albumArtistTitle(tags)
    fileTitle = '{0} - {1} - {2}'.format(artist, album, title)

    r = {ord(c): '_' for c in BAD_WIN_FILE_CHARS}
    return fileTitle.translate(r).strip('_') + '.' + mime_type
