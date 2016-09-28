import os
import logging
from elasticsearch import Elasticsearch, ConnectionError, RequestError
from pyTagger.io import loadJson, toAbsolute


class Client(object):
    def __init__(self, index='library', doc_type='track'):
        self.host = os.getenv('ES_HOST', '192.168.50.20')
        self.index = index
        self.doc_type = doc_type
        self.es = Elasticsearch([self.host])
        self.log = logging.getLogger(__name__)

        es_log = logging.getLogger('elasticsearch')
        es_log.setLevel(logging.ERROR)

    def _replaceDots(self, ids):
        result = {}
        for k, v in ids.items():
            if '.' in k:
                result[k.replace('.', '_')] = v
            else:
                result[k] = v
        return result

    def exists(self):
        return self.es.indices.exists(index=self.index)

    def create(self):
        absPath = toAbsolute('proxies/es-index-library.json')
        body = loadJson(absPath)
        result = self.es.indices.create(index=self.index, body=body)
        return result[u'acknowledged']

    def load(self, snapshot):
        if not snapshot or not isinstance(snapshot, dict):
            raise TypeError("'snapshot' must be dictionary")

        success, error = 0, 0

        try:
            if not self.exists() and not self.create():
                raise Exception('Cannot create index')

            for k, v in snapshot.items():
                v['path'] = k

                # Fix dots in field names
                if 'ufid' in v:
                    v['ufid'] = self._replaceDots(v['ufid'])

                try:
                    self.es.create(
                        index=self.index,
                        doc_type=self.doc_type,
                        body=v
                    )
                    success += 1
                    if (success + error) % 100 == 0:
                        self.log.info("%d records loaded", success + error)

                except RequestError as e:
                    self.log.warning("'%s' could not be loaded %s", k, e)
                    error += 1

        except ConnectionError:
            self.log.error('Cannot connect to Elasticsearch')
            raise

        return (success, error)

    def search(self, dsl):
        return self.es.search(
            index=self.index, doc_type=self.doc_type, body=dsl
        )

if __name__ == '__main__':
    snapshot = loadJson(toAbsolute('../mp3s.json'))

    cli = Client()
    cli.log.setLevel(logging.INFO)
    print(cli.load(snapshot))
