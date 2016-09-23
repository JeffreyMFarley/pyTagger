from pyTagger.proxies.es import Client
from pyTagger.mp3_snapshot import Formatter


def _rowsFromBuckets(buckets):
    for bucket in buckets:
        key = bucket[u"key"]
        for dups in bucket[u"files"][u"buckets"]:
            yield (key, dups[u"key"])


def findDuplicates(client):
    r = client.search({
        'from': 0, 'size': 0,
        'aggs': {
            'duplicates': {
                'terms': {
                    'field': 'fileHash',
                    'min_doc_count': 2,
                    'size': 100
                },
                'aggs': {
                    'files': {
                        'terms': {
                            'field': 'path'
                        }
                    }
                }
            }
        }
    })

    buckets = r[u"aggregations"][u"duplicates"][u"buckets"]

    return _rowsFromBuckets(buckets)

if __name__ == "__main__":
    cli = Client()

    fmt = Formatter()
    print("hash,file")
    for hashValue, fileName in findDuplicates(cli):
        print("{0},{1}".format(hashValue, fmt.normalizeToAscii(fileName)))
