from __future__ import unicode_literals
import datetime
import os
import shutil
import sys
import unittest
if sys.version < '3':
    import codecs
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf-8')
else:
    _output = lambda fileName: open(fileName, 'w', encoding='utf-8')
import pyTagger
from pyTagger.utils import walk, generateUfid
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
        u, f = updateFromSnapshot(id3Proxy, snapshot, True)

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
        self.assertEqual(u, 53)
        self.assertEqual(f, 2)

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

    def test_05_extractImages(self):
        from pyTagger.operations.on_directory import extractImages
        from pyTagger.proxies.id3 import ID3Proxy

        targetDir = os.path.join(RESULT_DIRECTORY, 'images')
        for name in os.listdir(targetDir):
            os.remove(os.path.join(targetDir, name))

        processed = extractImages(
            INTEGRATION_TEST_DIRECTORY, targetDir, ID3Proxy()
        )

        files = [name for name in os.listdir(targetDir)]
        self.assertEqual(26, len(files))
        self.assertEqual(processed['extracted'], 26)
        self.assertEqual(processed['skipped'], 7)
        self.assertEqual(processed['errors'], 1)

    def test_06_checkin(self):
        from pyTagger.operations.on_directory import renameFiles
        from pyTagger.operations.on_directory import prepareForLibrary
        from pyTagger.proxies.id3 import ID3Proxy

        targetDir = os.path.join(RESULT_DIRECTORY, 'renamed', '')
        if os.path.exists(targetDir):
            shutil.rmtree(targetDir)

        # Clone over files
        cloneDir = os.path.join(RESULT_DIRECTORY, 'checked_in', '')
        if os.path.exists(cloneDir):
            shutil.rmtree(cloneDir)

        os.makedirs(cloneDir)
        for f in walk(os.path.join(SOURCE_DIRECTORY, 'Checkin'), True):
            shutil.copy(f, cloneDir)

        processed = prepareForLibrary(cloneDir)
        self.assertEqual(processed, 7)

        c = renameFiles(cloneDir, targetDir, ID3Proxy())
        self.assertEqual(c['moved'], 7)
        self.assertEqual(c['skipped'], 0)
        self.assertEqual(c['errors'], 0)
        self.assertEqual(c['collisions'], 0)

        expected = os.path.join(targetDir, 'Beck', 'Dreams', '01 Dreams.mp3')
        self.assertTrue(os.path.exists(expected))

    def test_00_extractFromList(self):
        from pyTagger.operations.on_directory import extractImagesFrom
        from pyTagger.proxies.id3 import ID3Proxy

        fileName = os.path.join(RESULT_DIRECTORY, 'extract_list.txt')
        with _output(fileName) as f:
            f.writelines([os.path.join(
                INTEGRATION_TEST_DIRECTORY, '01 Oh No.mp3'
            ), '\n'])
            f.writelines([os.path.join(
                INTEGRATION_TEST_DIRECTORY, '08 - Aeroplane.mp3'
            ), '\n'])

        targetDir = os.path.join(RESULT_DIRECTORY, 'some_images')
        if os.path.exists(targetDir):
            shutil.rmtree(targetDir)

        processed = extractImagesFrom(fileName, targetDir, ID3Proxy())

        files = [name for name in os.listdir(targetDir)]
        self.assertEqual(len(files), 2)
        self.assertEqual(processed['extracted'], 2)
        self.assertEqual(processed['skipped'], 0)
        self.assertEqual(processed['errors'], 0)

if __name__ == '__main__':
    unittest.main(failfast=True, exit=False)
