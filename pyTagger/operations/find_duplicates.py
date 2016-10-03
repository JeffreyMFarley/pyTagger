from __future__ import print_function
from pyTagger.io import loadJson, toAbsolute
from pyTagger.proxies.es import Client

# -----------------------------------------------------------------------------
# Clones = Exact Duplicates


def _flattenAggregation(response):
    buckets = response[u"aggregations"][u"primary"][u"buckets"]

    for bucket in buckets:
        key = bucket[u"key"]
        for secondary in bucket[u"secondary"][u"buckets"]:
            yield (key, secondary[u"key"])


def findClones(client):
    r = client.search({
        'from': 0, 'size': 0,
        'aggs': {
            'primary': {
                'terms': {
                    'field': 'fileHash',
                    'min_doc_count': 2,
                    'size': 100
                },
                'aggs': {
                    'secondary': {
                        'terms': {
                            'field': 'path'
                        }
                    }
                }
            }
        }
    })

    return _flattenAggregation(r)

# -----------------------------------------------------------------------------
# Isonom = Name based matches


def _isonomQuery(track):
        # "_source": [
        #     "title", "track", "artist", "albumArtist", "album",
        #     "length", "subtitle", "genre", "path", "disc", "totalDisc"
        # ],

    terms = []

    if 'track' in track and track['track']:
        terms.append({"term": {"track": track['track']}})

    for k in ['album', 'artist', 'title']:
        if k in track and track[k]:
            terms.append({
                "match": {k: {"query": track[k], "operator": "and"}}
            })

    if len(terms) == 0:
        raise ValueError("track does not contain any searchable fields")

    query = {
        "from": 0, "size": 10,
        "sort": [
            "_score",
            "album.raw"
        ],
        "query": {
            "bool": {
                "should": terms
            }
        },
        "min_score": 4
    }

    return query


def _projectIsonomResults(response):
    hits = response[u"hits"][u"hits"]
    for hit in hits:
        yield (hit[u"_score"], hit[u"_source"])


def findIsonomTracks(client, track):
    query = _isonomQuery(track)
    response = client.search(query)
    for score, isonom in _projectIsonomResults(response):
        yield (track, score, isonom)

# -----------------------------------------------------------------------------


if __name__ == "__main__":
    from hew import Normalizer
    import sys
    import json

    snapshot = loadJson(toAbsolute('../mp3s-cfpb.json'))

    cli = Client()
    nml = Normalizer()

    print("file,score,isonom")
    for k, v in snapshot.items():
        matches, near = 0, 0
        try:
            for _, score, isonom in findIsonomTracks(cli, v):
                if score > 10:
                    print("{0},{1},{2}".format(
                        nml.to_ascii(k), score, nml.to_ascii(isonom['path']))
                    )
                    matches += 1
                else:
                    near += 1
        except Exception as e:
            print("Error on", nml.to_ascii(k), e,
                  json.dumps(v, indent=2, sort_keys=True),
                  file=sys.stderr, sep='\n', end='\n\n')
        if matches != 1:
            print("Match Error", nml.to_ascii(k), matches, near,
                  file=sys.stderr)
