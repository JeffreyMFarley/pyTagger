from __future__ import print_function
import os
import sys
import time
import json
import requests
from operator import itemgetter


def relativeToAbsolute(path):
    # where is this script?
    thisScriptDir = os.path.dirname(__file__)

    # get the expected paths
    return os.path.join(thisScriptDir, path)


def pickleForTesting(r, params, baseFile):
    import pickle

    fileName = relativeToAbsolute('{0}-{1}.p'.format(baseFile,
                                                     params['start']))
    with open(fileName, 'wb') as f:
        pickle.dump(r, f)

# -----------------------------------------------------------------------------


def apiKeys():
    '''
    Generator for the list of keys in the .env file
    '''
    envFileName = relativeToAbsolute('../.env')
    if not os.path.exists(envFileName):
        raise ValueError("ENV file '%s' not found." % envFileName)

    # get the keys
    with open(envFileName, 'r') as f:
        for line in f:
            k, v = line.strip().split('=', 1)
            if k[0] != '#':
                yield (k, v)


def getApiKey(name):
    '''
    Gets the one (and only!) api key with `name`
    '''
    keys = [v for k, v in apiKeys() if k == name]
    assert len(keys) > 0
    assert len(keys) == 1
    return keys[0]

# -------------------------------------------------------------------------
# Projections
# -------------------------------------------------------------------------


def musicBrainz(field):
    def curried(song):
        if field in song:
            for o in song[field]:
                if o['catalog'] == 'musicbrainz':
                    return o['foreign_id'].split(':')[-1]
    return curried


def audioSummary(field):
    def curried(song):
        if 'audio_summary' in song:
            o = song['audio_summary']
            if field in o:
                return o[field]
    return curried

_songProjection = {
    'artist': lambda x: x['artist_name'],
    'bpm': audioSummary('tempo'),
    'id_musicbrainz_artist': musicBrainz('artist_foreign_ids'),
    'id_musicbrainz_song': musicBrainz('tracks'),
    'id_echonest_artist': lambda x: x['artist_id'],
    'id_echonest_song': lambda x: x['id'],
    'key': audioSummary('key'),
    'length': audioSummary('duration'),
    'title': lambda x: x['title'],
    'acousticness': audioSummary('acousticness'),
    'danceability': audioSummary('danceability'),
    'energy': audioSummary('energy'),
    'instrumentalness': audioSummary('instrumentalness'),
    'liveness': audioSummary('liveness'),
    'loudness': audioSummary('loudness'),
    'speechiness': audioSummary('speechiness'),
    'valence': audioSummary('valence')
}


def projection(song):
    return {k: _songProjection[k](song) for k in sorted(_songProjection)}

# -----------------------------------------------------------------------------
# Class
# -----------------------------------------------------------------------------


class EchoNestProxy(object):
    """
    Encapsulates calling the EchoNest Web Service
    """
    def __init__(self):
        from hew import Normalizer

        self.api_key = getApiKey('ECHONEST_API_KEY')
        self.maxCallsPerMinute = 200
        self.step = 100
        self.status_code = 0
        self.normalizer = Normalizer()
        self.requestHook = None

    # -------------------------------------------------------------------------

    def _chunk(self, url, params):
        ''' Retrieves a full set of data from an API
        '''
        if not self.api_key:
            raise StopIteration

        # The URL parameters
        params.update({'api_key': self.api_key,
                       'results': self.step,
                       'start': 0,
                       'bucket': ['audio_summary', 'tracks', 'id:musicbrainz']
                       })

        while True:
            print('Calling', url, params['artist'], params['start'])
            r = requests.get(url, params=params)

            if self.requestHook:
                self.requestHook(r, params)

            self.status_code = r.status_code
            if r.status_code != 200:
                raise StopIteration

            data = json.loads(r.text)

            if not data or 'response' not in data:
                print('Unable to load records', r.status_code, file=sys.stderr)
                if 'error' in data:
                    print(data['error'], file=sys.stderr)
                raise StopIteration

            if 'songs' in data['response']:
                songs = data['response']['songs']
                yield songs
            else:
                print(data, file=sys.stderr)
                raise StopIteration

            if len(songs) == 100:
                params['start'] = params['start'] + self.step

            if len(songs) < 100:
                raise StopIteration

            time.sleep(60/self.maxCallsPerMinute)

    # -------------------------------------------------------------------------

    def getByArtist(self, artist):
        url = 'http://developer.echonest.com/api/v4/song/search'
        cleaned = self.normalizer.for_query_string(artist)
        params = {'artist': cleaned}

        for chunk in self._chunk(url, params):
            for song in chunk:
                yield projection(song)

    def getByArtistAndTitle(self, artist, title):
        url = 'http://developer.echonest.com/api/v4/song/search'
        artist0 = self.normalizer.for_query_string(artist)
        title0 = self.normalizer.for_query_string(title)
        params = {'artist': artist0, 'title': title0}

        for chunk in self._chunk(url, params):
            for song in chunk:
                yield projection(song)

if __name__ == '__main__':
    service = EchoNestProxy()
    #service.requestHook = partial(pickleForTesting,
    #                              baseFile='../tests/echonest-chunks')
    #l = list(service.getByArtist(u'Meat Beat Manifesto'))

    songs = sorted(service.getByArtist(u'The Future Sound of London'),
                   key=itemgetter('artist', 'title', 'length'))

    columns = sorted(_songProjection.keys())
    print('\t'.join(columns))
    for song in songs:
        cells = [unicode(song[col]) if col in song else '' for col in columns]
        print(service.normalizer.to_ascii(u'\t'.join(cells)))

    #for song in songs:
    #    s = json.dumps(song, ensure_ascii=True, sort_keys=True)
    #    print(s)
