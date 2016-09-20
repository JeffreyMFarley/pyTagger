import json
import os
import sys
if sys.version < '3':
    import eyed3
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
from elasticsearch import Elasticsearch


def relativeToAbsolute(path):
    # where is this script?
    thisScriptDir = os.path.dirname(__file__)

    # get the expected paths
    return os.path.join(thisScriptDir, path)

if __name__ == '__main__':
    inFileName = relativeToAbsolute('../mp3s.json')
    with _input(inFileName) as f:
        snapshot = json.load(f)

    es = Elasticsearch()
    for k, v in snapshot.items():
        v['path'] = k
        try:
            r = es.create(
                index='library',
                doc_type='track',
                body=v
            )
        except Exception as e:
            print(k, e)
