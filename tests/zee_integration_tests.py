from __future__ import unicode_literals
import datetime
import json
import os
import shutil
import sys
import unittest
if sys.version < '3':
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: open(fileName, 'w', encoding='utf-8')
import pyTagger
from pyTagger.models import Snapshot
from pyTagger.utils import walk, generateUfid
from pyTagger.extract_images import ExtractImages
from tests import *

INTEGRATION_TEST_DIRECTORY = os.path.join(
    RESULT_DIRECTORY, 'integration-test'
)


def setUpModule():
    if sampleFilesExist and not os.path.exists(INTEGRATION_TEST_DIRECTORY):
        os.makedirs(INTEGRATION_TEST_DIRECTORY)

    for fullPath in walk(SOURCE_DIRECTORY, True):
        shutil.copy(fullPath, INTEGRATION_TEST_DIRECTORY)


def tearDownModule():
    if os.path.exists(INTEGRATION_TEST_DIRECTORY):
        shutil.rmtree(INTEGRATION_TEST_DIRECTORY)


class TestIntegration(unittest.TestCase):
    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    # @unittest.skip('Check coverage')
    def setUp(self):
        pass

    def test_01_update(self):
        from pyTagger.operations.on_mp3 import updateFromSnapshot
        from pyTagger.proxies.id3 import ID3Proxy

        # Setup fixture
        snapshot = {}
        stamp = datetime.date.today()
        ufid = generateUfid()
        for fullPath in walk(INTEGRATION_TEST_DIRECTORY):
            snapshot[fullPath] = {
                'media': 'DIG',
                'ufid': {'DJTagger': ufid},
                'comments': [
                    {'lang': 'eng', 'text': '', 'description': d}
                    for d in ['', 'iTunes_CDDB_IDs', 'iTunNORM',
                              'iTunPGAP', 'iTunSMPB', 'ID3v1.x Comment']
                ],
                'group': '',
                'subtitle': stamp.isoformat()
            }
            snapshot[fullPath]['comments'].append({
                'lang': '', 'text': '', 'description': ''
            })

        # Execute
        id3Proxy = ID3Proxy()
        updateFromSnapshot(id3Proxy, snapshot, True)

        # Validate
        for fullPath in walk(INTEGRATION_TEST_DIRECTORY):
            actual = id3Proxy.extractTags(fullPath)
            if not actual:
                continue

            expected = snapshot[fullPath]
            for k, v in actual.items():
                if k in expected:
                    if k == 'group':
                        self.assertIsNone(actual[k])
                    elif k == 'comments' and 'Everything Counts' in fullPath:
                        pass  # The Everything Counts MP3 has illegal comments
                    elif k == 'comments':
                        self.assertEqual(actual[k], [])
                    elif k == 'ufid':
                        self.assertEqual(actual[k]['DJTagger'], ufid)
                    else:
                        self.assertEqual(actual[k], expected[k])

    def test_02_scan(self):
        from pyTagger.operations.on_directory import buildSnapshot
        from pyTagger.proxies.id3 import ID3Proxy

        reader = ID3Proxy()
        outFile = os.path.join(RESULT_DIRECTORY, 'snapshot.json')

        buildSnapshot(INTEGRATION_TEST_DIRECTORY, outFile, reader)
        assert os.path.getsize(outFile) > 0

    def test_03_convert(self):
        from pyTagger.operations.to_csv import writeCsv
        from pyTagger.utils import loadJson

        inFile = os.path.join(RESULT_DIRECTORY, 'snapshot.json')
        outFile = os.path.join(RESULT_DIRECTORY, 'snapshot.txt')

        snapshot = loadJson(inFile)
        writeCsv(snapshot, outFile)
        assert os.path.getsize(outFile) > 0

    def test_04_convertBack(self):
        from pyTagger.operations.from_csv import convert
        from pyTagger.utils import loadJson

        inFile = os.path.join(RESULT_DIRECTORY, 'snapshot.txt')
        outFile = os.path.join(RESULT_DIRECTORY, 'snapshot2.json')

        convert(inFile, outFile)

        original = os.path.join(RESULT_DIRECTORY, 'snapshot.json')
        a = loadJson(original)
        b = loadJson(outFile)

        self.maxDiff = None
        for path, tags in b.items():
            a_tags = a[path]
            for tag, value in tags.items():
                if tag == 'lyrics':
                    # TODO - why does '\n' inside lyrics get converted to '\r'
                    # TODO - From Sasha has empty lyrics that get stripped
                    pass
                elif not value:
                    self.assertTrue(tag not in a_tags or not a_tags[tag],
                                    'FAIL: {0} found in {1} or {2}'.format(
                                        tag, repr(path), repr(a_tags[tag])
                                        if tag in a_tags else ''
                                    ))
                elif tag == 'comments' and 'Everything Counts' in path:
                    pass  # The Everything Counts MP3 has illegal comment tags
                else:
                    self.assertEqual(value, a_tags[tag])

    def test_05_extractAll(self):
        targetDir = os.path.join(RESULT_DIRECTORY, 'images')
        target = ExtractImages(targetDir)

        # Clear directory
        for name in os.listdir(targetDir):
            os.remove(os.path.join(targetDir, name))

        target.extractAll(INTEGRATION_TEST_DIRECTORY)

        files = [name for name in os.listdir(targetDir)]
        self.assertEqual(27, len(files))

    def test_06_rename(self):
        targetDir = os.path.join(RESULT_DIRECTORY, 'renamed', '')
        if os.path.exists(targetDir):
            shutil.rmtree(targetDir)

        target = pyTagger.Rename(targetDir)

        # Clone over files
        cloneDir = os.path.join(RESULT_DIRECTORY, 'checked_in', '')
        if os.path.exists(cloneDir):
            shutil.rmtree(cloneDir)

        os.makedirs(cloneDir)
        for f in walk(os.path.join(SOURCE_DIRECTORY, 'Checkin'), True):
            shutil.copy(f, cloneDir)

        prepare = pyTagger.PrepareCheckIn()
        prepare.run(cloneDir)
        target.run(cloneDir)

        files = [name for name in os.listdir(targetDir)]
        self.assertEqual(7, len(files))

        expected = os.path.join(targetDir, 'Beck', 'Dreams', '01 Dreams.mp3')
        self.assertTrue(os.path.exists(expected))

    def test_00_extractFromList(self):
        fileName = os.path.join(RESULT_DIRECTORY, 'extract_list.txt')
        with _output(fileName) as f:
            f.writelines([os.path.join(
                INTEGRATION_TEST_DIRECTORY, '01 Oh No.mp3'
            ), '\n'])
            f.writelines([os.path.join(
                INTEGRATION_TEST_DIRECTORY, '08 - Aeroplane.mp3'
            ), '\n'])

        targetDir = os.path.join(RESULT_DIRECTORY, 'some_images')
        target = ExtractImages(targetDir)
        target.extractFrom(fileName)

        files = [name for name in os.listdir(targetDir)]
        assert len(files) == 2

if __name__ == '__main__':
    unittest.main(failfast=True, exit=False)
