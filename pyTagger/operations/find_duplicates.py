from __future__ import unicode_literals
from pyTagger.models import TrackMatch

# -----------------------------------------------------------------------------
# Clones = Exact Duplicates


def _flattenAggregation(response):
    buckets = response['aggregations']['primary']['buckets']

    for bucket in buckets:
        key = bucket['key']
        for secondary in bucket['secondary']['buckets']:
            yield (key, secondary['key'])


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


def _isonomQuery(track, minScore):
    query = {
        'from': 0, 'size': 6,
        'sort': '_score',
        'query': {'bool': {}},
        'min_score': minScore
    }

    if 'id' in track and track['id']:
        query['query']['bool']['must_not'] = {'term': {'id': track['id']}}

    terms = []

    if 'track' in track and track['track']:
        terms.append({'term': {'track': track['track']}})

    for k in ['album', 'artist', 'title']:
        if k in track and track[k]:
            terms.append({
                'match': {k: {'query': track[k], 'operator': 'and'}}
            })
            terms.append({
                'match': {k: {'query': track[k]}}
            })

    if len(terms) == 0:
        raise ValueError('track does not contain any searchable fields')

    query['query']['bool']['should'] = terms
    return query


def _projectIsonomResults(response):
    hits = response['hits']['hits']
    for hit in hits:
        yield (hit['_score'], hit['_source'])


def findIsonomTracks(client, track, minScore):
    client.log.info('=' * 50)
    client.log.info('\t'.join([track['title'], track['album']]))
    query = _isonomQuery(track, minScore)
    response = client.search(query)
    for score, isonom in _projectIsonomResults(response):
        path = isonom['path']
        del isonom['path']
        client.log.info('\t'.join([
             str(score), isonom['title'], isonom['album'], path
        ]))
        yield (path, score, isonom)


def findIsonoms(client, snapshot, minScore):
    for k in sorted(snapshot):
        v = snapshot[k]

        try:
            matches = list(findIsonomTracks(client, v, minScore))
            quality = [x for x in matches if x[1] >= 12]

            if len(quality) == 1:
                path, score, tags = quality[0]
                yield TrackMatch('single', k, path, score, v, tags)
            elif len(matches) == 1:
                path, score, tags = matches[0]
                yield TrackMatch('single', k, path, score, v, tags)
            elif len(matches) > 1:
                for path, score, tags in matches:
                    yield TrackMatch('multiple', k, path, score, v, tags)
            else:
                yield TrackMatch('nothing', k, None, 0.0, v, None)
        except ValueError:
            yield TrackMatch('insufficient', k, None, 0.0, v, None)
