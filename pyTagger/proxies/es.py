import os
import logging
from elasticsearch import Elasticsearch, ConnectionError, RequestError
from pyTagger.io import loadJson, toAbsolute


class Client(object):
    def __init__(self, index='library', doc_type='track'):
        self.host = os.getenv('ES_HOST', 'localhost')
        self.index = index
        self.doc_type = doc_type
        self.es = Elasticsearch([self.host])
        self.log = logging.getLogger(__name__)

        es_log = logging.getLogger('elasticsearch')
        es_log.setLevel(logging.ERROR)

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

        try:
            if not self.exists() and not self.create():
                raise Exception('Cannot create index')

            for k, v in snapshot.items():
                v['path'] = k
                try:
                    r = self.es.create(
                        index=self.index,
                        doc_type=self.doc_type,
                        body=v
                    )
                except RequestError as e:
                    self.log.warning(
                        "'{0}' could not be loaded {1}".format(k, e)
                    )

        except ConnectionError:
            self.log.error('Cannot connect to Elasticsearch')
            raise

if __name__ == '__main__':
    snapshot = loadJson(toAbsolute('../mp3s.json'))

    cli = Client()
    cli.load(snapshot)
